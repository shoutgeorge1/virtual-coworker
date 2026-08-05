/**
 * Client-side attribution + event helpers for the paid Search pilot.
 * Ads conversion tags fire only when NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=true
 * and IDs are set — never in bare local development.
 */

export type Attribution = {
  utm_source: string;
  utm_medium: string;
  utm_campaign: string;
  utm_term: string;
  utm_content: string;
  gclid: string;
  landing_page_url: string;
  referrer: string;
};

const ATTR_KEY = "vc_pilot_attribution";

function param(name: string): string {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get(name) || "";
}

export function captureAttribution(): Attribution {
  if (typeof window === "undefined") {
    return {
      utm_source: "",
      utm_medium: "",
      utm_campaign: "",
      utm_term: "",
      utm_content: "",
      gclid: "",
      landing_page_url: "",
      referrer: "",
    };
  }

  const next: Attribution = {
    utm_source: param("utm_source"),
    utm_medium: param("utm_medium"),
    utm_campaign: param("utm_campaign"),
    utm_term: param("utm_term"),
    utm_content: param("utm_content"),
    gclid: param("gclid"),
    landing_page_url: window.location.href.split("#")[0],
    referrer: document.referrer || "",
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
      landing_page_url: next.landing_page_url || prev.landing_page_url || "",
      referrer: next.referrer || prev.referrer || "",
    };
    sessionStorage.setItem(ATTR_KEY, JSON.stringify(merged));
    return merged;
  } catch {
    return next;
  }
}

export function readAttribution(): Attribution {
  if (typeof window === "undefined") return captureAttribution();
  try {
    const raw = sessionStorage.getItem(ATTR_KEY);
    if (raw) return { ...captureAttribution(), ...JSON.parse(raw) };
  } catch {
    /* ignore */
  }
  return captureAttribution();
}

type DataLayerEvent = {
  event: string;
  [key: string]: string | number | boolean | undefined;
};

declare global {
  interface Window {
    dataLayer?: DataLayerEvent[];
  }
}

/** Diagnostic / secondary events — safe in all environments. */
export function trackEvent(name: string, payload: Record<string, string | number | boolean | undefined> = {}) {
  if (typeof window === "undefined") return;
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event: name, ...payload });
}

/**
 * Primary Ads conversion helper.
 * No-ops unless explicitly enabled with real IDs — prevents fake conversions in dev.
 */
export function trackPrimaryConversion(eventName: "form_submit" | "qualified_form_submit") {
  trackEvent(eventName);
  const enabled = process.env.NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS === "true";
  const sendId = process.env.NEXT_PUBLIC_ADS_CONVERSION_ID;
  const label = process.env.NEXT_PUBLIC_ADS_CONVERSION_LABEL;
  if (!enabled || !sendId || !label) return;
  // Real gtag wiring is installed via temporary GTM once IDs are confirmed.
  trackEvent("ads_conversion_queued", { send_to: `${sendId}/${label}`, conversion_event: eventName });
}
