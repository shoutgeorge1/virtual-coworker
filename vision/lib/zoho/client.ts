/**
 * Server-only Zoho CRM V8 client.
 * Token refresh + in-memory cache; retry once on 401; bounded timeouts.
 * Never log tokens / PII. zoho_synced requires a CRM record id.
 */

import { parseZohoCrmConfig, type ZohoCrmConfig } from "./config";
import { mapLeadToCrmPayload, type LeadRecord, type VerifiedFieldSet } from "./payload";
import { leadLogSafe, redactText, redactUnknown } from "./redact";

export type ZohoCrmResult = {
  ok: boolean;
  zoho_synced: boolean;
  recordId?: string;
  detail: string;
  duration_ms: number;
};

export class ZohoCrmError extends Error {
  readonly code: string;
  readonly status?: number;

  constructor(code: string, message: string, status?: number) {
    super(redactText(message));
    this.name = "ZohoCrmError";
    this.code = code;
    this.status = status;
  }
}

type TokenCache = {
  accessToken: string;
  expiresAtMs: number;
};

const globalCache = new Map<string, TokenCache>();

function cacheKey(cfg: ZohoCrmConfig): string {
  return `${cfg.accountsUrl}|${cfg.clientId}|${cfg.refreshToken.slice(0, 8)}`;
}

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs: number,
  fetchImpl: typeof fetch = fetch,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetchImpl(url, { ...init, signal: controller.signal });
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new ZohoCrmError("timeout", `Zoho request timed out after ${timeoutMs}ms`);
    }
    throw new ZohoCrmError("network", redactUnknown(err));
  } finally {
    clearTimeout(timer);
  }
}

export async function refreshAccessToken(
  cfg: ZohoCrmConfig,
  fetchImpl: typeof fetch = fetch,
): Promise<string> {
  const key = cacheKey(cfg);
  const cached = globalCache.get(key);
  const now = Date.now();
  if (cached && cached.expiresAtMs > now + 30_000) {
    return cached.accessToken;
  }

  const body = new URLSearchParams({
    refresh_token: cfg.refreshToken,
    client_id: cfg.clientId,
    client_secret: cfg.clientSecret,
    grant_type: "refresh_token",
  });

  const url = `${cfg.accountsUrl.replace(/\/$/, "")}/oauth/v2/token`;
  const res = await fetchWithTimeout(
    url,
    { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body },
    cfg.timeoutMs,
    fetchImpl,
  );

  const text = await res.text().catch(() => "");
  if (!res.ok) {
    throw new ZohoCrmError(
      "token_refresh_failed",
      `HTTP ${res.status} ${redactText(text.slice(0, 200))}`,
      res.status,
    );
  }

  let json: { access_token?: string; expires_in?: number };
  try {
    json = JSON.parse(text) as { access_token?: string; expires_in?: number };
  } catch {
    throw new ZohoCrmError("token_parse_failed", "Invalid token JSON");
  }

  if (!json.access_token) {
    throw new ZohoCrmError("token_missing", "No access_token in refresh response");
  }

  const expiresIn = Number(json.expires_in) || 3600;
  globalCache.set(key, {
    accessToken: json.access_token,
    expiresAtMs: now + expiresIn * 1000,
  });

  return json.access_token;
}

/** Test helper — clear in-memory token cache. */
export function clearZohoTokenCache(): void {
  globalCache.clear();
}

function extractRecordId(payload: unknown): string | undefined {
  if (!payload || typeof payload !== "object") return undefined;
  const data = (payload as { data?: unknown }).data;
  if (!Array.isArray(data) || !data[0] || typeof data[0] !== "object") return undefined;
  const row = data[0] as { details?: { id?: string }; id?: string; code?: string; status?: string };
  const id = row.details?.id || row.id;
  if (typeof id === "string" && id.trim()) return id.trim();
  return undefined;
}

async function upsertOnce(
  cfg: ZohoCrmConfig,
  accessToken: string,
  record: Record<string, unknown>,
  duplicateCheckFields: string[],
  fetchImpl: typeof fetch,
): Promise<{ status: number; body: unknown; recordId?: string }> {
  const base = cfg.apiDomain.replace(/\/$/, "");
  const url = `${base}/crm/v8/${encodeURIComponent(cfg.module)}/upsert`;
  const body = {
    data: [record],
    duplicate_check_fields: duplicateCheckFields.length
      ? duplicateCheckFields
      : [cfg.submissionIdField],
  };

  const res = await fetchWithTimeout(
    url,
    {
      method: "POST",
      headers: {
        Authorization: `Zoho-oauthtoken ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    },
    cfg.timeoutMs,
    fetchImpl,
  );

  const text = await res.text().catch(() => "");
  let parsed: unknown = text;
  try {
    parsed = text ? JSON.parse(text) : {};
  } catch {
    parsed = { raw: text.slice(0, 200) };
  }

  return {
    status: res.status,
    body: parsed,
    recordId: extractRecordId(parsed),
  };
}

/**
 * Upsert employer lead to Zoho CRM V8.
 * Success for zoho_synced requires a CRM record id in the response.
 */
export async function upsertEmployerLead(
  lead: LeadRecord,
  opts: {
    env?: NodeJS.ProcessEnv;
    verified?: VerifiedFieldSet | null;
    fetchImpl?: typeof fetch;
  } = {},
): Promise<ZohoCrmResult> {
  const started = Date.now();
  const env = opts.env || process.env;
  const cfg = parseZohoCrmConfig(env);

  if (!cfg.enabled) {
    return {
      ok: false,
      zoho_synced: false,
      detail: "zoho_crm_disabled",
      duration_ms: Date.now() - started,
    };
  }

  const fetchImpl = opts.fetchImpl || fetch;

  try {
    const mapped = mapLeadToCrmPayload(lead, cfg, opts.verified ?? null);
    let token = await refreshAccessToken(cfg, fetchImpl);
    let result = await upsertOnce(
      cfg,
      token,
      mapped.data,
      mapped.duplicateCheckFields,
      fetchImpl,
    );

    // Retry once on expiry / unauthorized
    if (result.status === 401) {
      clearZohoTokenCache();
      token = await refreshAccessToken(cfg, fetchImpl);
      result = await upsertOnce(
        cfg,
        token,
        mapped.data,
        mapped.duplicateCheckFields,
        fetchImpl,
      );
    }

    const duration_ms = Date.now() - started;
    const recordId = result.recordId;
    const synced = Boolean(recordId) && result.status >= 200 && result.status < 300;

    console.info(
      "[zoho-crm]",
      JSON.stringify(
        leadLogSafe({
          submission_id: lead.submission_id,
          market: lead.market,
          channel: "zoho_crm",
          ok: synced,
          error: synced ? undefined : `HTTP ${result.status}`,
          duration_ms,
        }),
      ),
    );

    if (!synced) {
      return {
        ok: false,
        zoho_synced: false,
        detail: redactText(`upsert_failed HTTP ${result.status}`),
        duration_ms,
      };
    }

    return {
      ok: true,
      zoho_synced: true,
      recordId,
      detail: "ok",
      duration_ms,
    };
  } catch (err) {
    const duration_ms = Date.now() - started;
    const detail = err instanceof ZohoCrmError ? err.message : redactUnknown(err);
    console.info(
      "[zoho-crm]",
      JSON.stringify(
        leadLogSafe({
          submission_id: lead.submission_id,
          market: lead.market,
          channel: "zoho_crm",
          ok: false,
          error: detail,
          duration_ms,
        }),
      ),
    );
    return {
      ok: false,
      zoho_synced: false,
      detail,
      duration_ms,
    };
  }
}
