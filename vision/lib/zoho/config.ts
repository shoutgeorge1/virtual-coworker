/**
 * Server-only Zoho CRM env parsing.
 * Never expose these via NEXT_PUBLIC_*.
 */

export type ZohoCrmConfig = {
  enabled: boolean;
  clientId: string;
  clientSecret: string;
  refreshToken: string;
  accountsUrl: string;
  apiDomain: string;
  module: string;
  /** External id field API name for upsert idempotency */
  submissionIdField: string;
  /** Optional verified custom field API names; empty = omit (don't invent) */
  fields: ZohoFieldOverrides;
  timeoutMs: number;
};

export type ZohoFieldOverrides = {
  gclid?: string;
  gbraid?: string;
  wbraid?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  market?: string;
  category?: string;
  variant?: string;
  lp_version?: string;
  landing_page_url?: string;
  referrer?: string;
  role?: string;
  timeline?: string;
  company_size?: string;
  positions_needed?: string;
  hiring_timeline?: string;
  lead_score?: string;
  estimated_lead_value?: string;
  message?: string;
};

const DEFAULT_ACCOUNTS = "https://accounts.zoho.com";
const DEFAULT_API = "https://www.zohoapis.com";

function trim(v: string | undefined): string {
  return (v || "").trim();
}

function bool(v: string | undefined): boolean {
  return trim(v).toLowerCase() === "true";
}

function optField(env: NodeJS.ProcessEnv, key: string): string | undefined {
  const v = trim(env[key]);
  return v || undefined;
}

/**
 * Parse Zoho CRM config. `enabled` requires flag + credentials.
 * Missing credentials ⇒ not enabled (safe default).
 */
export function parseZohoCrmConfig(env: NodeJS.ProcessEnv = process.env): ZohoCrmConfig {
  const clientId = trim(env.ZOHO_CRM_CLIENT_ID);
  const clientSecret = trim(env.ZOHO_CRM_CLIENT_SECRET);
  const refreshToken = trim(env.ZOHO_CRM_REFRESH_TOKEN);
  const flag = bool(env.ZOHO_CRM_ENABLED);
  const hasCreds = Boolean(clientId && clientSecret && refreshToken);

  const timeoutRaw = Number(trim(env.ZOHO_CRM_TIMEOUT_MS) || "15000");
  const timeoutMs = Number.isFinite(timeoutRaw) && timeoutRaw > 0 ? timeoutRaw : 15000;

  return {
    enabled: flag && hasCreds,
    clientId,
    clientSecret,
    refreshToken,
    accountsUrl: trim(env.ZOHO_CRM_ACCOUNTS_URL) || DEFAULT_ACCOUNTS,
    apiDomain: trim(env.ZOHO_CRM_API_DOMAIN) || DEFAULT_API,
    module: trim(env.ZOHO_CRM_MODULE) || "Leads",
    submissionIdField: trim(env.ZOHO_CRM_SUBMISSION_ID_FIELD) || "VC_Submission_ID",
    fields: {
      gclid: optField(env, "ZOHO_CRM_FIELD_GCLID"),
      gbraid: optField(env, "ZOHO_CRM_FIELD_GBRAID"),
      wbraid: optField(env, "ZOHO_CRM_FIELD_WBRAID"),
      utm_source: optField(env, "ZOHO_CRM_FIELD_UTM_SOURCE"),
      utm_medium: optField(env, "ZOHO_CRM_FIELD_UTM_MEDIUM"),
      utm_campaign: optField(env, "ZOHO_CRM_FIELD_UTM_CAMPAIGN"),
      utm_term: optField(env, "ZOHO_CRM_FIELD_UTM_TERM"),
      utm_content: optField(env, "ZOHO_CRM_FIELD_UTM_CONTENT"),
      market: optField(env, "ZOHO_CRM_FIELD_MARKET"),
      category: optField(env, "ZOHO_CRM_FIELD_CATEGORY"),
      variant: optField(env, "ZOHO_CRM_FIELD_VARIANT"),
      lp_version: optField(env, "ZOHO_CRM_FIELD_LP_VERSION"),
      landing_page_url: optField(env, "ZOHO_CRM_FIELD_LANDING_PAGE_URL"),
      referrer: optField(env, "ZOHO_CRM_FIELD_REFERRER"),
      role: optField(env, "ZOHO_CRM_FIELD_ROLE"),
      timeline: optField(env, "ZOHO_CRM_FIELD_TIMELINE"),
      company_size: optField(env, "ZOHO_CRM_FIELD_COMPANY_SIZE"),
      positions_needed: optField(env, "ZOHO_CRM_FIELD_POSITIONS_NEEDED"),
      hiring_timeline: optField(env, "ZOHO_CRM_FIELD_HIRING_TIMELINE"),
      lead_score: optField(env, "ZOHO_CRM_FIELD_LEAD_SCORE"),
      estimated_lead_value: optField(env, "ZOHO_CRM_FIELD_ESTIMATED_LEAD_VALUE"),
      message: optField(env, "ZOHO_CRM_FIELD_MESSAGE"),
    },
    timeoutMs,
  };
}

export function zohoCrmConfigured(env: NodeJS.ProcessEnv = process.env): boolean {
  return parseZohoCrmConfig(env).enabled;
}
