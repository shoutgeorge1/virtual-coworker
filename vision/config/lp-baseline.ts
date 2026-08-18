/**
 * Paid Landing Page Baseline v1 — August 2026
 *
 * Evidence-informed production baseline (not an A/B “winner”).
 * Hybrid: approved price-led hero + Tell Us Who You Need quiz + phone closer,
 * with live /us image bands and section rhythm (logos, how, roles, why+photo,
 * team, stories, quiz, closer).
 *
 * Do not invent prices, savings, or speed claims. US rates only when published.
 * AU: no unverified dollar amount in H1.
 */

import type { MarketId } from "./markets";
import {
  CATEGORIES,
  CATEGORY_SLUGS,
  type CategorySlug,
} from "./categories";
import {
  JOB_SEEKER_LINE,
  marketLandingCopy,
} from "./guided-match";
import {
  COMPANY_IDENTITY,
  PUBLIC_QUOTES,
  SITE,
  TRUST_PROOF,
  googleBusinessForMarket,
} from "./site";

/** Label for ops / deploy notes. Not Ads Primary. */
export const BASELINE_LABEL =
  "Paid Landing Page Baseline v1 - August 2026" as const;

export const BASELINE_LP_VERSION = "baseline_v1_2026_08" as const;
/** Visual lineage from the approved staffing-partner challenger. */
export const BASELINE_LP_VARIANT = "price_staffing_v1" as const;

export type BaselineIntentCluster = "core" | CategorySlug;

export type BaselineRoleCard = { title: string; body: string };
export type BaselineStep = { k: string; t: string; d: string };
export type BaselineWhyItem = { title: string; body: string };

/** Published US starting rates only. Omit when role mixes rates or unverified. */
export const US_PUBLISHED_RATES: Partial<
  Record<CategorySlug, { noun: string; rateHour: number } | { noun: string; rateHour: null }>
> = {
  "digital-marketing": { noun: "Digital Marketing Manager", rateHour: 12 },
  "social-media": { noun: "Social Media Manager", rateHour: 8 },
  accounting: { noun: "Accountant", rateHour: 10 },
  bookkeeping: { noun: "Bookkeeper", rateHour: 8 },
  // VA $7 + EA $10 on same route — no single H1 rate.
  "administrative-support": { noun: "Administrative Support", rateHour: null },
  "customer-service": { noun: "Customer Support", rateHour: 7 },
  hr: { noun: "HR Support", rateHour: null },
  recruitment: { noun: "Recruitment Assistant", rateHour: 9 },
  // Sales mixes setter / support / lead-gen — omit single rate.
  sales: { noun: "Sales Support", rateHour: null },
};

export type BaselineRouteConfig = {
  market: MarketId;
  route: string;
  intent_cluster: BaselineIntentCluster;
  role: CategorySlug | null;
  eyebrow: string;
  h1: string;
  supporting_copy: string;
  proof_items: readonly string[];
  role_tasks: readonly BaselineRoleCard[];
  rate_text: string;
  hero_image: string;
  hero_alt: string;
  phone_display: string;
  phone_href: string;
  phone_short: string;
  form_role: string;
  lp_version: typeof BASELINE_LP_VERSION;
  lp_variant: typeof BASELINE_LP_VARIANT;
};

function softHour(rate: number): string {
  // Soft wrap after "/" so mobile does not clip "$N/Hour"
  return `$${rate}/\u200bHour`;
}

function coreH1(market: MarketId): string {
  if (market === "us") {
    return `Hire Dedicated Filipino Remote Staff From ${softHour(7)}`;
  }
  return "Hire Dedicated Filipino Remote Staff";
}

function roleH1(market: MarketId, slug: CategorySlug): string {
  const meta = US_PUBLISHED_RATES[slug];
  const noun = meta?.noun || CATEGORIES[slug].label;
  if (market === "us" && meta && meta.rateHour != null) {
    return `Hire a Dedicated Filipino ${noun} From ${softHour(meta.rateHour)}`;
  }
  return `Hire a Dedicated Filipino ${noun}`;
}

function rateText(market: MarketId, slug: CategorySlug | null): string {
  if (market !== "us" || !slug) {
    if (market === "us" && !slug) return "From $7/hour";
    return "";
  }
  const meta = US_PUBLISHED_RATES[slug];
  if (!meta || meta.rateHour == null) return "";
  return `From $${meta.rateHour}/hour`;
}

function coreRoleCards(market: MarketId): BaselineRoleCard[] {
  const hours = market === "au" ? "Australian hours" : "your hours";
  return [
    {
      title: "Administration",
      body: `Inbox, calendar, documents, and follow-up owned by one person on ${hours}.`,
    },
    {
      title: "Bookkeeping",
      body: "Invoices, reconciliations, and routine reporting.",
    },
    {
      title: "Marketing",
      body: "Content, campaigns, posting, and reporting support.",
    },
    {
      title: "Customer support",
      body: "Tickets, chat, and customer follow-through.",
    },
    {
      title: "Sales support",
      body: "Lists, outreach support, and CRM hygiene.",
    },
    {
      title: "HR / recruiting",
      body: "Sourcing support, scheduling, and people admin.",
    },
  ];
}

function roleTaskCards(slug: CategorySlug): BaselineRoleCard[] {
  return CATEGORIES[slug].benefits.slice(0, 4).map((body, i) => ({
    title: ["Day-to-day ownership", "Dedicated seat", "Your team", "You decide"][i] || `Task ${i + 1}`,
    body,
  }));
}

function supportingCopy(market: MarketId, slug: CategorySlug | null): string {
  if (slug) {
    const label = (US_PUBLISHED_RATES[slug]?.noun || CATEGORIES[slug].label).toLowerCase();
    return `We recruit and vet for your ${label} seat. You interview the shortlist and choose who joins. Full-time or part-time, on your time zone.`;
  }
  return "We recruit and vet experienced candidates for your role. You interview the shortlist and choose who joins. Full-time or part-time, on your time zone.";
}

export function baselineHowSteps(market: MarketId): BaselineStep[] {
  const admin = market === "au" ? "employment admin" : "payroll and HR";
  return [
    {
      k: "1",
      t: "Tell us the role",
      d: "Work, hours, and how many people you need.",
    },
    {
      k: "2",
      t: "We recruit and vet",
      d: "Philippines team sources and screens for your brief.",
    },
    {
      k: "3",
      t: "You interview and select",
      d: "Meet finalists on video. Nobody starts without your yes.",
    },
    {
      k: "4",
      t: "We stay on the account",
      d: `Onboarding, ${admin}, and the time tracker after you hire.`,
    },
  ];
}

export function baselineWhyItems(market: MarketId): BaselineWhyItem[] {
  const hours =
    market === "au" ? "Australian business hours" : "US business hours";
  const admin = market === "au" ? "employment admin" : "payroll and HR";
  return [
    {
      title: `Since ${TRUST_PROOF.sinceYear}`,
      body: "Staffing partner. US and Australian offices. Philippines recruitment hub.",
    },
    {
      title: "Your hours",
      body: `Dedicated staff for ${hours}. Full-time or part-time. 20 hours/week minimum.`,
    },
    {
      title: "You choose",
      body: "You interview on video. Nobody is assigned without your yes.",
    },
    {
      title: "We employ",
      body: `After you hire, we handle ${admin} and stay on the account.`,
    },
  ];
}

export function buildBaselineRoute(opts: {
  market: MarketId;
  role?: CategorySlug | null;
}): BaselineRouteConfig {
  const market = opts.market;
  const role = opts.role || null;
  const base = marketLandingCopy(market);
  const path = role ? `/${market}/${role}` : `/${market}`;

  return {
    market,
    route: path,
    intent_cluster: role || "core",
    role,
    eyebrow: "Dedicated Filipino Remote Staff",
    h1: role ? roleH1(market, role) : coreH1(market),
    supporting_copy: supportingCopy(market, role),
    proof_items: [
      `Since ${TRUST_PROOF.sinceYear}`,
      "No Recruitment Fees",
      "20–40 Hours Per Week",
    ],
    role_tasks: role ? roleTaskCards(role) : coreRoleCards(market),
    rate_text: rateText(market, role),
    hero_image: base.heroSrc,
    hero_alt: base.heroAlt,
    phone_display: base.phoneDisplay,
    phone_href: base.phoneHref,
    phone_short: market === "au" ? "1300 886 740" : "888-964-8644",
    form_role: role ? CATEGORIES[role].formLabel : "",
    lp_version: BASELINE_LP_VERSION,
    lp_variant: BASELINE_LP_VARIANT,
  };
}

export function baselineSharedCopy(market: MarketId) {
  const base = marketLandingCopy(market);
  const google = googleBusinessForMarket(market);
  return {
    primaryCta: "Tell Us Who You Need",
    howEyebrow: "How hiring works",
    howTitle: "Tell us the role. We recruit. You interview.",
    howLead:
      market === "au"
        ? "Staffing partner for Australian hours. You choose who joins."
        : "Staffing partner model. You choose who joins.",
    rolesEyebrow: "Roles we hire for",
    rolesTitle: "Dedicated staff for work you already need",
    rolesLead: "Dedicated staff, not a rotating freelance pool.",
    whyEyebrow: "Why companies stay",
    whyTitle: "Why companies stay",
    teamTitle: "The team that recruits your hire",
    teamLead: "Philippines recruitment floor. US and Australian offices behind the account.",
    storiesTitle: "What employers say",
    gateEyebrow: "Employers",
    gateTitle: "Tell Us Who You Need",
    gateLead:
      "Answer three quick questions so our staffing team can prepare the right shortlist. About one minute.",
    finalTitle: "Prefer to Talk It Through?",
    finalLead: "Call our staffing team about the role, schedule, and experience you need.",
    finalPhoneCta: `Call ${base.phoneDisplay}`,
    googleLine: `${google.rating} Google · ${google.reviewCount} reviews`,
    clutchLine: `${TRUST_PROOF.clutch.rating} Clutch · ${TRUST_PROOF.clutch.reviewCount} reviews`,
    entity: base.entity,
    nap: base.nap,
    sinceYear: base.sinceYear,
    linkedin: base.linkedin,
    adminLabel: base.adminLabel,
    sceneSrc: base.sceneSrc,
    sceneAlt: base.sceneAlt,
    teamSrc: base.teamSrc,
    teamAlt: base.teamAlt,
    closerSrc: base.closerSrc,
    closerAlt: base.closerAlt,
    seekerLine: JOB_SEEKER_LINE,
    steps: baselineHowSteps(market),
    whyItems: baselineWhyItems(market),
  };
}

export function baselineQuotes(role?: CategorySlug | null) {
  const quotes = PUBLIC_QUOTES.map((q) => ({
    text: q.quote,
    by: `${q.name} · ${q.role}${q.company ? ` · ${q.company}` : ""}`,
    company: q.company,
  }));
  let featIdx = 0;
  if (role === "bookkeeping" || role === "accounting") {
    const i = quotes.findIndex((q) => q.company === "Credit Card Compare");
    if (i >= 0) featIdx = i;
  }
  const featured = quotes[featIdx];
  const rest = quotes.filter((_, i) => i !== featIdx);
  return { featured, rest };
}

export function allBaselineRoleSlugs(): readonly CategorySlug[] {
  return CATEGORY_SLUGS;
}

export function baselineTrackingExtras(cfg: BaselineRouteConfig) {
  return {
    lp_version: cfg.lp_version,
    lp_variant: cfg.lp_variant,
    lp_market: cfg.market,
    lp_route: cfg.route,
    lp_role: cfg.role || "",
    lp_intent_cluster: cfg.intent_cluster,
  };
}

/** Alias paths retired from Ads conceptually; preserve as redirects to market home. */
export const BASELINE_HOME_ALIASES = [
  "start",
  "offer",
  "proof",
  "consult",
  "capacity",
  "time",
  "teammate",
] as const;

export { COMPANY_IDENTITY, SITE, TRUST_PROOF };
