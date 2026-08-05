/**
 * Market-specific Stage 1 config.
 * Named placeholders until Virtual Coworker confirms real values.
 * Do not invent emails, phones, budgets, conversion IDs, or guarantees.
 */

export type MarketId = "us" | "au";

export type MarketConfig = {
  id: MarketId;
  label: string;
  country: string;
  currencyHint: string;
  landingPath: string;
  consultPath: string;
  leadEmailEnv: "LEAD_EMAIL_US" | "LEAD_EMAIL_AU";
  phoneEnv: "NEXT_PUBLIC_US_PHONE" | "NEXT_PUBLIC_AU_PHONE";
  /** Public display placeholders until env is set */
  phoneDisplayPlaceholder: string;
  phoneHrefPlaceholder: string;
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
    consultPath: "/us/consult",
    leadEmailEnv: "LEAD_EMAIL_US",
    phoneEnv: "NEXT_PUBLIC_US_PHONE",
    phoneDisplayPlaceholder: "[US_BUSINESS_PHONE]",
    phoneHrefPlaceholder: "tel:[US_BUSINESS_PHONE]",
    careersUrlEnv: "NEXT_PUBLIC_CAREERS_URL",
    careersUrlFallback: "/ph",
    headline: "Hire dedicated Philippines staff for your US business.",
    prop: "Virtual Coworker recruits, vets, and manages offshore teammates so you can hire with a clear employer path — not a freelance marketplace.",
    staffingExplain:
      "You tell us the role. We shortlist screened talent, you interview, and we handle payroll and account management once you hire.",
    servicesProposed: [
      "Dedicated VA hire",
      "Admin & inbox",
      "Customer support",
      "Sales / CRM",
      "Marketing support",
    ],
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
    consultPath: "/au/consult",
    leadEmailEnv: "LEAD_EMAIL_AU",
    phoneEnv: "NEXT_PUBLIC_AU_PHONE",
    phoneDisplayPlaceholder: "[AU_BUSINESS_PHONE]",
    phoneHrefPlaceholder: "tel:[AU_BUSINESS_PHONE]",
    careersUrlEnv: "NEXT_PUBLIC_CAREERS_URL",
    careersUrlFallback: "/ph",
    headline: "Hire dedicated Philippines staff for your Australian business.",
    prop: "Virtual Coworker is a staffing partner for Australian employers who want vetted offshore teammates with clear ownership — not gig-platform churn.",
    staffingExplain:
      "You brief the role. We recruit and screen. You choose who to hire. We manage the employment ops so your business stays the client.",
    servicesProposed: [
      "Dedicated VA hire",
      "Admin & inbox",
      "Customer support",
      "Sales / CRM",
      "Marketing support",
    ],
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
  const value = (raw || "").trim();
  if (!value) {
    return {
      display: cfg.phoneDisplayPlaceholder,
      href: null,
      configured: false,
    };
  }
  const digits = value.replace(/[^\d+]/g, "");
  return {
    display: value,
    href: `tel:${digits}`,
    configured: true,
  };
}

export function resolveCareersUrl(): string {
  return (process.env.NEXT_PUBLIC_CAREERS_URL || "").trim() || "/ph";
}

export const PILOT = {
  fee: "$3,000",
  channel: "Google Search",
  objective:
    "Can Google Search generate qualified US and Australian employer leads at an acceptable cost?",
  primaryContact: "Braden",
  gateVariant: "inline",
} as const;
