/**
 * Market-specific Stage 1 config.
 * US phone: (310) 730-9126 - George 2026-08-10 (888 paused; 964 is WP landmine).
 * AU phone: 1300 886 740 — George-approved (2026-08-08); GBP listing.
 * Phone stays secondary to Start Hiring / Have a chat. Do not invent numbers.
 * Do not invent emails, budgets, conversion IDs, or guarantees.
 */

import { allFormRoleLabels } from "./categories";

export type MarketId = "us" | "au";

export type MarketConfig = {
  id: MarketId;
  label: string;
  country: string;
  currencyHint: string;
  landingPath: string;
  leadEmailEnv: "LEAD_EMAIL_US" | "LEAD_EMAIL_AU";
  phoneEnv: "NEXT_PUBLIC_US_PHONE" | "NEXT_PUBLIC_AU_PHONE";
  /**
   * Known public business line when env empty.
   * US / AU: George-approved public lines. Phone stays secondary to Start Hiring.
   */
  knownPhone: string | null;
  careersUrlEnv: "NEXT_PUBLIC_CAREERS_URL";
  careersUrlFallback: string;
  headline: string;
  prop: string;
  staffingExplain: string;
  servicesProposed: string[];
  keywordThemes: string[];
  negativeThemes: string[];
};

/** Verified public PH careers WordPress host (job-seeker exit only). */
export const DEFAULT_CAREERS_URL = "https://virtualcoworker.com.ph";

export const MARKETS: Record<MarketId, MarketConfig> = {
  us: {
    id: "us",
    label: "United States",
    country: "United States",
    currencyHint: "USD",
    landingPath: "/us",
    leadEmailEnv: "LEAD_EMAIL_US",
    phoneEnv: "NEXT_PUBLIC_US_PHONE",
    knownPhone: "(310) 730-9126",
    careersUrlEnv: "NEXT_PUBLIC_CAREERS_URL",
    careersUrlFallback: DEFAULT_CAREERS_URL,
    headline:
      "Your week is full. Hire a dedicated Filipino teammate.",
    prop: "We recruit and screen. You interview and pick. We handle payroll. Dedicated seats on your hours — not a gig marketplace.",
    staffingExplain:
      "Tell us the role. Free consult — no pressure. We recruit and shortlist. You interview and pick. We handle payroll and paperwork. Rates depend on the seat — we’ll talk through them once we understand what you need.",
    servicesProposed: allFormRoleLabels(),
    keywordThemes: [
      "remote staffing agency",
      "virtual assistant agency",
      "hire virtual staff",
      "philippines staffing agency",
      "hire filipino virtual assistant",
      "virtual assistant company",
    ],
    negativeThemes: [
      "job",
      "jobs",
      "salary",
      "career",
      "careers",
      "apply",
      "resume",
      "training",
      "work from home",
      "free",
    ],
  },
  au: {
    id: "au",
    label: "Australia",
    country: "Australia",
    currencyHint: "AUD",
    landingPath: "/au",
    leadEmailEnv: "LEAD_EMAIL_AU",
    phoneEnv: "NEXT_PUBLIC_AU_PHONE",
    knownPhone: "1300 886 740",
    careersUrlEnv: "NEXT_PUBLIC_CAREERS_URL",
    careersUrlFallback: DEFAULT_CAREERS_URL,
    headline:
      "Your week is full. A dedicated Filipino teammate takes the load.",
    prop: "We recruit and shortlist. You interview and choose. We handle employment admin. Dedicated teammates on Australian hours — not a gig marketplace.",
    staffingExplain:
      "Tell us the role. We’ll have a short chat — free, no pressure. We recruit and shortlist. You interview and pick. We handle employment admin so you stay on the work. Rates depend on the role — we’ll talk them through once we understand what you need.",
    servicesProposed: allFormRoleLabels(),
    keywordThemes: [
      "hire virtual assistant philippines",
      "hire filipino virtual assistant",
      "virtual assistant for business",
      "hiring a virtual assistant",
      "virtual assistant company",
    ],
    negativeThemes: [
      "job",
      "jobs",
      "salary",
      "career",
      "careers",
      "apply",
      "resume",
      "training",
      "work from home",
      "free",
    ],
  },
};

/** Build a dialable tel: href. AU 13/1300/1800 → +61; US keeps national digits. */
export function phoneTelHref(display: string, market: MarketId): string {
  const trimmed = display.trim();
  if (!trimmed) return "";
  const hasPlus = trimmed.includes("+");
  const digits = trimmed.replace(/\D/g, "");
  if (!digits) return "";
  if (hasPlus) return `tel:+${digits}`;
  if (market === "au") {
    // National 13/1300/1800 stay as +61 + full national number (keep leading 1).
    if (/^(1300|1800|13)\d+$/.test(digits)) return `tel:+61${digits}`;
    // Other AU numbers: drop leading 0 for E.164 if present.
    const national = digits.startsWith("0") ? digits.slice(1) : digits;
    return `tel:+61${national}`;
  }
  return `tel:${digits}`;
}

export function resolvePhone(market: MarketId): {
  display: string;
  href: string | null;
  configured: boolean;
} {
  const cfg = MARKETS[market];
  const raw =
    market === "us"
      ? process.env.NEXT_PUBLIC_US_PHONE
      : process.env.NEXT_PUBLIC_AU_PHONE;
  const value = (raw || "").trim() || cfg.knownPhone || "";
  if (!value) {
    return { display: "", href: null, configured: false };
  }
  const href = phoneTelHref(value, market);
  return {
    display: value,
    href: href || null,
    configured: Boolean(href),
  };
}

/** Employer WordPress hosts — never use these as the job-seeker careers exit. */
const EMPLOYER_WP_HOST_RE =
  /^https?:\/\/(www\.)?virtualcoworker\.com(\.au)?(\/|$)/i;

/** Philippines careers WordPress (allowed job-seeker egress). */
const PH_CAREERS_HOST_RE =
  /^https?:\/\/(www\.)?virtualcoworker\.com\.ph(\/|$)/i;

export function isPhCareersUrl(url: string): boolean {
  return PH_CAREERS_HOST_RE.test((url || "").trim());
}

export function isExternalCareersUrl(url: string): boolean {
  const u = (url || "").trim();
  return /^https?:\/\//i.test(u);
}

/**
 * Job-seeker exit → WordPress Philippines careers (leave paid employer funnel).
 * Default: https://virtualcoworker.com.ph
 * Rejects US/AU WordPress employer hosts; allows .ph or same-host relative paths.
 */
export function resolveCareersUrl(): string {
  const configured = (process.env.NEXT_PUBLIC_CAREERS_URL || "").trim();
  if (configured) {
    if (EMPLOYER_WP_HOST_RE.test(configured) && !isPhCareersUrl(configured)) {
      console.error(
        "[careers] NEXT_PUBLIC_CAREERS_URL points at employer WordPress — falling back to PH careers",
      );
      return DEFAULT_CAREERS_URL;
    }
    return configured;
  }
  return DEFAULT_CAREERS_URL;
}

/** True when careers env was set to an employer WordPress host (misconfig). */
export function careersUrlIsBlocker(): boolean {
  const configured = (process.env.NEXT_PUBLIC_CAREERS_URL || "").trim();
  return Boolean(
    configured &&
      EMPLOYER_WP_HOST_RE.test(configured) &&
      !isPhCareersUrl(configured),
  );
}

export const PILOT = {
  channel: "Google Search",
  objective:
    "Can Google Search generate qualified US and Australian employer inquiries at an acceptable cost?",
  primaryContact: "Braden",
  gateVariant: "inline",
  lpVersion: "stage1-v9",
} as const;
