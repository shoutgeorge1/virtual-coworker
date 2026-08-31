/**
 * Authoritative landing-page version stamp.
 *
 * One value. Pages, dataLayer events, lead POST, and the baseline registry
 * all import from here. Do not hard-code lp_version in Google Ads suffixes,
 * GTM, or individual components.
 *
 * Semantic ops label (US_BASELINE_2026-08-18) is not a replacement for
 * lp_version — it freezes the production experience for measurement.
 */

export const AUTHORITATIVE_LP_VERSION = "baseline_v1_2026_08" as const;

/** @deprecated Use AUTHORITATIVE_LP_VERSION. Kept as a documented alias only. */
export const LP_VERSION = AUTHORITATIVE_LP_VERSION;

/** Pre-baseline code stamp. Not the live paid LP. */
export const LEGACY_STAGE_LP_VERSION = "stage1-v8" as const;

/** Stale Ads Final URL suffix. Do not put this back on live campaigns. */
export const STALE_ADS_LP_VERSION = "stage1-v7" as const;

/** Ops freeze label for the US paid experience. */
export const US_BASELINE_LABEL = "US_BASELINE_2026-08-18" as const;

export const US_BASELINE_URL = "https://www.virtualcoworker.app/us" as const;

export const US_BASELINE_COMPONENT = "StaffingBaselineLanding+GuidedMatchGate" as const;

/** First date of the clean measurement window (America/Los_Angeles). */
export const CLEAN_MEASUREMENT_START = "2026-08-18" as const;

/** Unused staffing-agency candidate. Not an Ads Final URL. */
export const STAFFING_AGENCY_CANDIDATE_LP_VERSION =
  "staffing_agency_candidate_2026_08_18" as const;

export const STAFFING_AGENCY_CANDIDATE_PATH = "/us/staffing" as const;

export const LANDING_PAGE_TYPES = {
  employer_paid_lp: "employer_paid_lp",
  staffing_agency_candidate: "staffing_agency_candidate",
  quiz_lp: "quiz_lp",
} as const;

export type LandingPageType =
  (typeof LANDING_PAGE_TYPES)[keyof typeof LANDING_PAGE_TYPES];
