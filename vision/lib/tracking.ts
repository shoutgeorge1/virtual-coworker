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
 * Canonical events (+ short aliases for GTM maps):
 * - employer_gate_selected
 * - employer_form_started
 * - employer_form_validation_error
 * - employer_inquiry_submitted  (+ alias form_submit_success) — delivery OK, not Ads Primary
 * - employer_inquiry_delivery_failed
 * - phone_cta_clicked           (+ alias phone_click) — click ≠ qualified call
 * - primary_cta_clicked         — sell-first hero CTA to #gate; not Ads Primary
 * - calendly_cta_clicked        (+ alias calendly_click) — thank-you popup / book click; not Ads Primary
 * - calendly_embed_viewed       — legacy inline calendar seen; not Ads Primary
 * - conversion_assist_opened
 * - conversion_assist_cta_clicked
 * - job_seeker_redirected       (interaction only — never Ads conversion)
 * - form_start                  (+ alias of employer_form_started)
 * - chat_widget_impression / chat_widget_open
 * - popup_impression / popup_close
 */

import { markPrimaryConverted } from "./conversion-assist";

export const LP_VERSION = "stage1-v8";

export type Attribution = {
  utm_source: string;
  utm_medium: string;
  utm_campaign: string;
  utm_term: string;
  utm_content: string;
  gclid: string;
  gbraid: string;
  wbraid: string;
  landing_page_url: string;
  referrer: string;
  lp_version: string;
  lp_variant: string;
  market: string;
  category: string;
  variant: string;
  captured_at: string;
};

const ATTR_KEY = "vc_pilot_attribution";
const PRIMARY_FIRED_KEY = "vc_primary_fired_ids";

function param(name: string): string {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get(name) || "";
}

function emptyAttr(market = ""): Attribution {
  return {
    utm_source: "",
    utm_medium: "",
    utm_campaign: "",
    utm_term: "",
    utm_content: "",
    gclid: "",
    gbraid: "",
    wbraid: "",
    landing_page_url: "",
    referrer: "",
    lp_version: LP_VERSION,
    lp_variant: "",
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
};

export function captureAttribution(
  market = "",
  extras: AttributionExtras = {},
): Attribution {
  if (typeof window === "undefined") return emptyAttr(market);

  const version = extras.lp_version || LP_VERSION;

  const next: Attribution = {
    utm_source: param("utm_source"),
    utm_medium: param("utm_medium"),
    utm_campaign: param("utm_campaign"),
    utm_term: param("utm_term"),
    utm_content: param("utm_content"),
    gclid: param("gclid"),
    gbraid: param("gbraid"),
    wbraid: param("wbraid"),
    landing_page_url: window.location.href.split("#")[0],
    referrer: document.referrer || "",
    lp_version: version,
    lp_variant: extras.lp_variant || param("lp_variant") || "",
    market: market || param("market") || "",
    category: extras.category || param("category") || "",
    variant: extras.variant || param("variant") || "",
    captured_at: new Date().toISOString(),
  };

  try {
    const prev = JSON.parse(sessionStorage.getItem(ATTR_KEY) || "{}") as Partial<Attribution>;
    const merged: Attribution = {
      utm_source: next.utm_source || prev.utm_source || "",
      utm_medium: next.utm_medium || prev.utm_medium || "",
      utm_campaign: next.utm_campaign || prev.utm_campaign || "",
      utm_term: next.utm_term || prev.utm_term || "",
      utm_content: next.utm_content || prev.utm_content || "",
      gclid: next.gclid || prev.gclid || "",
      gbraid: next.gbraid || prev.gbraid || "",
      wbraid: next.wbraid || prev.wbraid || "",
      landing_page_url: next.landing_page_url || prev.landing_page_url || "",
      referrer: next.referrer || prev.referrer || "",
      lp_version: version || prev.lp_version || LP_VERSION,
      lp_variant: next.lp_variant || prev.lp_variant || "",
      market: next.market || prev.market || market || "",
      category: next.category || prev.category || "",
      variant: next.variant || prev.variant || "",
      captured_at: prev.captured_at || next.captured_at,
    };
    sessionStorage.setItem(ATTR_KEY, JSON.stringify(merged));
    return merged;
  } catch {
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

/** Diagnostic / secondary events — safe in all environments. */
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
  const eventPayload: DataLayerEvent = {
    event: name,
    ...payload,
    market,
    site_surface: market || undefined,
    lp_version: lpVersion,
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

/** Phone CTA click — canonical + short alias. Not a qualified call conversion. */
export function trackPhoneClick(
  payload: Record<string, string | number | boolean | undefined> = {},
) {
  trackEvent("phone_cta_clicked", { ...payload, is_qualified_call: false });
  trackEvent("phone_click", {
    ...payload,
    is_qualified_call: false,
    alias_of: "phone_cta_clicked",
  });
  // Meaningful phone initiation — suppress secondary recovery for this session.
  markPrimaryConverted("phone_click");
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event("vc-primary-converted"));
  }
}

/** Calendly CTA click — canonical + short alias. Not Ads Primary. */
export function trackCalendlyClick(
  payload: Record<string, string | number | boolean | undefined> = {},
) {
  trackEvent("calendly_cta_clicked", payload);
  trackEvent("calendly_click", { ...payload, alias_of: "calendly_cta_clicked" });
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
 * Name: employer_inquiry_submitted (+ alias form_submit_success).
 * Funnel / observation only — NOT the Ads bidding Primary (spam risk).
 * Steering = duration-qualified phone; quality = Zoho Qualified lead offline.
 * Never fire for log_only / conversion_eligible=false.
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
  leadScore?: number;
  estimatedLeadValue?: number;
  valueKind?: string;
  fitLabel?: string;
  landingPage?: string;
  utmSource?: string;
  utmMedium?: string;
  utmCampaign?: string;
  utmTerm?: string;
  utmContent?: string;
  gclid?: string;
  gbraid?: string;
  wbraid?: string;
  submittedAt?: string;
  lpSurface?: string;
  ctaMode?: string;
  lpVariant?: string;
}) {
  if (opts.conversionEligible === false) {
    trackEvent("employer_inquiry_log_only", {
      market: opts.market,
      submission_id: opts.submissionId,
      primary_eligible: false,
      bidding_primary: false,
      modeled_value_for_bidding: false,
    });
    return;
  }
  if (!opts.submissionId || alreadyFiredPrimary(opts.submissionId)) {
    trackEvent("employer_inquiry_submitted_deduped", {
      market: opts.market,
      submission_id: opts.submissionId,
    });
    return;
  }
  markPrimaryFired(opts.submissionId);
  markPrimaryConverted("form_submit");
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event("vc-primary-converted"));
  }
  const payload = {
    market: opts.market,
    country: opts.market === "au" ? "AU" : "US",
    submission_id: opts.submissionId,
    role: opts.role || "",
    role_category: opts.category || "",
    category: opts.category || "",
    variant: opts.variant || "",
    company_size: opts.companySize || "",
    positions_needed: opts.positionsNeeded || "",
    hiring_timeline: opts.hiringTimeline || "",
    lead_score: opts.leadScore,
    estimated_lead_value: opts.estimatedLeadValue,
    value_kind: opts.valueKind || "estimated_modeled",
    fit_label: opts.fitLabel || "",
    landing_page: opts.landingPage || "",
    utm_source: opts.utmSource || "",
    utm_medium: opts.utmMedium || "",
    utm_campaign: opts.utmCampaign || "",
    utm_term: opts.utmTerm || "",
    utm_content: opts.utmContent || "",
    gclid: opts.gclid || "",
    gbraid: opts.gbraid || "",
    wbraid: opts.wbraid || "",
    submitted_at: opts.submittedAt || "",
    lp_surface: opts.lpSurface || "form",
    cta_mode: opts.ctaMode || (opts.lpSurface === "quiz" ? "quiz_lp" : "form_primary"),
    landing_type:
      opts.ctaMode === "quiz_lp" || opts.lpSurface === "quiz" ? "quiz_lp" : "form_lp",
    lp_variant: opts.lpVariant || (opts.lpSurface === "quiz" ? "quiz" : ""),
    /** Durable delivery succeeded — still NOT Ads bidding Primary */
    primary_eligible: true,
    bidding_primary: false,
    modeled_value_for_bidding: false,
    funnel_step: "form_submit_success",
    is_job_order: false,
    is_placement: false,
    is_qualified_call: false,
  };
  trackEvent("employer_inquiry_submitted", payload);
  trackEvent("form_submit_success", { ...payload, alias_of: "employer_inquiry_submitted" });
  trackEvent("form_submit", { ...payload, alias_of: "employer_inquiry_submitted" });
}
