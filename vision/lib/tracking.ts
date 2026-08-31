/**
 * Client-side attribution + Stage 1 dataLayer helpers.
 * No hard-coded Ads conversion IDs. Map Ads goals in GTM / Ads UI.
 *
 * Conversion architecture (Aug 2026):
 * - Phone calls (duration-qualified, e.g. 60s+) = primary volume/quality steering signal
 * - Zoho "Qualified lead" offline import = deeper quality signal (then Job Order / Placement)
 * - Form submit = delivery / funnel observation only — NOT bidding Primary
 * - estimated_lead_value / lead_score = modeled site estimate only (not Ads conversion value yet)
 * - Do not over-optimize to raw form fills. Modeled $ is wired for analytics, not bidding.
 *
 * Canonical events (one dataLayer name each — no aliases):
 * - lp_view
 * - form_start
 * - employer_form_step_completed
 * - employer_inquiry_submitted  — delivery OK, not Ads Primary
 * - employer_inquiry_delivery_failed
 * - phone_cta_clicked           — click ≠ qualified call
 * - primary_cta_clicked
 * - calendly_cta_clicked
 * - calendly_embed_viewed
 * - calendly_booking_complete  — calendly.event_scheduled only (/us/book · /au/book)
 * - job_seeker_redirected
 * - form_validation_error
 */

import { markPrimaryConverted } from "./conversion-assist";
import {
  AUTHORITATIVE_LP_VERSION,
  US_BASELINE_LABEL,
} from "../config/lp-version";

export const LP_VERSION = AUTHORITATIVE_LP_VERSION;
export { US_BASELINE_LABEL, AUTHORITATIVE_LP_VERSION };

export type Attribution = {
  utm_source: string;
  utm_medium: string;
  utm_campaign: string;
  utm_term: string;
  utm_content: string;
  utm_matchtype: string;
  utm_device: string;
  gclid: string;
  gbraid: string;
  wbraid: string;
  landing_page_url: string;
  referrer: string;
  lp_version: string;
  lp_variant: string;
  baseline_label: string;
  session_id: string;
  market: string;
  category: string;
  variant: string;
  captured_at: string;
};

const ATTR_KEY = "vc_pilot_attribution";
const CLICK_ID_KEY = "vc_pilot_click_ids";
const CLICK_ID_TTL_MS = 90 * 24 * 60 * 60 * 1000;
const PRIMARY_FIRED_KEY = "vc_primary_fired_ids";

type DurableClickIds = {
  gclid?: string;
  gbraid?: string;
  wbraid?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  saved_at?: string;
};

function readDurableClickIds(): DurableClickIds {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage?.getItem(CLICK_ID_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as DurableClickIds;
    const saved = Date.parse(parsed.saved_at || "");
    if (!saved || Date.now() - saved > CLICK_ID_TTL_MS) return {};
    return parsed;
  } catch {
    return {};
  }
}

function writeDurableClickIds(attr: Pick<Attribution, "gclid" | "gbraid" | "wbraid" | "utm_source" | "utm_medium" | "utm_campaign" | "utm_term" | "utm_content">) {
  if (!attr.gclid && !attr.gbraid && !attr.wbraid) return;
  if (typeof window === "undefined") return;
  try {
    window.localStorage?.setItem(
      CLICK_ID_KEY,
      JSON.stringify({
        gclid: attr.gclid,
        gbraid: attr.gbraid,
        wbraid: attr.wbraid,
        utm_source: attr.utm_source,
        utm_medium: attr.utm_medium,
        utm_campaign: attr.utm_campaign,
        utm_term: attr.utm_term,
        utm_content: attr.utm_content,
        saved_at: new Date().toISOString(),
      }),
    );
  } catch {
    /* private mode / quota */
  }
}

function param(name: string): string {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get(name) || "";
}

function newSessionId(): string {
  const rand = Math.random().toString(36).slice(2, 10);
  return `vc_${Date.now().toString(36)}_${rand}`;
}

function emptyAttr(market = ""): Attribution {
  return {
    utm_source: "",
    utm_medium: "",
    utm_campaign: "",
    utm_term: "",
    utm_content: "",
    utm_matchtype: "",
    utm_device: "",
    gclid: "",
    gbraid: "",
    wbraid: "",
    landing_page_url: "",
    referrer: "",
    lp_version: LP_VERSION,
    lp_variant: "",
    baseline_label: US_BASELINE_LABEL,
    session_id: "",
    market,
    category: "",
    variant: "",
    captured_at: "",
  };
}

export type AttributionExtras = {
  category?: string;
  variant?: string;
  lp_variant?: string;
  /** Optional page override (e.g. baseline_v1_2026_08). Default LP_VERSION. */
  lp_version?: string;
  baseline_label?: string;
};

export function captureAttribution(
  market = "",
  extras: AttributionExtras = {},
): Attribution {
  if (typeof window === "undefined") return emptyAttr(market);

  const version = extras.lp_version || LP_VERSION;
  const baselineLabel = extras.baseline_label || US_BASELINE_LABEL;

  const next: Attribution = {
    utm_source: param("utm_source"),
    utm_medium: param("utm_medium"),
    utm_campaign: param("utm_campaign"),
    utm_term: param("utm_term"),
    utm_content: param("utm_content"),
    utm_matchtype: param("utm_matchtype"),
    utm_device: param("utm_device"),
    gclid: param("gclid"),
    gbraid: param("gbraid"),
    wbraid: param("wbraid"),
    landing_page_url: window.location.href.split("#")[0],
    referrer: document.referrer || "",
    lp_version: version,
    lp_variant: extras.lp_variant || param("lp_variant") || "",
    baseline_label: baselineLabel,
    session_id: "",
    market: market || param("market") || "",
    category: extras.category || param("category") || "",
    variant: extras.variant || param("variant") || "",
    captured_at: new Date().toISOString(),
  };

  try {
    const prev = JSON.parse(sessionStorage.getItem(ATTR_KEY) || "{}") as Partial<Attribution>;
    const durable = readDurableClickIds();
    const merged: Attribution = {
      utm_source: next.utm_source || prev.utm_source || durable.utm_source || "",
      utm_medium: next.utm_medium || prev.utm_medium || durable.utm_medium || "",
      utm_campaign: next.utm_campaign || prev.utm_campaign || durable.utm_campaign || "",
      utm_term: next.utm_term || prev.utm_term || durable.utm_term || "",
      utm_content: next.utm_content || prev.utm_content || durable.utm_content || "",
      utm_matchtype: next.utm_matchtype || prev.utm_matchtype || "",
      utm_device: next.utm_device || prev.utm_device || "",
      gclid: next.gclid || prev.gclid || durable.gclid || "",
      gbraid: next.gbraid || prev.gbraid || durable.gbraid || "",
      wbraid: next.wbraid || prev.wbraid || durable.wbraid || "",
      landing_page_url: prev.landing_page_url || next.landing_page_url || "",
      referrer: prev.referrer || next.referrer || "",
      lp_version: version || prev.lp_version || LP_VERSION,
      lp_variant: next.lp_variant || prev.lp_variant || "",
      baseline_label: baselineLabel || prev.baseline_label || US_BASELINE_LABEL,
      session_id: prev.session_id || newSessionId(),
      market: next.market || prev.market || market || "",
      category: next.category || prev.category || "",
      variant: next.variant || prev.variant || "",
      captured_at: prev.captured_at || next.captured_at,
    };
    sessionStorage.setItem(ATTR_KEY, JSON.stringify(merged));
    writeDurableClickIds(merged);
    return merged;
  } catch {
    next.session_id = newSessionId();
    writeDurableClickIds(next);
    return next;
  }
}

export function readAttribution(
  market = "",
  extras: AttributionExtras = {},
): Attribution {
  if (typeof window === "undefined") return captureAttribution(market, extras);
  try {
    const raw = sessionStorage.getItem(ATTR_KEY);
    if (raw) {
      const prev = JSON.parse(raw) as Partial<Attribution>;
      return {
        ...emptyAttr(market),
        ...prev,
        ...captureAttribution(market || prev.market || "", {
          category: extras.category || prev.category,
          variant: extras.variant || prev.variant,
          lp_variant: extras.lp_variant || prev.lp_variant,
          lp_version: extras.lp_version || prev.lp_version,
          baseline_label: extras.baseline_label || prev.baseline_label,
        }),
      };
    }
  } catch {
    /* ignore */
  }
  return captureAttribution(market, extras);
}

type DataLayerEvent = {
  event: string;
  [key: string]: string | number | boolean | undefined;
};

declare global {
  interface Window {
    dataLayer?: DataLayerEvent[];
    gtag?: (...args: unknown[]) => void;
    /** Set by MarketGtm when NEXT_PUBLIC_GA4_* is present. */
    __vcGa4MeasurementId?: string;
    /** Beacon sender installed by MarketGtm for experiment_* → GA4 collect. */
    __vcSendExpGa4?: (
      name: string,
      params: Record<string, string | number | boolean>,
    ) => void;
    /** Queued experiment_* GA4 sends until MarketGtm bridge is ready. */
    __vcExpGa4Queue?: Array<[string, Record<string, string | number | boolean>]>;
  }
}

const EXPERIMENT_EVENT_PREFIX = "experiment_";

/**
 * Dual-send site A/B events to GA4 via collect beacon (MarketGtm installs
 * window.__vcSendExpGa4). GTM alone was only forwarding page_view; gtag('event')
 * is swallowed when GTM owns the same measurement ID.
 */
function sendExperimentToGa4(
  name: string,
  params: Record<string, string | number | boolean>,
): void {
  if (typeof window === "undefined") return;
  if (!name.startsWith(EXPERIMENT_EVENT_PREFIX)) return;
  if (typeof window.__vcSendExpGa4 === "function") {
    window.__vcSendExpGa4(name, params);
    return;
  }
  window.__vcExpGa4Queue = window.__vcExpGa4Queue || [];
  window.__vcExpGa4Queue.push([name, params]);
}

const PII_EVENT_KEYS =
  /^(name|full_?name|first_?name|last_?name|email|phone|telephone|tel|message|form_message|company|company_website)$/i;

/** Diagnostic / secondary events — safe in all environments. No PII. */
export function trackEvent(
  name: string,
  payload: Record<string, string | number | boolean | undefined> = {},
) {
  if (typeof window === "undefined") return;
  window.dataLayer = window.dataLayer || [];
  const market = String(payload.market || "");
  const lpVariant =
    payload.lp_variant !== undefined && payload.lp_variant !== ""
      ? payload.lp_variant
      : undefined;
  const lpVersion =
    payload.lp_version !== undefined && payload.lp_version !== ""
      ? String(payload.lp_version)
      : LP_VERSION;
  const pagePath =
    payload.page_path !== undefined && payload.page_path !== ""
      ? String(payload.page_path)
      : window.location.pathname || "";
  const safePayload: Record<string, string | number | boolean | undefined> = {};
  for (const [key, value] of Object.entries(payload)) {
    if (PII_EVENT_KEYS.test(key)) continue;
    safePayload[key] = value;
  }
  const eventPayload: DataLayerEvent = {
    event: name,
    ...safePayload,
    market,
    site_surface: market || undefined,
    lp_version: lpVersion,
    page_path: pagePath,
    ...(lpVariant ? { lp_variant: lpVariant } : {}),
  };
  window.dataLayer.push(eventPayload);

  if (name.startsWith(EXPERIMENT_EVENT_PREFIX)) {
    const ga4Params: Record<string, string | number | boolean> = {};
    for (const [key, value] of Object.entries(eventPayload)) {
      if (key === "event" || value === undefined) continue;
      ga4Params[key] = value;
    }
    sendExperimentToGa4(name, ga4Params);
  }
}

/** Phone CTA click — canonical only. Not a qualified call conversion. */
export function trackPhoneClick(
  payload: Record<string, string | number | boolean | undefined> = {},
) {
  trackEvent("phone_cta_clicked", { ...payload, is_qualified_call: false });
  // Meaningful phone initiation — suppress secondary recovery for this session.
  markPrimaryConverted("phone_click");
  if (typeof window !== "undefined" && typeof window.dispatchEvent === "function") {
    window.dispatchEvent(new Event("vc-primary-converted"));
  }
}

/** Calendly CTA click — canonical only. Not Ads Primary. */
export function trackCalendlyClick(
  payload: Record<string, string | number | boolean | undefined> = {},
) {
  trackEvent("calendly_cta_clicked", payload);
}

/** Legacy thank-you inline Calendly viewed. Diagnostic only - not Ads Primary. */
export function trackCalendlyEmbedViewed(
  payload: Record<string, string | number | boolean | undefined> = {},
) {
  trackEvent("calendly_embed_viewed", {
    ...payload,
    bidding_primary: false,
    is_qualified_call: false,
  });
}

function alreadyFiredPrimary(submissionId: string): boolean {
  if (typeof window === "undefined") return false;
  try {
    const ids = JSON.parse(sessionStorage.getItem(PRIMARY_FIRED_KEY) || "[]") as string[];
    return ids.includes(submissionId);
  } catch {
    return false;
  }
}

function markPrimaryFired(submissionId: string) {
  if (typeof window === "undefined") return;
  try {
    const ids = JSON.parse(sessionStorage.getItem(PRIMARY_FIRED_KEY) || "[]") as string[];
    if (!ids.includes(submissionId)) {
      ids.push(submissionId);
      sessionStorage.setItem(PRIMARY_FIRED_KEY, JSON.stringify(ids.slice(-50)));
    }
  } catch {
    /* ignore */
  }
}

/**
 * Durable form delivery event after server accept.
 * Name: employer_inquiry_submitted only (no aliases).
 * Funnel / observation only — NOT the Ads bidding Primary (spam risk).
 * Never fire for log_only / conversion_eligible=false.
 * Never send PII or click ids to the dataLayer.
 */
export function trackValidEmployerSubmit(opts: {
  market: string;
  submissionId: string;
  role?: string;
  category?: string;
  variant?: string;
  conversionEligible?: boolean;
  companySize?: string;
  positionsNeeded?: string;
  hiringTimeline?: string;
  schedule?: string;
  leadScore?: number;
  estimatedLeadValue?: number;
  valueKind?: string;
  fitLabel?: string;
  landingPage?: string;
  lpVersion?: string;
  lpSurface?: string;
  ctaMode?: string;
  lpVariant?: string;
  pagePath?: string;
}) {
  if (opts.conversionEligible === false) {
    trackEvent("employer_inquiry_log_only", {
      market: opts.market,
      lead_reference: opts.submissionId,
      primary_eligible: false,
      bidding_primary: false,
      modeled_value_for_bidding: false,
    });
    return;
  }
  if (!opts.submissionId || alreadyFiredPrimary(opts.submissionId)) {
    trackEvent("employer_inquiry_submitted_deduped", {
      market: opts.market,
      lead_reference: opts.submissionId,
    });
    return;
  }
  markPrimaryFired(opts.submissionId);
  markPrimaryConverted("form_submit");
  if (typeof window !== "undefined" && typeof window.dispatchEvent === "function") {
    window.dispatchEvent(new Event("vc-primary-converted"));
  }
  const landingType =
    opts.ctaMode === "quiz_lp" || opts.lpSurface === "quiz" ? "quiz_lp" : "employer_paid_lp";
  const payload = {
    market: opts.market,
    lp_version: opts.lpVersion || LP_VERSION,
    page_path: opts.pagePath || "",
    landing_page_type: landingType,
    role_selected: opts.role || "",
    staff_count_range: opts.positionsNeeded || "",
    work_schedule: opts.schedule || "",
    lead_reference: opts.submissionId,
    category: opts.category || "",
    variant: opts.variant || "",
    company_size: opts.companySize || "",
    hiring_timeline: opts.hiringTimeline || "",
    lead_score: opts.leadScore,
    estimated_lead_value: opts.estimatedLeadValue,
    value_kind: opts.valueKind || "estimated_modeled",
    fit_label: opts.fitLabel || "",
    landing_page: opts.landingPage || "",
    lp_surface: opts.lpSurface || "form",
    cta_mode: opts.ctaMode || (opts.lpSurface === "quiz" ? "quiz_lp" : "form_primary"),
    lp_variant: opts.lpVariant || (opts.lpSurface === "quiz" ? "quiz" : ""),
    primary_eligible: true,
    bidding_primary: false,
    modeled_value_for_bidding: false,
    funnel_step: "form_submit_success",
    is_job_order: false,
    is_placement: false,
    is_qualified_call: false,
  };
  trackEvent("employer_inquiry_submitted", payload);
}
