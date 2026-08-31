/**
 * Server-only Zoho CRM env parsing.
 * Never expose these via NEXT_PUBLIC_*.
 *
 * Production write gate is ZOHO_SUBMISSION_ENABLED (default false).
 * ZOHO_CRM_ENABLED is ignored for writes and must stay false.
 */

export type ZohoCrmConfig = {
  enabled: boolean;
  clientId: string;
  clientSecret: string;
  refreshToken: string;
  accountsUrl: string;
  apiDomain: string;
  module: string;
  /** Existing writable text field used as submission id (not a new custom field). */
  submissionIdField: string;
  /** Verified writable notes field (this org has no Description). */
  notesField: string;
  /** Safe initial Sales Enquiry status only. Never Discovery/JO/Placement. */
  leadStatus: string;
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
  form_source?: string;
  lead_source?: string;
  campaign_name?: string;
  website?: string;
};

const DEFAULT_ACCOUNTS = "https://accounts.zoho.com";
const DEFAULT_API = "https://www.zohoapis.com";

/** Verified 2026-08-17 from CRM v8 settings/fields on Leads (UI: Sales Enquiries). */
export const VERIFIED_SALES_ENQUIRY = {
  module: "Leads",
  moduleDisplay: "Sales Enquiries",
  submissionIdField: "Gravity_Form_Entry_ID",
  notesField: "Other_Client_Profile_Information",
  leadStatus: "New Enquiry (Auto)",
  gclid: "utm_gclid",
  utm_source: "utm_source",
  utm_medium: "utm_medium",
  utm_campaign: "utm_campaign",
  utm_term: "utm_term",
  utm_content: "utm_content",
  market: "Region",
  landing_page_url: "Referring_URL",
  role: "Job_Position_Required",
  form_source: "Form_Source",
  lead_source: "Lead_Source",
  campaign_name: "Campaign_Name",
  website: "Website",
} as const;

/** Existing Lead_Source picklist values that cannot mean JO / Discovery / qualified. */
export const SAFE_LEAD_SOURCE_VALUES = new Set([
  "Other",
  "Website",
  "Advertisement",
  "Web Research",
  "Web Download",
]);

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
 * Parse Zoho CRM config. Writes require ZOHO_SUBMISSION_ENABLED=true + credentials.
 * ZOHO_CRM_ENABLED never enables writes.
 */
export function parseZohoCrmConfig(env: NodeJS.ProcessEnv = process.env): ZohoCrmConfig {
  const clientId = trim(env.ZOHO_CRM_CLIENT_ID);
  const clientSecret = trim(env.ZOHO_CRM_CLIENT_SECRET);
  const refreshToken = trim(env.ZOHO_CRM_REFRESH_TOKEN);
  const submissionFlag = bool(env.ZOHO_SUBMISSION_ENABLED);
  const hasCreds = Boolean(clientId && clientSecret && refreshToken);

  const timeoutRaw = Number(trim(env.ZOHO_CRM_TIMEOUT_MS) || "15000");
  const timeoutMs = Number.isFinite(timeoutRaw) && timeoutRaw > 0 ? timeoutRaw : 15000;

  return {
    enabled: submissionFlag && hasCreds,
    clientId,
    clientSecret,
    refreshToken,
    accountsUrl: trim(env.ZOHO_CRM_ACCOUNTS_URL) || DEFAULT_ACCOUNTS,
    apiDomain: trim(env.ZOHO_CRM_API_DOMAIN) || DEFAULT_API,
    module: trim(env.ZOHO_CRM_MODULE) || VERIFIED_SALES_ENQUIRY.module,
    submissionIdField:
      trim(env.ZOHO_CRM_SUBMISSION_ID_FIELD) || VERIFIED_SALES_ENQUIRY.submissionIdField,
    notesField: trim(env.ZOHO_CRM_FIELD_MESSAGE) || VERIFIED_SALES_ENQUIRY.notesField,
    leadStatus: trim(env.ZOHO_CRM_LEAD_STATUS) || VERIFIED_SALES_ENQUIRY.leadStatus,
    fields: {
      gclid: optField(env, "ZOHO_CRM_FIELD_GCLID") || VERIFIED_SALES_ENQUIRY.gclid,
      gbraid: optField(env, "ZOHO_CRM_FIELD_GBRAID"),
      wbraid: optField(env, "ZOHO_CRM_FIELD_WBRAID"),
      utm_source: optField(env, "ZOHO_CRM_FIELD_UTM_SOURCE") || VERIFIED_SALES_ENQUIRY.utm_source,
      utm_medium: optField(env, "ZOHO_CRM_FIELD_UTM_MEDIUM") || VERIFIED_SALES_ENQUIRY.utm_medium,
      utm_campaign:
        optField(env, "ZOHO_CRM_FIELD_UTM_CAMPAIGN") || VERIFIED_SALES_ENQUIRY.utm_campaign,
      utm_term: optField(env, "ZOHO_CRM_FIELD_UTM_TERM") || VERIFIED_SALES_ENQUIRY.utm_term,
      utm_content: optField(env, "ZOHO_CRM_FIELD_UTM_CONTENT") || VERIFIED_SALES_ENQUIRY.utm_content,
      market: optField(env, "ZOHO_CRM_FIELD_MARKET") || VERIFIED_SALES_ENQUIRY.market,
      category: optField(env, "ZOHO_CRM_FIELD_CATEGORY"),
      variant: optField(env, "ZOHO_CRM_FIELD_VARIANT"),
      lp_version: optField(env, "ZOHO_CRM_FIELD_LP_VERSION"),
      landing_page_url:
        optField(env, "ZOHO_CRM_FIELD_LANDING_PAGE_URL") || VERIFIED_SALES_ENQUIRY.landing_page_url,
      referrer: optField(env, "ZOHO_CRM_FIELD_REFERRER"),
      role: optField(env, "ZOHO_CRM_FIELD_ROLE") || VERIFIED_SALES_ENQUIRY.role,
      timeline: optField(env, "ZOHO_CRM_FIELD_TIMELINE"),
      company_size: optField(env, "ZOHO_CRM_FIELD_COMPANY_SIZE"),
      positions_needed: optField(env, "ZOHO_CRM_FIELD_POSITIONS_NEEDED"),
      hiring_timeline: optField(env, "ZOHO_CRM_FIELD_HIRING_TIMELINE"),
      lead_score: optField(env, "ZOHO_CRM_FIELD_LEAD_SCORE"),
      estimated_lead_value: optField(env, "ZOHO_CRM_FIELD_ESTIMATED_LEAD_VALUE"),
      message: optField(env, "ZOHO_CRM_FIELD_MESSAGE") || VERIFIED_SALES_ENQUIRY.notesField,
      form_source: optField(env, "ZOHO_CRM_FIELD_FORM_SOURCE") || VERIFIED_SALES_ENQUIRY.form_source,
      lead_source: optField(env, "ZOHO_CRM_FIELD_LEAD_SOURCE") || VERIFIED_SALES_ENQUIRY.lead_source,
      campaign_name:
        optField(env, "ZOHO_CRM_FIELD_CAMPAIGN_NAME") || VERIFIED_SALES_ENQUIRY.campaign_name,
      website: optField(env, "ZOHO_CRM_FIELD_WEBSITE") || VERIFIED_SALES_ENQUIRY.website,
    },
    timeoutMs,
  };
}

export function zohoCrmConfigured(env: NodeJS.ProcessEnv = process.env): boolean {
  return parseZohoCrmConfig(env).enabled;
}

export function uniqueSubmissionId(prefix = "VC"): string {
  const ts = Date.now().toString(36);
  const rand = Math.random().toString(36).slice(2, 8);
  return `${prefix}-${ts}-${rand}`;
}
