/**
 * Map employer lead → Zoho Sales Enquiry (Leads) using verified API names only.
 * Create-only. Do not invent fields. Do not write Ads-filter status values.
 */

import {
  SAFE_LEAD_SOURCE_VALUES,
  VERIFIED_SALES_ENQUIRY,
  type ZohoCrmConfig,
  type ZohoFieldOverrides,
} from "./config";

export type LeadRecord = {
  submission_id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  company?: string;
  company_website?: string;
  role?: string;
  category?: string;
  variant?: string;
  timeline?: string;
  company_size?: string;
  positions_needed?: string;
  schedule?: string;
  hiring_timeline?: string;
  lead_score?: number | string;
  estimated_lead_value?: number | string;
  value_kind?: string;
  fit_label?: string;
  message?: string;
  market: string;
  intent?: string;
  lead_source?: string;
  form_source?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  gclid?: string;
  gbraid?: string;
  wbraid?: string;
  adgroup?: string;
  keyword?: string;
  match_type?: string;
  device?: string;
  landing_page_url?: string;
  referrer?: string;
  lp_version?: string;
  submitted_at?: string;
  session_id?: string;
  is_job_order?: boolean;
  is_placement?: boolean;
};

export const STANDARD_LEAD_FIELDS = {
  First_Name: "First_Name",
  Last_Name: "Last_Name",
  Email: "Email",
  Phone: "Phone",
  Company: "Company",
} as const;

/** Status values that Google Ads Data Manager connections are named after. Never write these. */
export const ADS_FILTER_STATUS_VALUES = new Set([
  "Discovery Scheduled",
  "Job Order Submitted",
  "Placement",
  "Create Job Opening",
  "Pre-Qualified",
  "Contact Successful",
  "Discovery Booked",
  "Discovery Completed",
  "Qualified",
]);

export type VerifiedFieldSet = {
  apiNames: Set<string>;
  allowStandards: boolean;
};

export type FieldProposal = {
  proposed_api_name: string;
  purpose: string;
  required_for: string;
};

export type MappedPayload = {
  module: string;
  data: Record<string, unknown>;
  omitted: string[];
  proposals: FieldProposal[];
  duplicateCheckFields: string[];
  usesGclidSystemKey: boolean;
};

function setIf(
  data: Record<string, unknown>,
  apiName: string | undefined,
  value: string | undefined,
  omitted: string[],
  logical: string,
  verified: VerifiedFieldSet | null,
): void {
  const v = (value || "").trim();
  if (!v) return;
  if (!apiName) {
    omitted.push(logical);
    return;
  }
  if (verified && !verified.apiNames.has(apiName) && apiName !== "$gclid") {
    omitted.push(logical);
    return;
  }
  data[apiName] = v;
}

export function regionForMarket(market: string): string {
  const m = (market || "").trim().toLowerCase();
  if (m === "us" || m === "usa") return "USA";
  if (m === "au") return "AU";
  return "";
}

/** Zoho CRM datetime: `YYYY-MM-DDTHH:MM:SS+00:00`. Rejects JS `...Z` and fractional seconds. */
export function formatZohoDateTime(raw: string): string | undefined {
  const v = raw.trim();
  if (!v) return undefined;
  const ms = Date.parse(v);
  if (!Number.isFinite(ms)) return undefined;
  const d = new Date(ms);
  const pad = (n: number) => String(n).padStart(2, "0");
  return (
    `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}` +
    `T${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())}+00:00`
  );
}

export function buildEnquiryNotes(lead: LeadRecord): string {
  const lines: string[] = [];
  const banner = (lead.message || "").trim();
  if (banner) lines.push(banner);
  const extras: [string, string][] = [
    ["submission_id", lead.submission_id],
    ["lead_source_requested", lead.lead_source || ""],
    ["market", lead.market],
    ["role", lead.role || ""],
    ["category", lead.category || ""],
    ["company_size", lead.company_size || ""],
    ["positions_needed", lead.positions_needed || ""],
    ["schedule", lead.schedule || ""],
    ["hiring_timeline", lead.hiring_timeline || lead.timeline || ""],
    ["gclid", lead.gclid || ""],
    ["gbraid", lead.gbraid || ""],
    ["wbraid", lead.wbraid || ""],
    ["utm_source", lead.utm_source || ""],
    ["utm_medium", lead.utm_medium || ""],
    ["utm_campaign", lead.utm_campaign || ""],
    ["utm_term", lead.utm_term || ""],
    ["utm_content", lead.utm_content || ""],
    ["adgroup", lead.adgroup || ""],
    ["keyword", lead.keyword || ""],
    ["match_type", lead.match_type || ""],
    ["device", lead.device || ""],
    ["landing_page_url", lead.landing_page_url || ""],
    ["referrer", lead.referrer || ""],
    ["lp_version", lead.lp_version || ""],
    ["session_id", lead.session_id || ""],
    ["submitted_at", lead.submitted_at || ""],
  ];
  const filled = extras.filter(([, v]) => v.trim());
  if (filled.length) {
    lines.push("");
    lines.push("--- VC LP payload ---");
    for (const [k, v] of filled) lines.push(`${k}: ${v}`);
  }
  return lines.join("\n").slice(0, 30000);
}

/**
 * Build a create-only Sales Enquiry body.
 * Never writes Ads-filter statuses, JO flags, discovery dates, or qualification.
 */
export function mapLeadToCrmPayload(
  lead: LeadRecord,
  config: Pick<ZohoCrmConfig, "module" | "submissionIdField" | "notesField" | "leadStatus" | "fields">,
  verified: VerifiedFieldSet | null = null,
): MappedPayload {
  const data: Record<string, unknown> = {};
  const omitted: string[] = [];
  const fields: ZohoFieldOverrides = config.fields;
  const allowStd = !verified || verified.allowStandards;

  const std = (name: keyof typeof STANDARD_LEAD_FIELDS, value: string | undefined, logical: string) => {
    const api = STANDARD_LEAD_FIELDS[name];
    if (!allowStd) {
      if (verified && verified.apiNames.has(api)) {
        setIf(data, api, value, omitted, logical, verified);
      } else if ((value || "").trim()) {
        omitted.push(logical);
      }
      return;
    }
    if (verified && !verified.apiNames.has(api)) {
      if ((value || "").trim()) omitted.push(logical);
      return;
    }
    const v = (value || "").trim();
    if (v) data[api] = v;
  };

  std("First_Name", lead.firstName, "firstName");
  std("Last_Name", lead.lastName || lead.email, "lastName");
  std("Email", lead.email, "email");
  std("Phone", lead.phone, "phone");
  std("Company", lead.company, "company");

  const notes = buildEnquiryNotes(lead);
  if (notes) {
    setIf(data, config.notesField || fields.message, notes, omitted, "message", verified);
  }

  setIf(data, config.submissionIdField, lead.submission_id, omitted, "submission_id", verified);
  setIf(data, fields.website, lead.company_website, omitted, "company_website", verified);
  setIf(data, fields.role, lead.role, omitted, "role", verified);
  setIf(data, fields.landing_page_url, lead.landing_page_url, omitted, "landing_page_url", verified);

  const region = regionForMarket(lead.market);
  setIf(data, fields.market, region, omitted, "market", verified);

  const requestedSource = (lead.lead_source || "").trim();
  if (requestedSource && SAFE_LEAD_SOURCE_VALUES.has(requestedSource)) {
    setIf(data, fields.lead_source, requestedSource, omitted, "lead_source", verified);
  } else if (requestedSource) {
    omitted.push("lead_source_picklist");
  }

  const formSource = (lead.form_source || lead.lead_source || "").trim();
  setIf(data, fields.form_source, formSource, omitted, "form_source", verified);

  const safeStatus = (config.leadStatus || VERIFIED_SALES_ENQUIRY.leadStatus).trim();
  if (safeStatus && !ADS_FILTER_STATUS_VALUES.has(safeStatus)) {
    data.Lead_Status = safeStatus;
  }

  setIf(data, fields.utm_source, lead.utm_source, omitted, "utm_source", verified);
  setIf(data, fields.utm_medium, lead.utm_medium, omitted, "utm_medium", verified);
  setIf(data, fields.utm_campaign, lead.utm_campaign, omitted, "utm_campaign", verified);
  setIf(data, fields.utm_term, lead.utm_term, omitted, "utm_term", verified);
  setIf(data, fields.utm_content, lead.utm_content, omitted, "utm_content", verified);
  setIf(data, fields.campaign_name, lead.utm_campaign, omitted, "campaign_name", verified);

  const gclid = (lead.gclid || "").trim();
  if (gclid) {
    setIf(data, fields.gclid || VERIFIED_SALES_ENQUIRY.gclid, gclid, omitted, "gclid", verified);
  }
  if ((lead.gbraid || "").trim()) omitted.push("gbraid");
  if ((lead.wbraid || "").trim()) omitted.push("wbraid");
  if ((lead.referrer || "").trim()) omitted.push("referrer");

  const submitted = formatZohoDateTime(lead.submitted_at || "");
  if (submitted) {
    data.Submission_Timestamp = submitted;
  }

  const proposals = proposeMissingFields(omitted, config.submissionIdField);

  return {
    module: config.module,
    data,
    omitted: [...new Set(omitted)],
    proposals,
    duplicateCheckFields: [],
    usesGclidSystemKey: false,
  };
}

export function proposeMissingFields(
  omittedLogical: string[],
  submissionIdField: string,
): FieldProposal[] {
  const catalog: Record<string, FieldProposal> = {
    gbraid: {
      proposed_api_name: "(none — fold into Enquiry Notes)",
      purpose: "iOS click id",
      required_for: "Ads attribution",
    },
    wbraid: {
      proposed_api_name: "(none — fold into Enquiry Notes)",
      purpose: "Web click id",
      required_for: "Ads attribution",
    },
    referrer: {
      proposed_api_name: "Referrer (read-only) — fold into Enquiry Notes",
      purpose: "HTTP referrer",
      required_for: "attribution",
    },
    lead_source_picklist: {
      proposed_api_name: "Form_Source + Enquiry Notes",
      purpose: "Requested source is not an existing Lead_Source picklist value",
      required_for: "do not invent picklist values",
    },
    submission_id: {
      proposed_api_name: submissionIdField,
      purpose: "External submission id",
      required_for: "traceability",
    },
  };
  const out: FieldProposal[] = [];
  for (const key of omittedLogical) {
    if (catalog[key]) out.push(catalog[key]);
  }
  return out;
}

export function formatSchemaApplyProposal(proposals: FieldProposal[]): string {
  if (!proposals.length) return "No missing-field proposals.";
  const lines = [
    "SCHEMA APPLY PROPOSAL (requires George approval; do not auto-create)",
    ...proposals.map((p) => `- ${p.proposed_api_name}: ${p.purpose} (${p.required_for})`),
  ];
  return lines.join("\n");
}
