/**
 * Market-specific pilot content.
 * Placeholders stay marked until Virtual Coworker confirms real values.
 * Do not invent emails, phones, budgets, or conversion IDs.
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
    phoneDisplayPlaceholder: "[US_PHONE]",
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
      "virtual assistant philippines cost",
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
      "OnlineJobs.ph",
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
    phoneDisplayPlaceholder: "[AU_PHONE]",
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
      "philippines virtual assistant cost",
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
      "OnlineJobs.ph",
    ],
  },
};

export const PILOT = {
  fee: "$3,000",
  channel: "Google Search",
  objective:
    "Can Google Search generate qualified US and Australian employer leads at an acceptable cost?",
  primaryContact: "Braden",
} as const;
