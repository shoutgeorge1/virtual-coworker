/**
 * GA4 Data API — read-only landing-page daily rows.
 * Auth: service account JSON via GA4_SERVICE_ACCOUNT_JSON (Vercel)
 * or GOOGLE_APPLICATION_CREDENTIALS file path (local).
 */

import { createSign } from "node:crypto";
import { readFileSync } from "node:fs";
import { withRetry } from "@/lib/sync/retry";
import { redactText, redactUnknown } from "@/lib/sync/redact";
import type { LandingPageDayRow, Market } from "@/lib/sync/types";

const GA_SCOPE = "https://www.googleapis.com/auth/analytics.readonly";
const TOKEN_URL = "https://oauth2.googleapis.com/token";

export type Ga4Config = {
  propertyIdUs: string;
  propertyIdAu: string | null;
  clientEmail: string;
  privateKey: string;
};

type SaJson = {
  client_email?: string;
  private_key?: string;
};

export function parseGa4Config(env: NodeJS.ProcessEnv = process.env): Ga4Config | null {
  const propertyIdUs = (env.GA4_PROPERTY_ID || "549075481").trim();
  const propertyIdAu = (env.GA4_PROPERTY_ID_AU || "").trim() || null;
  const sa = loadServiceAccount(env);
  if (!sa?.client_email || !sa.private_key || !propertyIdUs) return null;
  return {
    propertyIdUs,
    propertyIdAu,
    clientEmail: sa.client_email,
    privateKey: sa.private_key.replace(/\\n/g, "\n"),
  };
}

function loadServiceAccount(env: NodeJS.ProcessEnv): SaJson | null {
  const raw = (env.GA4_SERVICE_ACCOUNT_JSON || env.GOOGLE_SERVICE_ACCOUNT_JSON || "").trim();
  if (raw) {
    try {
      return JSON.parse(raw) as SaJson;
    } catch {
      try {
        return JSON.parse(Buffer.from(raw, "base64").toString("utf8")) as SaJson;
      } catch {
        return null;
      }
    }
  }
  const path = (env.GOOGLE_APPLICATION_CREDENTIALS || "").trim();
  if (path) {
    try {
      return JSON.parse(readFileSync(path, "utf8")) as SaJson;
    } catch {
      return null;
    }
  }
  return null;
}

function base64url(input: Buffer | string): string {
  const b = Buffer.isBuffer(input) ? input : Buffer.from(input);
  return b.toString("base64").replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}

async function serviceAccountAccessToken(
  cfg: Ga4Config,
  fetchImpl: typeof fetch = fetch,
): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  const header = base64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claim = base64url(
    JSON.stringify({
      iss: cfg.clientEmail,
      scope: GA_SCOPE,
      aud: TOKEN_URL,
      iat: now,
      exp: now + 3600,
    }),
  );
  const unsigned = `${header}.${claim}`;
  const signer = createSign("RSA-SHA256");
  signer.update(unsigned);
  const sig = base64url(signer.sign(cfg.privateKey));
  const assertion = `${unsigned}.${sig}`;

  const body = new URLSearchParams({
    grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
    assertion,
  });
  const res = await fetchImpl(TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  const text = await res.text();
  if (!res.ok) {
    throw new Error(`GA4 SA token HTTP ${res.status}: ${redactText(text.slice(0, 180))}`);
  }
  const json = JSON.parse(text) as { access_token?: string };
  if (!json.access_token) throw new Error("GA4 SA token missing access_token");
  return json.access_token;
}

type Ga4Row = {
  dimensionValues?: Array<{ value?: string }>;
  metricValues?: Array<{ value?: string }>;
};

async function runReport(
  cfg: Ga4Config,
  propertyId: string,
  start: string,
  end: string,
  fetchImpl: typeof fetch,
): Promise<Ga4Row[]> {
  return withRetry(async () => {
    const token = await serviceAccountAccessToken(cfg, fetchImpl);
    const url = `https://analyticsdata.googleapis.com/v1beta/properties/${propertyId}:runReport`;
    const all: Ga4Row[] = [];
    let offset = 0;
    const limit = 10_000;

    for (;;) {
      const res = await fetchImpl(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          dateRanges: [{ startDate: start, endDate: end }],
          dimensions: [{ name: "date" }, { name: "landingPagePlusQueryString" }],
          metrics: [
            { name: "sessions" },
            { name: "engagedSessions" },
            { name: "conversions" },
            { name: "totalUsers" },
          ],
          limit,
          offset,
        }),
      });
      const text = await res.text();
      if (!res.ok) {
        throw new Error(`GA4 runReport HTTP ${res.status}: ${redactText(text.slice(0, 240))}`);
      }
      const json = JSON.parse(text) as {
        rows?: Ga4Row[];
        rowCount?: number;
      };
      const batch = json.rows || [];
      all.push(...batch);
      offset += batch.length;
      if (!batch.length || offset >= Number(json.rowCount || 0)) break;
    }
    return all;
  });
}

function ga4DateToIso(raw: string): string {
  // GA4 returns YYYYMMDD
  if (/^\d{8}$/.test(raw)) {
    return `${raw.slice(0, 4)}-${raw.slice(4, 6)}-${raw.slice(6, 8)}`;
  }
  return raw;
}

function inferMarketFromPath(path: string): Market | "other" {
  const p = (path || "").toLowerCase().split("?")[0] || "";
  if (p === "/au" || p.startsWith("/au/")) return "AU";
  if (p === "/us" || p.startsWith("/us/")) return "US";
  return "other";
}

export function normalizeLandingRows(
  rows: Ga4Row[],
  market: Market,
  propertyId: string,
): LandingPageDayRow[] {
  const out: LandingPageDayRow[] = [];
  for (const row of rows) {
    const dims = row.dimensionValues || [];
    const mets = row.metricValues || [];
    const date = ga4DateToIso(dims[0]?.value || "");
    const landing = dims[1]?.value || "(not set)";
    if (!date) continue;
    out.push({
      date,
      market,
      property_id: propertyId,
      landing_page: landing,
      sessions: Number(mets[0]?.value || 0) || 0,
      engaged_sessions: Number(mets[1]?.value || 0) || 0,
      conversions: Number(mets[2]?.value || 0) || 0,
      total_users: Number(mets[3]?.value || 0) || 0,
    });
  }
  return out;
}

export type Ga4PullResult = {
  landingPages: LandingPageDayRow[];
  errors: string[];
};

export async function pullGa4Window(
  cfg: Ga4Config,
  start: string,
  end: string,
  opts: { fetchImpl?: typeof fetch } = {},
): Promise<Ga4PullResult> {
  const fetchImpl = opts.fetchImpl || fetch;
  const out: Ga4PullResult = { landingPages: [], errors: [] };

  const jobs: Array<{ market: Market; propertyId: string }> = [
    { market: "US", propertyId: cfg.propertyIdUs },
  ];
  if (cfg.propertyIdAu) {
    jobs.push({ market: "AU", propertyId: cfg.propertyIdAu });
  }

  for (const job of jobs) {
    try {
      const rows = await runReport(cfg, job.propertyId, start, end, fetchImpl);
      const normalized = normalizeLandingRows(rows, job.market, job.propertyId);
      // Keep property market as source of truth; path inference is informational only.
      out.landingPages.push(
        ...normalized.map((r) => {
          const inferred = inferMarketFromPath(r.landing_page);
          return inferred === "other" || inferred === job.market
            ? r
            : { ...r, market: job.market };
        }),
      );
    } catch (err) {
      out.errors.push(`${job.market}: ${redactUnknown(err)}`);
    }
  }

  return out;
}
