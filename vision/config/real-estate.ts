/**
 * US real-estate / property-management industry page.
 * Not a 10th paid category. Do not add to CATEGORY_SLUGS or AU routes.
 *
 * Supported seats only: Assistant Property Manager, Guest Relations,
 * Lead Generation (dedicated headcount), Bookkeeper, Executive Assistant.
 * Do not pitch generic Real Estate VA, ISA, or cold calling.
 */

import {
  BASELINE_LP_VARIANT,
  BASELINE_LP_VERSION,
  type BaselineRoleCard,
  type BaselineRouteConfig,
} from "./lp-baseline";
import { marketLandingCopy } from "./guided-match";
import { TRUST_PROOF } from "./site";

export const REAL_ESTATE_SLUG = "real-estate" as const;
export const REAL_ESTATE_PATH = "/us/real-estate" as const;
export const REAL_ESTATE_FORM_ROLE = "Real estate / property operations";

export const REAL_ESTATE_TITLE =
  "Hire Property and Real Estate Staff | Virtual Coworker US";

export const REAL_ESTATE_DESCRIPTION =
  "Hire dedicated Filipino staff for US property managers and real-estate operators. Assistant property managers, guest relations, lead generation, bookkeeping, and executive support. You interview. We handle payroll.";

export const REAL_ESTATE_H1 =
  "Hire Dedicated Filipino Property Staff Who Work Your Hours";

export const REAL_ESTATE_SUPPORTING =
  "Assistant property managers, guest relations, lead generation, bookkeeping, and executive support. Dedicated people who own the seat so you can stay on the work that makes money. You interview the shortlist. This is a staffing hire, not a cold-calling desk and not a lead-buying service.";

export const REAL_ESTATE_ROLES_HEADING =
  "What these property and real-estate seats cover";

export const REAL_ESTATE_ROLE_CARDS: readonly BaselineRoleCard[] = [
  {
    title: "Assistant Property Manager",
    body: "A dedicated person who owns day-to-day property operations so the manager is not the bottleneck.",
  },
  {
    title: "Guest Relations Specialist",
    body: "Guest messages, stays, and follow-through owned by one teammate, not a rotating freelancer.",
  },
  {
    title: "Lead Generation",
    body: "A dedicated lead-generation seat for follow-up and pipeline hygiene. Not pay-per-lead. Not a lead-buying platform.",
  },
  {
    title: "Bookkeeper",
    body: "Invoices, records, and reconciliations for the property or brokerage books.",
  },
  {
    title: "Executive Assistant",
    body: "Inbox, calendar, and coordination so owners and operators get time back.",
  },
];

export function buildRealEstateRoute(): BaselineRouteConfig {
  const base = marketLandingCopy("us");
  return {
    market: "us",
    route: REAL_ESTATE_PATH,
    intent_cluster: "real-estate",
    role: null,
    eyebrow: "Dedicated Filipino Remote Staff",
    h1: REAL_ESTATE_H1,
    supporting_copy: REAL_ESTATE_SUPPORTING,
    proof_items: [
      `Since ${TRUST_PROOF.sinceYear}`,
      "No Recruitment Fees",
      "20–40 Hours Per Week",
    ],
    role_tasks: REAL_ESTATE_ROLE_CARDS,
    rate_text: "",
    hero_image: base.heroSrc,
    hero_alt: base.heroAlt,
    phone_display: base.phoneDisplay,
    phone_href: base.phoneHref,
    phone_short: "888-964-8644",
    form_role: REAL_ESTATE_FORM_ROLE,
    lp_version: BASELINE_LP_VERSION,
    lp_variant: BASELINE_LP_VARIANT,
  };
}
