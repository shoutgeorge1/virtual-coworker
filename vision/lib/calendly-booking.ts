/**
 * Direct booking-page Calendly completion tracking.
 * Fires only on calendly.event_scheduled — not page view, embed load, or date pick.
 */

import { readAttribution, trackEvent } from "./tracking";

const FIRED_KEY = "vc_calendly_booking_complete_ids";

type CalendlyScheduledPayload = {
  event?: { uri?: string };
  invitee?: { uri?: string };
};

function alreadyFired(dedupeId: string): boolean {
  if (typeof window === "undefined") return false;
  try {
    const ids = JSON.parse(sessionStorage.getItem(FIRED_KEY) || "[]") as string[];
    return ids.includes(dedupeId);
  } catch {
    return false;
  }
}

function markFired(dedupeId: string) {
  if (typeof window === "undefined") return;
  try {
    const ids = JSON.parse(sessionStorage.getItem(FIRED_KEY) || "[]") as string[];
    if (!ids.includes(dedupeId)) {
      ids.push(dedupeId);
      sessionStorage.setItem(FIRED_KEY, JSON.stringify(ids.slice(-50)));
    }
  } catch {
    /* private mode / quota */
  }
}

export function calendlyScheduledDedupeId(
  market: string,
  payload: CalendlyScheduledPayload | null | undefined,
): string {
  const invitee = (payload?.invitee?.uri || "").trim();
  if (invitee) return invitee;
  const eventUri = (payload?.event?.uri || "").trim();
  if (eventUri) return eventUri;
  return `calendly_booking_${market}_once`;
}

/**
 * Push calendly_booking_complete once per invitee/event.
 * Includes market + stored attribution (click ids / UTMs).
 * Not Ads Primary — GTM/Ads maps this separately if desired.
 */
export function trackCalendlyBookingComplete(opts: {
  market: string;
  bookUrl?: string;
  payload?: CalendlyScheduledPayload | null;
}): boolean {
  if (opts.market !== "us" && opts.market !== "au") return false;
  const dedupeId = calendlyScheduledDedupeId(opts.market, opts.payload);
  if (alreadyFired(dedupeId)) {
    trackEvent("calendly_booking_complete_deduped", {
      market: opts.market,
      booking_reference: dedupeId,
      bidding_primary: false,
      is_qualified_call: false,
    });
    return false;
  }
  markFired(dedupeId);

  const attr = readAttribution(opts.market, {
    lp_variant: "calendly_book",
  });

  trackEvent("calendly_booking_complete", {
    market: opts.market,
    page_path:
      typeof window !== "undefined" ? window.location.pathname || "" : "",
    landing_page_type: "calendly_book",
    lp_variant: "calendly_book",
    booking_reference: dedupeId,
    book_url: opts.bookUrl || "",
    gclid: attr.gclid || "",
    gbraid: attr.gbraid || "",
    wbraid: attr.wbraid || "",
    utm_source: attr.utm_source || "",
    utm_medium: attr.utm_medium || "",
    utm_campaign: attr.utm_campaign || "",
    utm_content: attr.utm_content || "",
    utm_term: attr.utm_term || "",
    session_id: attr.session_id || "",
    bidding_primary: false,
    is_qualified_call: false,
  });
  return true;
}

/** Test-only. */
export function resetCalendlyBookingDedupeForTests() {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.removeItem(FIRED_KEY);
  } catch {
    /* ignore */
  }
}

export function isCalendlyEventScheduledMessage(data: unknown): boolean {
  if (!data || typeof data !== "object") return false;
  const event = (data as { event?: unknown }).event;
  return event === "calendly.event_scheduled";
}

export function calendlyScheduledPayloadFromMessage(
  data: unknown,
): CalendlyScheduledPayload | null {
  if (!isCalendlyEventScheduledMessage(data)) return null;
  const payload = (data as { payload?: CalendlyScheduledPayload }).payload;
  return payload && typeof payload === "object" ? payload : {};
}
