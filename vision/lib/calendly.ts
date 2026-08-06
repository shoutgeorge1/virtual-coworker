/**
 * Market Calendly booking URLs for the thank-you page.
 *
 * Defaults from live Virtual Coworker WordPress thank-you widgets (2026-08-06):
 *   US → calendly.com/cheyenne-virtualcoworker/30min
 *   AU → calendly.com/apac-virtualcoworker/30min
 *
 * Override anytime with NEXT_PUBLIC_CALENDLY_US / NEXT_PUBLIC_CALENDLY_AU.
 */

import type { MarketId } from "../config/markets";

const CORPORATE_DEFAULTS: Record<MarketId, string> = {
  us: "https://calendly.com/cheyenne-virtualcoworker/30min",
  au: "https://calendly.com/apac-virtualcoworker/30min",
};

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
