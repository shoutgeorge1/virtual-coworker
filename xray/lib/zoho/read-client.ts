/**
 * Zoho CRM read-only client — refresh-token OAuth + COQL pagination.
 * Mirrors vision/lib/zoho refresh flow and ads-launch probe patterns.
 * Never create/update/delete.
 */

import { withRetry } from "@/lib/sync/retry";
import { redactText, redactUnknown } from "@/lib/sync/redact";
import { normalizeGclid, resolveJoin } from "@/lib/sync/join";
import type { Market, ZohoInquiryDayRow } from "@/lib/sync/types";

export type ZohoReadConfig = {
  clientId: string;
  clientSecret: string;
  refreshToken: string;
  accountsUrl: string;
  apiDomain: string;
  module: string;
  gclidField: string;
  timeoutMs: number;
};

export function parseZohoReadConfig(env: NodeJS.ProcessEnv = process.env): ZohoReadConfig | null {
  const clientId = (env.ZOHO_CRM_CLIENT_ID || "").trim();
  const clientSecret = (env.ZOHO_CRM_CLIENT_SECRET || "").trim();
  const refreshToken = (env.ZOHO_CRM_REFRESH_TOKEN || "").trim();
  if (!clientId || !clientSecret || !refreshToken) return null;
  return {
    clientId,
    clientSecret,
    refreshToken,
    accountsUrl: (env.ZOHO_CRM_ACCOUNTS_URL || "https://accounts.zoho.com").trim(),
    apiDomain: (env.ZOHO_CRM_API_DOMAIN || "https://www.zohoapis.com").trim(),
    module: (env.ZOHO_CRM_MODULE || "Leads").trim(),
    gclidField: (env.ZOHO_CRM_FIELD_GCLID || "utm_gclid").trim(),
    timeoutMs: Number(env.ZOHO_CRM_TIMEOUT_MS || 15000) || 15000,
  };
}

type TokenCache = { accessToken: string; expiresAtMs: number };
const globalCache = new Map<string, TokenCache>();

export function clearZohoReadTokenCache(): void {
  globalCache.clear();
}

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs: number,
  fetchImpl: typeof fetch,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetchImpl(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

export async function refreshZohoAccessToken(
  cfg: ZohoReadConfig,
  fetchImpl: typeof fetch = fetch,
): Promise<string> {
  const key = `${cfg.accountsUrl}|${cfg.clientId}|${cfg.refreshToken.slice(0, 8)}`;
  const cached = globalCache.get(key);
  const now = Date.now();
  if (cached && cached.expiresAtMs > now + 30_000) return cached.accessToken;

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
  const text = await res.text();
  if (!res.ok) {
    throw new Error(`Zoho token refresh HTTP ${res.status}: ${redactText(text.slice(0, 180))}`);
  }
  const json = JSON.parse(text) as { access_token?: string; expires_in?: number };
  if (!json.access_token) throw new Error("Zoho token refresh missing access_token");
  globalCache.set(key, {
    accessToken: json.access_token,
    expiresAtMs: now + (Number(json.expires_in) || 3600) * 1000,
  });
  return json.access_token;
}

type ZohoRecord = Record<string, unknown>;

async function coqlPage(
  cfg: ZohoReadConfig,
  selectQuery: string,
  fetchImpl: typeof fetch,
): Promise<ZohoRecord[]> {
  return withRetry(async () => {
    let token = await refreshZohoAccessToken(cfg, fetchImpl);
    const url = `${cfg.apiDomain.replace(/\/$/, "")}/crm/v8/coql`;
    const run = async (access: string) =>
      fetchWithTimeout(
        url,
        {
          method: "POST",
          headers: {
            Authorization: `Zoho-oauthtoken ${access}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ select_query: selectQuery }),
        },
        cfg.timeoutMs,
        fetchImpl,
      );

    let res = await run(token);
    if (res.status === 401) {
      clearZohoReadTokenCache();
      token = await refreshZohoAccessToken(cfg, fetchImpl);
      res = await run(token);
    }
    const text = await res.text();
    if (!res.ok) {
      throw new Error(`Zoho COQL HTTP ${res.status}: ${redactText(text.slice(0, 240))}`);
    }
    const json = JSON.parse(text) as { data?: ZohoRecord[] };
    return json.data || [];
  });
}

/**
 * Paginate COQL in 200-row pages (Zoho limit) over Created_Time window.
 * Dates are calendar days; window uses UTC midnights.
 */
export async function fetchZohoInquiries(
  cfg: ZohoReadConfig,
  start: string,
  end: string,
  opts: { fetchImpl?: typeof fetch; pageSize?: number } = {},
): Promise<ZohoRecord[]> {
  const fetchImpl = opts.fetchImpl || fetch;
  const pageSize = opts.pageSize ?? 200;
  const startIso = `${start}T00:00:00+00:00`;
  // end day inclusive → next midnight exclusive
  const endDate = new Date(`${end}T00:00:00.000Z`);
  endDate.setUTCDate(endDate.getUTCDate() + 1);
  const endIso = endDate.toISOString().replace(/\.\d{3}Z$/, "+00:00");

  const fields = [
    "id",
    "Created_Time",
    "Lead_Status",
    "Lead_Source",
    "Region",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    cfg.gclidField,
    "Referring_URL",
    "Campaign_Name",
  ].join(", ");

  const all: ZohoRecord[] = [];
  let offset = 0;
  for (;;) {
    const q =
      `SELECT ${fields} FROM ${cfg.module} ` +
      `WHERE Created_Time >= '${startIso}' AND Created_Time < '${endIso}' ` +
      `LIMIT ${pageSize} OFFSET ${offset}`;
    const page = await coqlPage(cfg, q, fetchImpl);
    all.push(...page);
    if (page.length < pageSize) break;
    offset += pageSize;
    if (offset > 50_000) break; // hard safety cap
  }
  return all;
}

function str(v: unknown): string {
  return v == null ? "" : String(v).trim();
}

function marketFromRegion(region: string): Market | "UNKNOWN" {
  const r = region.toUpperCase();
  if (r.includes("AU") || r.includes("AUS") || r.includes("AUSTRALIA") || r.includes("APAC")) {
    return "AU";
  }
  if (r.includes("US") || r.includes("USA") || r.includes("UNITED STATES") || r.includes("AMERICA")) {
    return "US";
  }
  return "UNKNOWN";
}

function dateFromCreated(created: string): string {
  // 2026-08-15T12:34:56+00:00 or similar
  const m = /^(\d{4}-\d{2}-\d{2})/.exec(created);
  return m?.[1] || created.slice(0, 10);
}

export function normalizeZohoInquiries(
  records: ZohoRecord[],
  gclidField: string,
): ZohoInquiryDayRow[] {
  return records.map((rec) => {
    const gclid = normalizeGclid(str(rec[gclidField]));
    const utm_campaign = str(rec.utm_campaign) || str(rec.Campaign_Name) || null;
    const utm_term = str(rec.utm_term) || null;
    const utm_content = str(rec.utm_content) || null;
    const landing = str(rec.Referring_URL) || null;
    const date = dateFromCreated(str(rec.Created_Time));
    const join = resolveJoin({
      gclid,
      utm_campaign,
      utm_content,
      utm_term,
      ad_group: utm_content,
      keyword: utm_term,
      date,
      landing_page: landing,
    });
    const market = marketFromRegion(str(rec.Region));
    const leadSource = str(rec.Lead_Source);
    const paid_likely =
      Boolean(gclid) ||
      /google|cpc|ppc|paid|ads/i.test(str(rec.utm_medium)) ||
      /google|cpc|ppc|paid|ads/i.test(leadSource);

    return {
      date,
      market,
      record_id: str(rec.id),
      status: str(rec.Lead_Status),
      lead_source: leadSource,
      utm_source: str(rec.utm_source) || null,
      utm_medium: str(rec.utm_medium) || null,
      utm_campaign,
      utm_term,
      utm_content,
      has_gclid: Boolean(gclid),
      landing_page: landing,
      join_method: join.method,
      join_key: join.key,
      join_inferred: join.method === "date_landing_page_fallback",
      paid_likely,
    };
  });
}

export type ZohoPullResult = {
  inquiries: ZohoInquiryDayRow[];
  errors: string[];
};

export async function pullZohoWindow(
  cfg: ZohoReadConfig,
  start: string,
  end: string,
  opts: { fetchImpl?: typeof fetch } = {},
): Promise<ZohoPullResult> {
  try {
    const raw = await fetchZohoInquiries(cfg, start, end, opts);
    return {
      inquiries: normalizeZohoInquiries(raw, cfg.gclidField),
      errors: [],
    };
  } catch (err) {
    return { inquiries: [], errors: [redactUnknown(err)] };
  }
}
