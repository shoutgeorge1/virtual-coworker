/**
 * Unused US staffing-agency candidate. Not an Ads Final URL.
 * Reuses StaffingBaselineLanding layout, form, validation, tracking, and proof.
 * Do not invent prices, customer counts, guarantees, or new testimonials.
 */

import { TRUST_PROOF } from "./site";
import { baselineWhyItems, type BaselineWhyItem } from "./lp-baseline";
import {
  STAFFING_AGENCY_CANDIDATE_LP_VERSION,
  STAFFING_AGENCY_CANDIDATE_PATH,
} from "./lp-version";

export const STAFFING_AGENCY_PATH = STAFFING_AGENCY_CANDIDATE_PATH;
export const STAFFING_AGENCY_LP_VERSION = STAFFING_AGENCY_CANDIDATE_LP_VERSION;

export function staffingAgencyCopy() {
  const whyItems: BaselineWhyItem[] = [
    {
      title: `Since ${TRUST_PROOF.sinceYear}`,
      body: "Virtual Coworker recruits and vets dedicated Philippines staff for US businesses.",
    },
    {
      title: "You interview and choose",
      body: "You meet finalists on video. Nobody joins your team without your yes.",
    },
    {
      title: "We employ them",
      body: "After you hire, Virtual Coworker employs the worker and handles payroll and HR support.",
    },
    {
      title: "Your US hours",
      body: "Staff work your US business hours. Full-time and eligible part-time. 20 hours/week minimum.",
    },
  ];
  return {
    path: STAFFING_AGENCY_PATH,
    lp_version: STAFFING_AGENCY_LP_VERSION,
    eyebrow: "Philippines remote staffing partner",
    h1: "Hire dedicated Filipino staff for your US hours",
    supporting_copy:
      "Virtual Coworker recruits and vets candidates. You interview and choose who joins. We employ them and handle payroll. This is dedicated staffing — not a gig marketplace and not a personal concierge service.",
    howEyebrow: "How this staffing partnership works",
    howTitle: "We recruit. You interview. We employ.",
    howLead:
      "Tell us the role. We source and screen. You choose. After you hire, we stay on payroll and HR. Minimum engagement is 20 hours per week.",
    gateLead:
      "Answer three quick questions so our staffing team can prepare the right shortlist. About one minute. Full-time or eligible part-time.",
    whyItems,
    baselineWhy: baselineWhyItems("us"),
  };
}
