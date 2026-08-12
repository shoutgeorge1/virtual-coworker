/**
 * Map employer lead → Zoho CRM fields using verified / configured API names only.
 * Do not invent custom fields. Prefer $gclid when gclid present.
 * Prefer VC_Submission_ID (configurable) as external id for upsert idempotency.
 */

import type { ZohoCrmConfig, ZohoFieldOverrides } from "./config";

export type LeadRecord = {
  submission_id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  company?: string;
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
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  gclid?: string;
  gbraid?: string;
  wbraid?: string;
  landing_page_url?: string;
  referrer?: string;
  lp_version?: string;
  submitted_at?: string;
  is_job_order?: boolean;
  is_placement?: boolean;
};

/** Standard Zoho Leads API names (documented platform fields — not custom invent). */
export const STANDARD_LEAD_FIELDS = {
  First_Name: "First_Name",
  Last_Name: "Last_Name",
  Email: "Email",
  Phone: "Phone",
  Company: "Company",
  Description: "Description",
} as const;

export type VerifiedFieldSet = {
  /** When provided, only these API names (+ $gclid) may be written besides standards if included */
  apiNames: Set<string>;
  /** If true, include First_Name/Last_Name/Email/Phone/Company/Description when present in apiNames or allowStandards */
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
  /** Fields requested by lead but absent from verified set */
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

/**
 * Build CRM record body. If `verified` is null, only standard Lead fields + $gclid +
 * explicitly configured override fields are used (override names assumed verified by operator).
 */
export function mapLeadToCrmPayload(
  lead: LeadRecord,
  config: Pick<ZohoCrmConfig, "module" | "submissionIdField" | "fields">,
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
      } else {
        if ((value || "").trim()) omitted.push(logical);
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

  const descParts = [
    lead.role ? `Role: ${lead.role}` : "",
    lead.company_size ? `Company size: ${lead.company_size}` : "",
    lead.positions_needed ? `Positions needed: ${lead.positions_needed}` : "",
    lead.schedule ? `Schedule: ${lead.schedule}` : "",
    lead.hiring_timeline || lead.timeline
      ? `Timeline: ${lead.hiring_timeline || lead.timeline}`
      : "",
    lead.lead_score !== undefined && lead.lead_score !== ""
      ? `Modeled lead score: ${lead.lead_score} (website estimate — not revenue)`
      : "",
    lead.estimated_lead_value !== undefined && lead.estimated_lead_value !== ""
      ? `Modeled lead value USD: ${lead.estimated_lead_value} (${lead.value_kind || "estimated_modeled"})`
      : "",
    lead.message || "",
  ].filter(Boolean);
  if (descParts.length) {
    std("Description", descParts.join("\n"), "message");
  }

  // Idempotency external id
  setIf(
    data,
    config.submissionIdField,
    lead.submission_id,
    omitted,
    "submission_id",
    verified,
  );

  // Prefer Zoho system key when gclid present
  let usesGclidSystemKey = false;
  const gclid = (lead.gclid || "").trim();
  if (gclid) {
    const customGclid = fields.gclid;
    if (!customGclid || customGclid === "$gclid") {
      if (!verified || verified.apiNames.has("$gclid")) {
        data["$gclid"] = gclid;
        usesGclidSystemKey = true;
      } else {
        omitted.push("gclid");
      }
    } else if (!verified || verified.apiNames.has(customGclid)) {
      data[customGclid] = gclid;
    } else {
      omitted.push("gclid");
    }
  }

  setIf(data, fields.gbraid, lead.gbraid, omitted, "gbraid", verified);
  setIf(data, fields.wbraid, lead.wbraid, omitted, "wbraid", verified);
  setIf(data, fields.utm_source, lead.utm_source, omitted, "utm_source", verified);
  setIf(data, fields.utm_medium, lead.utm_medium, omitted, "utm_medium", verified);
  setIf(data, fields.utm_campaign, lead.utm_campaign, omitted, "utm_campaign", verified);
  setIf(data, fields.utm_term, lead.utm_term, omitted, "utm_term", verified);
  setIf(data, fields.utm_content, lead.utm_content, omitted, "utm_content", verified);
  setIf(data, fields.market, lead.market, omitted, "market", verified);
  setIf(data, fields.category, lead.category, omitted, "category", verified);
  setIf(data, fields.variant, lead.variant, omitted, "variant", verified);
  setIf(data, fields.lp_version, lead.lp_version, omitted, "lp_version", verified);
  setIf(data, fields.landing_page_url, lead.landing_page_url, omitted, "landing_page_url", verified);
  setIf(data, fields.referrer, lead.referrer, omitted, "referrer", verified);
  setIf(data, fields.role, lead.role, omitted, "role", verified);
  setIf(data, fields.timeline, lead.hiring_timeline || lead.timeline, omitted, "timeline", verified);
  setIf(data, fields.company_size, lead.company_size, omitted, "company_size", verified);
  setIf(data, fields.positions_needed, lead.positions_needed, omitted, "positions_needed", verified);
  setIf(data, fields.hiring_timeline, lead.hiring_timeline, omitted, "hiring_timeline", verified);
  setIf(
    data,
    fields.lead_score,
    lead.lead_score !== undefined ? String(lead.lead_score) : "",
    omitted,
    "lead_score",
    verified,
  );
  setIf(
    data,
    fields.estimated_lead_value,
    lead.estimated_lead_value !== undefined ? String(lead.estimated_lead_value) : "",
    omitted,
    "estimated_lead_value",
    verified,
  );

  // Honesty flags — only if verified custom fields exist (never invent)
  // is_job_order / is_placement intentionally not written unless schema has them later.

  const proposals = proposeMissingFields(omitted, config.submissionIdField);
  const duplicateCheckFields =
    data[config.submissionIdField] != null ? [config.submissionIdField] : [];

  return {
    module: config.module,
    data,
    omitted: [...new Set(omitted)],
    proposals,
    duplicateCheckFields,
    usesGclidSystemKey,
  };
}

export function proposeMissingFields(
  omittedLogical: string[],
  submissionIdField: string,
): FieldProposal[] {
  const catalog: Record<string, FieldProposal> = {
    submission_id: {
      proposed_api_name: submissionIdField,
      purpose: "Idempotent employer inquiry id",
      required_for: "upsert / zoho_synced reliability",
    },
    gclid: {
      proposed_api_name: "$gclid or GCLID",
      purpose: "Google click id",
      required_for: "Ads attribution",
    },
    gbraid: {
      proposed_api_name: "GBRAID",
      purpose: "iOS click id",
      required_for: "Ads attribution",
    },
    wbraid: {
      proposed_api_name: "WBRAID",
      purpose: "Web click id",
      required_for: "Ads attribution",
    },
    utm_source: { proposed_api_name: "UTM_Source", purpose: "UTM", required_for: "campaign reporting" },
    utm_medium: { proposed_api_name: "UTM_Medium", purpose: "UTM", required_for: "campaign reporting" },
    utm_campaign: {
      proposed_api_name: "UTM_Campaign",
      purpose: "UTM",
      required_for: "campaign reporting",
    },
    utm_term: { proposed_api_name: "UTM_Term", purpose: "UTM", required_for: "campaign reporting" },
    utm_content: {
      proposed_api_name: "UTM_Content",
      purpose: "UTM",
      required_for: "campaign reporting",
    },
    market: { proposed_api_name: "VC_Market", purpose: "us|au", required_for: "routing" },
    category: { proposed_api_name: "VC_Category", purpose: "role category", required_for: "reporting" },
    variant: { proposed_api_name: "VC_Variant", purpose: "LP variant", required_for: "A/B" },
    lp_version: { proposed_api_name: "VC_LP_Version", purpose: "package version", required_for: "QA" },
    landing_page_url: {
      proposed_api_name: "VC_Landing_Page_URL",
      purpose: "landing URL",
      required_for: "attribution",
    },
    referrer: { proposed_api_name: "VC_Referrer", purpose: "referrer", required_for: "attribution" },
    company_size: {
      proposed_api_name: "VC_Company_Size",
      purpose: "employer headcount band",
      required_for: "lead value / qualification",
    },
    positions_needed: {
      proposed_api_name: "VC_Positions_Needed",
      purpose: "seats requested",
      required_for: "lead value / qualification",
    },
    hiring_timeline: {
      proposed_api_name: "VC_Hiring_Timeline",
      purpose: "urgency band",
      required_for: "lead value / qualification",
    },
    lead_score: {
      proposed_api_name: "VC_Lead_Score",
      purpose: "website modeled score 0–100",
      required_for: "history — CRM qualification supersedes",
    },
    estimated_lead_value: {
      proposed_api_name: "VC_Estimated_Lead_Value",
      purpose: "website modeled $ (not revenue, not Ads bidding)",
      required_for: "history — CRM value supersedes",
    },
  };

  const out: FieldProposal[] = [];
  for (const key of omittedLogical) {
    if (catalog[key]) out.push(catalog[key]);
  }
  return out;
}

/**
 * Docs-only: `--apply-schema` field creation requires explicit George approval.
 * This helper never calls Zoho; it only formats a proposal list.
 */
export function formatSchemaApplyProposal(proposals: FieldProposal[]): string {
  if (!proposals.length) return "No missing-field proposals.";
  const lines = [
    "SCHEMA APPLY PROPOSAL (requires George approval; do not auto-create)",
    "Flag reference only: --apply-schema",
    ...proposals.map(
      (p) => `- ${p.proposed_api_name}: ${p.purpose} (${p.required_for})`,
    ),
  ];
  return lines.join("\n");
}
