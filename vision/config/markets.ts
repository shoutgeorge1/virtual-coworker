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
    prop: "Virtual Coworker recruits, vets, and manages offshore teammates so you can hire with a clear employer path — not a freelance marketplace.",
    staffingExplain:
      "You tell us the role. We shortlist screened talent, you interview, and we handle payroll and account management once you hire.",
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
    prop: "Virtual Coworker is a staffing partner for Australian employers who want vetted offshore teammates with clear ownership — not gig-platform churn.",
    staffingExplain:
      "You brief the role. We recruit and screen. You choose who to hire. We manage the employment ops so your business stays the client.",
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

export function resolveCareersUrl(): string {
  const configured = (process.env.NEXT_PUBLIC_CAREERS_URL || "").trim();
  if (configured) return configured;
  // Explicit blocker path — /ph is a local concept page, not a live careers proof
  return MARKETS.us.careersUrlFallback;
}

/** True when careers URL is still the local fallback (blocker for paid launch). */
export function careersUrlIsBlocker(): boolean {
  return !(process.env.NEXT_PUBLIC_CAREERS_URL || "").trim();
}

export const PILOT = {
  channel: "Google Search",
  objective:
    "Can Google Search generate qualified US and Australian employer inquiries at an acceptable cost?",
  primaryContact: "Braden",
  gateVariant: "inline",
  lpVersion: "stage1-v5",
} as const;
