/**
 * Market-specific Stage 1 config.
 * US NA phone from operator brief: 310-426-8776.
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

export const MARKETS: Record<MarketId, MarketConfig> = {
  us: {
    id: "us",
    label: "United States",
    country: "United States",
    currencyHint: "USD",
    landingPath: "/us",
    leadEmailEnv: "LEAD_EMAIL_US",
    phoneEnv: "NEXT_PUBLIC_US_PHONE",
    knownPhone: "310-426-8776",
    careersUrlEnv: "NEXT_PUBLIC_CAREERS_URL",
    careersUrlFallback: "/ph",
    headline: "Hire dedicated Philippines staff for your US business.",
    prop: "Virtual Coworker is a staffing partner for US employers — we recruit and screen Philippines talent, you interview and choose, then we support the hire with payroll and account management.",
    staffingExplain:
      "Brief the seat you need filled. Get a shortlist of screened candidates. Interview on your terms. Hire with employment ops handled — so you stay the client, not a gig-platform customer.",
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
    careersUrlFallback: "/ph",
    headline: "Hire dedicated Philippines staff for your Australian business.",
    prop: "Virtual Coworker is a staffing partner for Australian employers who want vetted Philippines teammates with clear ownership — not gig-platform churn.",
    staffingExplain:
      "Brief the role. We recruit and screen in the Philippines. You interview and choose. We manage employment ops so your business stays the client.",
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

const WP_HOST_RE = /virtualcoworker\.com(\.au)?/i;

/**
 * Job-seeker exit stays inside the PH microsite.
 * Never return a WordPress careers URL — reject env misconfiguration.
 */
export function resolveCareersUrl(): string {
  const configured = (process.env.NEXT_PUBLIC_CAREERS_URL || "").trim();
  if (configured) {
    if (WP_HOST_RE.test(configured)) {
      console.error(
        "[careers] NEXT_PUBLIC_CAREERS_URL points at WordPress — falling back to /ph",
      );
      return MARKETS.us.careersUrlFallback;
    }
    return configured;
  }
  return MARKETS.us.careersUrlFallback;
}

/** True when careers env was set to a WordPress host (misconfig). /ph itself is valid. */
export function careersUrlIsBlocker(): boolean {
  const configured = (process.env.NEXT_PUBLIC_CAREERS_URL || "").trim();
  return Boolean(configured && WP_HOST_RE.test(configured));
}

export const PILOT = {
  channel: "Google Search",
  objective:
    "Can Google Search generate qualified US and Australian employer inquiries at an acceptable cost?",
  primaryContact: "Braden",
  gateVariant: "inline",
  lpVersion: "stage1-v7",
} as const;
