/**
 * Shared paid LP config for the guided-match employer surfaces.
 * Visual + copy direction: ads-launch/mocks/paid-lp-replacements-2026-08-16
 * after George’s 16 Aug production UI corrections.
 *
 * Do not put internal QA/PPC language here. Do not invent prices, rankings,
 * or photos-as-staff. Market facts come from site.ts / TRUST_PROOF.
 */

import type { MarketId } from "./markets";
import {
  CATEGORIES,
  type CategorySlug,
  formLabelForSlug,
} from "./categories";
import {
  REAL_ESTATE_CHIP,
  REAL_ESTATE_FORM_LABEL,
  REAL_ESTATE_SLUG,
} from "./lp-real-estate";
import {
  COMPANY_IDENTITY,
  PUBLIC_QUOTES,
  SITE,
  TRUST_PROOF,
  googleBusinessForMarket,
} from "./site";

export const GUIDED_MATCH_LP_SURFACE = "form" as const;
export const GUIDED_MATCH_CTA_MODE = "form_primary" as const;
export const GUIDED_MATCH_LANDING_TYPE = "form_lp" as const;

export type GuidedMatchRoleId =
  | "administrative-support"
  | "bookkeeping"
  | "digital-marketing"
  | "customer-service"
  | "sales"
  | "recruitment"
  | "other";

export type GuidedMatchRole = {
  id: GuidedMatchRoleId;
  chip: string;
  formLabel: string;
  category: CategorySlug | "";
  blurb: string;
};

/** Core chooser - includes Other / Not sure. Role pages skip this list. */
export const GUIDED_MATCH_ROLES: readonly GuidedMatchRole[] = [
  {
    id: "administrative-support",
    chip: "Admin / EA",
    formLabel: "Administrative / virtual assistant",
    category: "administrative-support",
    blurb: "Inbox, calendar, documents, follow-up.",
  },
  {
    id: "bookkeeping",
    chip: "Bookkeeping",
    formLabel: "Bookkeeping support",
    category: "bookkeeping",
    blurb: "Invoices, reconciliations, routine reporting.",
  },
  {
    id: "digital-marketing",
    chip: "Marketing / Social",
    formLabel: "Digital marketing support",
    category: "digital-marketing",
    blurb: "Content, campaigns, posting, reporting.",
  },
  {
    id: "customer-service",
    chip: "Customer Support",
    formLabel: "Customer service support",
    category: "customer-service",
    blurb: "Tickets, chat, and customer follow-through.",
  },
  {
    id: "sales",
    chip: "Sales",
    formLabel: "Sales support",
    category: "sales",
    blurb: "Lists, outreach support, CRM hygiene.",
  },
  {
    id: "recruitment",
    chip: "Recruiting / HR",
    formLabel: "Recruitment support",
    category: "recruitment",
    blurb: "Sourcing support, scheduling, people admin.",
  },
  {
    id: "other",
    chip: "Other / Not sure",
    formLabel: "Other / not sure",
    category: "",
    blurb: "Describe the help you need and we will match the role.",
  },
] as const;

export const GUIDED_MATCH_SCHEDULES = [
  { id: "full-time" as const, label: "Full-time" },
  { id: "part-time" as const, label: "Part-time" },
  { id: "mix" as const, label: "Not sure / mix" },
];

/** Shown next to FT / PT / mix. Cheyenne 2026-08-17. */
export const GUIDED_MATCH_HOURS_MINIMUM_NOTE = "20 hours/week minimum.";

export const GUIDED_MATCH_POSITIONS = [
  { id: "1" as const, label: "1 person" },
  { id: "2-3" as const, label: "2-3 people" },
  { id: "4-10" as const, label: "4-10 people" },
  { id: "11+" as const, label: "11+" },
];

export const GUIDED_MATCH_SIZES = [
  { id: "1-10" as const, label: "1-10" },
  { id: "11-50" as const, label: "11-50" },
  { id: "51-200" as const, label: "51-200" },
  { id: "201+" as const, label: "201+" },
];

export function hoursDefaultForMarket(market: MarketId): string {
  return market === "au" ? "AU business hours" : "US business hours";
}

export function roleForCategory(slug: CategorySlug | typeof REAL_ESTATE_SLUG): {
  formLabel: string;
  chip: string;
  category: CategorySlug | typeof REAL_ESTATE_SLUG;
} {
  if (slug === REAL_ESTATE_SLUG) {
    return {
      formLabel: REAL_ESTATE_FORM_LABEL,
      chip: REAL_ESTATE_CHIP,
      category: REAL_ESTATE_SLUG,
    };
  }
  const fromChooser = GUIDED_MATCH_ROLES.find((r) => r.category === slug);
  if (fromChooser) {
    return {
      formLabel: fromChooser.formLabel,
      chip: fromChooser.chip,
      category: slug,
    };
  }
  return {
    formLabel: formLabelForSlug(slug),
    chip: CATEGORIES[slug].label,
    category: slug,
  };
}

export function roleByChip(chip: string): GuidedMatchRole | undefined {
  return GUIDED_MATCH_ROLES.find((r) => r.chip === chip);
}

export type GuidedMatchStep =
  | "role"
  | "needs"
  | "hours"
  | "people"
  | "size"
  | "contact";

export function firstGuidedMatchStep(
  lockedCategory?: CategorySlug | typeof REAL_ESTATE_SLUG | null,
  sequentialNeeds = false,
): GuidedMatchStep {
  if (lockedCategory) return sequentialNeeds ? "hours" : "needs";
  return "role";
}

export function buildHiringMessage(opts: {
  hoursDefault: string;
  timezoneNote?: string;
}): string {
  const lines = [`Hours requested: ${opts.hoursDefault}`];
  const note = (opts.timezoneNote || "").trim();
  if (note) lines.push(`Time zone notes: ${note}`);
  return lines.join("\n");
}

export function marketLandingCopy(market: MarketId) {
  const au = market === "au";
  const google = googleBusinessForMarket(market);
  return {
    market,
    au,
    phoneDisplay: au ? SITE.auPhoneDisplay : SITE.usPhoneDisplay,
    phoneHref: au ? SITE.auPhoneHref : SITE.usPhoneHref,
    googleLine: `${google.rating} Google · ${google.reviewCount} reviews`,
    clutchLine: `${TRUST_PROOF.clutch.rating} Clutch · ${TRUST_PROOF.clutch.reviewCount} reviews`,
    entity: au
      ? `${COMPANY_IDENTITY.entityAu} · ABN ${COMPANY_IDENTITY.abn}`
      : COMPANY_IDENTITY.entityUs,
    nap: au
      ? `AU office · ${SITE.addressAu} · ABN ${COMPANY_IDENTITY.abn}`
      : `US office · ${SITE.addressUs}`,
    hoursDefault: hoursDefaultForMarket(market),
    adminLabel: au ? "employment admin" : "payroll and HR",
    heroSrc: au ? "/brand/va-au.jpg" : "/brand/va-us.jpg",
    heroAlt: au
      ? "Filipino teammate at work for an Australian business"
      : "Filipino teammate at work for a US business",
    closerSrc: au ? "/brand/hero-au-2026.jpg" : "/brand/hero-us-2026.jpg",
    closerAlt: "Virtual Coworker office photograph",
    teamSrc: "/guided-match/trust-team-office.jpg",
    teamAlt: "Virtual Coworker recruitment team at work",
    sceneSrc: "/guided-match/trust-consult.jpg",
    sceneAlt: "Virtual Coworker consult in the office",
    h1Core: au
      ? "Hire reliable Filipino staff who work Australian hours."
      : "Hire reliable Filipino staff who work your hours.",
    leadCore: au
      ? "Tell us the role. We recruit, vet and introduce candidates you can interview."
      : "Tell us the role. We recruit, vet and introduce candidates you can interview.",
    hoursFaqQ: au
      ? "Can they work Australian hours?"
      : "Can they work US hours?",
    hoursFaqA: au
      ? "Yes. We recruit for Australian business hours. Hours are confirmed before recruiting starts."
      : "Yes. We recruit for US business hours. Hours are confirmed before recruiting starts.",
    payrollFaqQ: au ? "Do you handle employment admin?" : "Do you handle payroll?",
    payrollFaqA: au
      ? "Yes. Once you hire, we handle onboarding, employment admin, and the time tracker."
      : "Yes. Once you hire, we handle onboarding, payroll and HR, and the time tracker.",
    phonePlaceholder: au ? "0400 000 000" : "(201) 555-0123",
    sinceYear: TRUST_PROOF.sinceYear,
    linkedin: "450K+",
  };
}

export function roleHeadline(opts: {
  market: MarketId;
  lockedCategory?: CategorySlug | null;
}): { h1: string; lead: string } {
  const c = marketLandingCopy(opts.market);
  if (!opts.lockedCategory) {
    return { h1: c.h1Core, lead: c.leadCore };
  }
  const label = CATEGORIES[opts.lockedCategory].label.toLowerCase();
  if (opts.market === "au") {
    return {
      h1: `Hire ${label} staff who work Australian hours.`,
      lead: "Tell us the workload. We recruit, vet and introduce people you can interview.",
    };
  }
  return {
    h1: `Hire ${label} staff who work your hours.`,
    lead: "Tell us the workload. We recruit, vet and introduce people you can interview.",
  };
}

export const GUIDED_MATCH_QUOTES = PUBLIC_QUOTES.map((q) => ({
  text: q.quote,
  by: `${q.name} · ${q.role} · ${q.company}`,
  company: q.company,
}));

export function featuredQuoteIndex(lockedCategory?: CategorySlug | null): number {
  if (lockedCategory === "bookkeeping" || lockedCategory === "accounting") {
    return GUIDED_MATCH_QUOTES.findIndex((q) => q.company === "Credit Card Compare");
  }
  return 0;
}

export const GUIDED_MATCH_ASSETS = {
  logo: { src: "/brand/logo-vc.png", alt: "Virtual Coworker" },
  team: {
    src: "/guided-match/trust-team-office.jpg",
    source: "vision/public/trust/choices/trust-team-office.png",
    approved: true,
  },
  consult: {
    src: "/guided-match/trust-consult.jpg",
    source: "vision/public/trust/choices/trust-consult.png",
    approved: true,
  },
} as const;

export const JOB_SEEKER_LINE = "Looking for work? View careers in the Philippines →";
