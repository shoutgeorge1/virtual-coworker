/**
 * US-only real-estate vertical LP. Clones the approved baseline layout.
 * Do not add this slug to CATEGORY_SLUGS (that would also create /au/real-estate).
 */

import type { MarketId } from "./markets";
import { SITE, TRUST_PROOF } from "./site";
import {
  BASELINE_LP_VARIANT,
  BASELINE_LP_VERSION,
  type BaselineRoleCard,
  type BaselineRouteConfig,
} from "./lp-baseline";

export const REAL_ESTATE_SLUG = "real-estate" as const;
export type RealEstateSlug = typeof REAL_ESTATE_SLUG;

export const REAL_ESTATE_CHIP = "Real estate";
export const REAL_ESTATE_FORM_LABEL = "Real estate support";

export const REAL_ESTATE_PATH = "/us/real-estate";
export const REAL_ESTATE_URL = `https://www.virtualcoworker.app${REAL_ESTATE_PATH}`;

export function isRealEstateSlug(value: string | null | undefined): value is RealEstateSlug {
  return value === REAL_ESTATE_SLUG;
}

function realEstateRoleCards(): BaselineRoleCard[] {
  return [
    {
      title: "Lead follow-up",
      body: "Call and email follow-up on inquiries so new leads do not sit untouched.",
    },
    {
      title: "CRM and lists",
      body: "Keep contacts, statuses, and next steps current in the system you already use.",
    },
    {
      title: "Listing and admin",
      body: "Inbox, calendar, documents, and listing paperwork owned by one dedicated person.",
    },
    {
      title: "Marketing support",
      body: "Content, posting, and campaign coordination for the team, not a freelance gig.",
    },
    {
      title: "Appointment setting",
      body: "Outreach and booking support so agents spend more time on conversations that close.",
    },
    {
      title: "Property management admin",
      body: "Tenant messages, lease files, and day-to-day admin for managers who need extra capacity.",
    },
  ];
}

export function buildRealEstateRoute(_market: MarketId = "us"): BaselineRouteConfig {
  return {
    market: "us",
    route: REAL_ESTATE_PATH,
    intent_cluster: "core",
    role: null,
    eyebrow: "Dedicated Filipino Remote Staff",
    h1: "Hire a Real Estate Virtual Assistant",
    supporting_copy:
      "For brokerages, teams, investors, and property managers. We recruit and vet dedicated Philippines staff who work your US hours. You interview the shortlist and choose who joins.",
    proof_items: [
      `Since ${TRUST_PROOF.sinceYear}`,
      "No Recruitment Fees",
      "20–40 Hours Per Week",
    ],
    role_tasks: realEstateRoleCards(),
    rate_text: "",
    hero_image: "/brand/va-us.jpg",
    hero_alt: "Filipino teammate at work for a US business",
    phone_display: SITE.usPhoneDisplay,
    phone_href: SITE.usPhoneHref,
    form_role: REAL_ESTATE_FORM_LABEL,
    lp_version: BASELINE_LP_VERSION,
    lp_variant: BASELINE_LP_VARIANT,
  };
}
