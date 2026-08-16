/**
 * Market Calendly booking URLs for the thank-you page.
 *
 * Defaults from live Virtual Coworker WordPress thank-you widgets (2026-08-06):
 *   US → calendly.com/cheyenne-virtualcoworker/30min
 *   AU → calendly.com/apac-virtualcoworker/30min
 *
 * Override anytime with NEXT_PUBLIC_CALENDLY_US / NEXT_PUBLIC_CALENDLY_AU.
 *
 * Thank-you booking UX: our overlay (headline + Call + initInlineWidget),
 * not Calendly native popup chrome (we cannot inject copy inside that).
 * Eligible us/au thank-you auto-opens once. Call stays conversion north star.
 * Booking click / overlay is not Ads Primary.
 */

import type { MarketId } from "../config/markets";

export const THANK_YOU_BOOKING_COPY = {
  us: {
    eyebrow: "30-minute consult",
    headline: "Book your free consultation",
    sub: "Obligation free, at no cost. A member of our team will walk through the role and next steps.",
    micro: "Call now if you’d rather talk immediately.",
  },
  au: {
    eyebrow: "30-minute chat",
    headline: "Book a free consultation",
    sub: "Obligation free, at no cost. A member of our team will talk through the role and Australian hours.",
    micro: "Call now if you’d rather talk immediately.",
  },
} as const;

const CORPORATE_DEFAULTS: Record<MarketId, string> = {
  us: "https://calendly.com/cheyenne-virtualcoworker/30min",
  au: "https://calendly.com/apac-virtualcoworker/30min",
};

/** WP thank-you widget used navy; keep the same brand accent in the popup. */
const EMBED_PRIMARY_COLOR = "214873";

function stripHash(hex: string): string {
  return hex.replace(/^#/, "");
}

function normalizeCalendlyUrl(raw: string): string | null {
  const trimmed = raw.trim();
  if (!trimmed) return null;
  try {
    const u = new URL(trimmed);
    if (u.protocol !== "https:") return null;
    if (u.hostname !== "calendly.com" && u.hostname !== "www.calendly.com") {
      return null;
    }
    // Drop widget query noise; keep a clean bookable URL.
    u.search = "";
    u.hash = "";
    return u.toString().replace(/\/$/, "");
  } catch {
    return null;
  }
}

/** Resolved booking URL for a market, or null if unset/invalid. */
export function calendlyUrlForMarket(market: MarketId): string | null {
  const envKey =
    market === "au" ? "NEXT_PUBLIC_CALENDLY_AU" : "NEXT_PUBLIC_CALENDLY_US";
  const fromEnv = (process.env[envKey] || "").trim();
  return (
    normalizeCalendlyUrl(fromEnv) ||
    normalizeCalendlyUrl(CORPORATE_DEFAULTS[market])
  );
}

/** Hostname for Calendly `embed_domain`. */
export function calendlyEmbedDomain(): string {
  const raw = (process.env.NEXT_PUBLIC_SITE_URL || "https://www.virtualcoworker.app").trim();
  try {
    return new URL(raw).hostname || "www.virtualcoworker.app";
  } catch {
    return "www.virtualcoworker.app";
  }
}

export type CalendlyWidgetTheme = {
  embedDomain?: string;
  primaryColor?: string;
  backgroundColor?: string;
  textColor?: string;
};

/**
 * URL passed to Calendly.initInlineWidget / initPopupWidget / preload.
 * https://calendly.com/help/how-to-customize-your-embed
 */
export function calendlyPopupUrl(
  bookUrl: string,
  opts: CalendlyWidgetTheme = {},
): string | null {
  const clean = normalizeCalendlyUrl(bookUrl);
  if (!clean) return null;
  const u = new URL(clean);
  const domain = (opts.embedDomain || calendlyEmbedDomain()).trim();
  if (domain) u.searchParams.set("embed_domain", domain);
  u.searchParams.set("hide_gdpr_banner", "1");
  u.searchParams.set("hide_event_type_details", "1");
  u.searchParams.set(
    "primary_color",
    stripHash(opts.primaryColor || EMBED_PRIMARY_COLOR),
  );
  if (opts.backgroundColor) {
    u.searchParams.set("background_color", stripHash(opts.backgroundColor));
  }
  if (opts.textColor) {
    u.searchParams.set("text_color", stripHash(opts.textColor));
  }
  return u.toString();
}

/** Survives React StrictMode remount; resets on full page reload. */
let autoOpenedPopupUrl = "";

/** Claim one auto-open per widget URL for this page load. */
export function claimCalendlyAutoOpen(widgetUrl: string): boolean {
  if (!widgetUrl || autoOpenedPopupUrl === widgetUrl) return false;
  autoOpenedPopupUrl = widgetUrl;
  return true;
}

/** Eligible employer thank-you only. Never auto-open test-hidden / eligible=0. */
export function shouldCalendlyAutoOpen(conversionEligible: boolean): boolean {
  return conversionEligible === true;
}

/** Test-only. */
export function resetCalendlyAutoOpenForTests() {
  autoOpenedPopupUrl = "";
}
