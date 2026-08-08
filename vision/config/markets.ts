/**
 * Market-specific Stage 1 config.
 * US phone: (888) 954-8644 — aligned with ads Call asset (was 310 interim).
 * AU: no phone — form-primary; do not invent a placeholder tel: link.
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
   * US: brief-confirmed NA number. AU: null — form primary, no fake phone.
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
    knownPhone: "(888) 954-8644",
    careersUrlEnv: "NEXT_PUBLIC_CAREERS_URL",
    careersUrlFallback: DEFAULT_CAREERS_URL,
    headline:
      "Free your team from work that keeps slipping — with a dedicated Filipino coworker.",
    prop: "Recover time for customers and growth. Virtual Coworker matches Filipino professionals to your US role, you interview and choose, and we support payroll and employment admin after you hire. Dedicated staffing — not a freelance marketplace.",
    staffingExplain:
      "Tell us the role. We follow up for a short hiring conversation, take your brief, and shortlist screened Filipino talent. You interview and decide before anyone starts. We handle payroll and account support after you hire. Rates are discussed once we understand the seat — transparent for the role, not a one-size price tag.",
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
  au: {
    id: "au",
    label: "Australia",
    country: "Australia",
    currencyHint: "AUD",
    landingPath: "/au",
    leadEmailEnv: "LEAD_EMAIL_AU",
    phoneEnv: "NEXT_PUBLIC_AU_PHONE",
    knownPhone: null,
    careersUrlEnv: "NEXT_PUBLIC_CAREERS_URL",
    careersUrlFallback: DEFAULT_CAREERS_URL,
    headline:
      "Add dependable capacity for Australian business hours — without building another local department.",
    prop: "Hand off the work that keeps slipping to a dedicated Filipino teammate. We recruit and shortlist for your role, you interview and choose, and we support employment admin after you hire. Staffing for Australian businesses — not a gig marketplace.",
    staffingExplain:
      "Send the role you need filled. Our team follows up for a hiring conversation, takes your brief, and shortlists screened candidates. You interview before anyone starts. We handle employment admin so you stay focused on the work. Rates depend on the role and seniority — we’ll talk through them once we understand what you need.",
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
    // AU default: no phone UI — form primary
    return { display: "", href: null, configured: false };
  }
  const digits = value.replace(/[^\d+]/g, "");
  return {
    display: value,
    href: `tel:${digits}`,
    configured: true,
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
  lpVersion: "stage1-v8",
} as const;
