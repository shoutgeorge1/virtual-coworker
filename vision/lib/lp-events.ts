/**
 * Canonical US paid-LP analytics events.
 * One dataLayer event per action. No aliases. No PII.
 * GTM/GA4 must map these names — do not dual-fire gtag() from the app.
 */

import {
  AUTHORITATIVE_LP_VERSION,
  LANDING_PAGE_TYPES,
  US_BASELINE_LABEL,
  type LandingPageType,
} from "../config/lp-version";
import { trackEvent } from "./tracking";

export type LpEventBase = {
  market: string;
  lp_version?: string;
  page_path?: string;
  landing_page_type?: LandingPageType | string;
};

const LP_VIEW_FIRED = new Set<string>();
const FORM_START_FIRED = new Set<string>();
const STEP_FIRED = new Set<string>();
const SUBMIT_FIRED = new Set<string>();
const PHONE_CLICK_GUARD = new WeakSet<Event>();

function pagePath(explicit?: string): string {
  if (explicit) return explicit;
  if (typeof window === "undefined") return "";
  return window.location.pathname || "";
}

function lpVersion(explicit?: string): string {
  return explicit || AUTHORITATIVE_LP_VERSION;
}

function landingType(
  explicit?: string,
  fallback: LandingPageType = LANDING_PAGE_TYPES.employer_paid_lp,
): string {
  return explicit || fallback;
}

export function resetLpEventDedupeForTests() {
  LP_VIEW_FIRED.clear();
  FORM_START_FIRED.clear();
  STEP_FIRED.clear();
  SUBMIT_FIRED.clear();
}

export function trackLpView(opts: LpEventBase & {
  baseline_label?: string;
  experiment_id?: string;
  variant?: string;
  split_running?: boolean;
}) {
  const path = pagePath(opts.page_path);
  const version = lpVersion(opts.lp_version);
  const key = `${opts.market}|${path}|${version}`;
  if (LP_VIEW_FIRED.has(key)) return;
  LP_VIEW_FIRED.add(key);

  const payload: Record<string, string | number | boolean | undefined> = {
    market: opts.market,
    lp_version: version,
    baseline_label: opts.baseline_label || US_BASELINE_LABEL,
    page_path: path,
    landing_page_type: landingType(opts.landing_page_type),
  };
  if (opts.split_running && opts.experiment_id) {
    payload.experiment_id = opts.experiment_id;
    if (opts.variant) payload.variant = opts.variant;
  }
  trackEvent("lp_view", payload);
}

/** GA4 standard name. Once per guided-match session, not on page load. */
export function trackFormStart(opts: LpEventBase & {
  role_selected?: string;
  start_reason?: string;
}) {
  const path = pagePath(opts.page_path);
  const key = `${opts.market}|${path}`;
  if (FORM_START_FIRED.has(key)) return;
  FORM_START_FIRED.add(key);
  trackEvent("form_start", {
    market: opts.market,
    lp_version: lpVersion(opts.lp_version),
    page_path: path,
    landing_page_type: landingType(opts.landing_page_type),
    role_selected: opts.role_selected || "",
    start_reason: opts.start_reason || "guided_match_interaction",
  });
}

export function trackEmployerFormStepCompleted(opts: LpEventBase & {
  step_number: number;
  step_name: string;
  role_selected?: string;
}) {
  const path = pagePath(opts.page_path);
  const key = `${opts.market}|${path}|${opts.step_number}|${opts.step_name}`;
  if (STEP_FIRED.has(key)) return;
  STEP_FIRED.add(key);
  trackEvent("employer_form_step_completed", {
    market: opts.market,
    lp_version: lpVersion(opts.lp_version),
    page_path: path,
    landing_page_type: landingType(opts.landing_page_type),
    step_number: opts.step_number,
    step_name: opts.step_name,
    role_selected: opts.role_selected || "",
  });
}

export type FormValidationErrorCategory =
  | "invalid_us_phone"
  | "missing_required_field"
  | "job_seeker_intent"
  | "server_rejection";

export function trackFormValidationError(opts: LpEventBase & {
  error_category: FormValidationErrorCategory;
  form_step?: string;
  role_selected?: string;
}) {
  trackEvent("form_validation_error", {
    market: opts.market,
    lp_version: lpVersion(opts.lp_version),
    page_path: pagePath(opts.page_path),
    landing_page_type: landingType(opts.landing_page_type),
    error_category: opts.error_category,
    form_step: opts.form_step || "",
    role_selected: opts.role_selected || "",
  });
}

export function trackPhoneCtaClicked(opts: LpEventBase & {
  cta_location: string;
}) {
  trackEvent("phone_cta_clicked", {
    market: opts.market,
    lp_version: lpVersion(opts.lp_version),
    page_path: pagePath(opts.page_path),
    landing_page_type: landingType(opts.landing_page_type),
    cta_location: opts.cta_location,
    is_qualified_call: false,
  });
}

/** Guard duplicate click handlers on the same DOM event (capture + bubble). */
export function notePhoneClickEvent(ev: Event | undefined) {
  if (!ev) return false;
  if (PHONE_CLICK_GUARD.has(ev)) return true;
  PHONE_CLICK_GUARD.add(ev);
  return false;
}

export function trackJobSeekerRedirected(opts: LpEventBase & {
  redirect_location: string;
  redirect_reason: string;
  destination?: string;
}) {
  trackEvent("job_seeker_redirected", {
    market: opts.market,
    lp_version: lpVersion(opts.lp_version),
    page_path: pagePath(opts.page_path),
    landing_page_type: landingType(opts.landing_page_type),
    redirect_location: opts.redirect_location,
    redirect_reason: opts.redirect_reason,
    destination: opts.destination || "",
    intent: "job_seeker",
    primary_eligible: false,
    bidding_primary: false,
  });
}

export function shouldSkipDuplicateSubmit(submissionId: string): boolean {
  if (!submissionId) return true;
  if (SUBMIT_FIRED.has(submissionId)) return true;
  SUBMIT_FIRED.add(submissionId);
  return false;
}
