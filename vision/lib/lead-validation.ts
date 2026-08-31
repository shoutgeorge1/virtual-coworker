/** Shared employer-lead validation (server + tests). No secrets. */

import {
  PH_PHONE_CAREERS_MESSAGE,
  US_PHONE_ERROR,
  validateUsPhone,
} from "./phone-format";

export const MIN_COMPLETION_MS = 2500;
export const DUPLICATE_WINDOW_MS = 10 * 60 * 1000;

export type LeadIntent = "employer" | "job_seeker" | "unknown";

export type LeadInput = {
  name?: string;
  email?: string;
  phone?: string;
  /** Required for employer follow-up. Validated in validateEmployerLead. */
  company?: string;
  role?: string;
  category?: string;
  variant?: string;
  timeline?: string;
  message?: string;
  market?: string;
  intent?: string;
  /** Honeypot — must be empty */
  website?: string;
  company_url?: string;
  /** Optional visible company site. Not a honeypot. Never required. */
  company_website?: string;
  form_started_at?: number | string;
  submitted_at?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  gclid?: string;
  gbraid?: string;
  wbraid?: string;
  utm_matchtype?: string;
  utm_device?: string;
  session_id?: string;
  baseline_label?: string;
  landing_page_url?: string;
  referrer?: string;
  lp_version?: string;
  lp_variant?: string;
  captured_at?: string;
  /** Soft qualification chips on the employer form (optional). */
  company_size?: string;
  positions_needed?: string;
  schedule?: string;
  hiring_timeline?: string;
  lead_score?: number | string;
  estimated_lead_value?: number | string;
  value_kind?: string;
  lp_surface?: string;
};

export type ValidationResult =
  | {
      ok: true;
      intent: "employer";
      market: "us" | "au";
      email: string;
      name: string;
      phone: string;
    }
  | {
      ok: false;
      code:
        | "invalid_json"
        | "missing_fields"
        | "invalid_email"
        | "invalid_us_phone"
        | "honeypot"
        | "too_fast"
        | "job_seeker"
        | "invalid_market"
        | "invalid_intent";
      reason: string;
    };

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const JOB_SEEKER_HINTS =
  /\b(looking for a job|job seeker|apply for|my resume|cv attached|hiring me|i need a job|want a job)\b/i;

export function classifyIntent(raw: LeadInput): LeadIntent {
  const intent = String(raw.intent || "").trim().toLowerCase();
  if (intent === "employer" || intent === "hire" || intent === "hiring") return "employer";
  if (intent === "job_seeker" || intent === "job" || intent === "applicant") return "job_seeker";

  const blob = [raw.message, raw.role, raw.name].filter(Boolean).join(" ");
  if (JOB_SEEKER_HINTS.test(blob)) return "job_seeker";
  return "unknown";
}

export function validateEmployerLead(raw: LeadInput): ValidationResult {
  const market = String(raw.market || "").toLowerCase();
  if (market !== "us" && market !== "au") {
    return { ok: false, code: "invalid_market", reason: "market must be us|au" };
  }

  const intent = classifyIntent(raw);
  if (intent === "job_seeker") {
    return { ok: false, code: "job_seeker", reason: "job seeker path — not an employer lead" };
  }
  if (intent !== "employer") {
    return { ok: false, code: "invalid_intent", reason: "employer intent required" };
  }

  const honeypot = String(raw.website || raw.company_url || "").trim();
  if (honeypot) {
    return { ok: false, code: "honeypot", reason: "rejected" };
  }
  // company_website is a visible optional field — never treat as honeypot, never required.

  const name = String(raw.name || "").trim();
  const email = String(raw.email || "").trim().toLowerCase();
  const phone = String(raw.phone || "").trim();
  const company = String(raw.company || "").trim();
  // company_website stays optional. Company name is required for sales follow-up.

  if (!name || !email || !phone || !company) {
    return {
      ok: false,
      code: "missing_fields",
      reason: "name, company, work email, and phone are required",
    };
  }
  if (!EMAIL_RE.test(email)) {
    return { ok: false, code: "invalid_email", reason: "valid work email required" };
  }

  let storedPhone = phone;
  if (market === "us") {
    const usPhone = validateUsPhone(phone);
    if (!usPhone.ok) {
      if (usPhone.code === "ph_job_seeker_phone") {
        return { ok: false, code: "job_seeker", reason: PH_PHONE_CAREERS_MESSAGE };
      }
      return { ok: false, code: "invalid_us_phone", reason: US_PHONE_ERROR };
    }
    storedPhone = usPhone.e164;
  }

  const started = Number(raw.form_started_at || 0);
  if (started > 0) {
    const elapsed = Date.now() - started;
    if (elapsed < MIN_COMPLETION_MS) {
      return { ok: false, code: "too_fast", reason: "form completed too quickly" };
    }
  }

  return { ok: true, intent: "employer", market, email, name, phone: storedPhone };
}

/** Safe reject log — no PII / message body. */
export function rejectLogPayload(
  code: string,
  market: string,
  meta: Record<string, string | number | boolean | undefined> = {},
) {
  return {
    event: "spam_or_applicant_rejected",
    code,
    market,
    at: new Date().toISOString(),
    ...meta,
  };
}

export function duplicateKey(email: string, market: string): string {
  return `${market}:${email.trim().toLowerCase()}`;
}
