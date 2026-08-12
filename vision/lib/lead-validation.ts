/** Shared employer-lead validation (server + tests). No secrets. */

export const MIN_COMPLETION_MS = 2500;
export const DUPLICATE_WINDOW_MS = 10 * 60 * 1000;

export type LeadIntent = "employer" | "job_seeker" | "unknown";

export type LeadInput = {
  name?: string;
  email?: string;
  phone?: string;
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
  | { ok: true; intent: "employer"; market: "us" | "au"; email: string; name: string }
  | {
      ok: false;
      code:
        | "invalid_json"
        | "missing_fields"
        | "invalid_email"
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

  const name = String(raw.name || "").trim();
  const email = String(raw.email || "").trim().toLowerCase();
  const phone = String(raw.phone || "").trim();
  const company = String(raw.company || "").trim();

  if (!name || !email || !phone || !company) {
    return {
      ok: false,
      code: "missing_fields",
      reason: "name, work email, phone, and company are required",
    };
  }
  if (!EMAIL_RE.test(email)) {
    return { ok: false, code: "invalid_email", reason: "valid work email required" };
  }

  const started = Number(raw.form_started_at || 0);
  if (started > 0) {
    const elapsed = Date.now() - started;
    if (elapsed < MIN_COMPLETION_MS) {
      return { ok: false, code: "too_fast", reason: "form completed too quickly" };
    }
  }

  return { ok: true, intent: "employer", market, email, name };
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
