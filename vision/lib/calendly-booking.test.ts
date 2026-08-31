import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  calendlyScheduledDedupeId,
  calendlyScheduledPayloadFromMessage,
  isCalendlyEventScheduledMessage,
  resetCalendlyBookingDedupeForTests,
  trackCalendlyBookingComplete,
} from "./calendly-booking";

const events: Array<{ event: string; [key: string]: unknown }> = [];

beforeEach(() => {
  events.length = 0;
  resetCalendlyBookingDedupeForTests();
  vi.stubGlobal("window", {
    location: {
      pathname: "/us/book",
      href: "https://www.virtualcoworker.app/us/book?gclid=test123&utm_source=google",
      search: "?gclid=test123&utm_source=google",
    },
    dataLayer: {
      push(item: { event: string }) {
        events.push(item);
      },
    },
    sessionStorage: (() => {
      const store = new Map<string, string>();
      return {
        getItem: (k: string) => store.get(k) ?? null,
        setItem: (k: string, v: string) => {
          store.set(k, v);
        },
        removeItem: (k: string) => {
          store.delete(k);
        },
      };
    })(),
    localStorage: (() => {
      const store = new Map<string, string>();
      return {
        getItem: (k: string) => store.get(k) ?? null,
        setItem: (k: string, v: string) => {
          store.set(k, v);
        },
        removeItem: (k: string) => {
          store.delete(k);
        },
      };
    })(),
  });
  vi.stubGlobal("document", { referrer: "" });
  // sessionStorage/localStorage also needed via globalThis for node
  Object.defineProperty(globalThis, "sessionStorage", {
    value: window.sessionStorage,
    configurable: true,
  });
  Object.defineProperty(globalThis, "localStorage", {
    value: window.localStorage,
    configurable: true,
  });
  Object.defineProperty(globalThis, "document", {
    value: { referrer: "" },
    configurable: true,
  });
  // Pre-seed attribution as captureAttribution would
  window.sessionStorage.setItem(
    "vc_pilot_attribution",
    JSON.stringify({
      gclid: "test123",
      utm_source: "google",
      utm_medium: "cpc",
      utm_campaign: "VC_US_S_CORE",
      utm_content: "sitelink",
      utm_term: "hire va",
      gbraid: "",
      wbraid: "",
      session_id: "vc_test_sess",
      market: "us",
      landing_page_url: "https://www.virtualcoworker.app/us/book",
      referrer: "",
      lp_version: "baseline_v1_2026_08",
      lp_variant: "calendly_book",
      baseline_label: "US_BASELINE_2026-08-18",
      category: "",
      variant: "",
      captured_at: new Date().toISOString(),
      utm_matchtype: "",
      utm_device: "",
    }),
  );
});

afterEach(() => {
  resetCalendlyBookingDedupeForTests();
  vi.unstubAllGlobals();
});

describe("calendly booking complete", () => {
  it("recognizes only calendly.event_scheduled", () => {
    expect(isCalendlyEventScheduledMessage({ event: "calendly.event_scheduled" })).toBe(
      true,
    );
    expect(isCalendlyEventScheduledMessage({ event: "calendly.date_and_time_selected" })).toBe(
      false,
    );
    expect(isCalendlyEventScheduledMessage({ event: "calendly.profile_page_viewed" })).toBe(
      false,
    );
    expect(isCalendlyEventScheduledMessage(null)).toBe(false);
  });

  it("fires calendly_booking_complete once with attribution", () => {
    const payload = {
      event: { uri: "https://api.calendly.com/scheduled_events/AAA" },
      invitee: { uri: "https://api.calendly.com/scheduled_events/AAA/invitees/BBB" },
    };
    expect(
      trackCalendlyBookingComplete({
        market: "us",
        bookUrl: "https://calendly.com/cheyenne-virtualcoworker/30min",
        payload,
      }),
    ).toBe(true);

    const fired = events.filter((e) => e.event === "calendly_booking_complete");
    expect(fired).toHaveLength(1);
    expect(fired[0].market).toBe("us");
    expect(fired[0].gclid).toBe("test123");
    expect(fired[0].utm_source).toBe("google");
    expect(fired[0].utm_campaign).toBe("VC_US_S_CORE");
    expect(fired[0].bidding_primary).toBe(false);
    expect(fired[0].landing_page_type).toBe("calendly_book");

    expect(
      trackCalendlyBookingComplete({
        market: "us",
        bookUrl: "https://calendly.com/cheyenne-virtualcoworker/30min",
        payload,
      }),
    ).toBe(false);
    expect(events.filter((e) => e.event === "calendly_booking_complete")).toHaveLength(1);
    expect(
      events.filter((e) => e.event === "calendly_booking_complete_deduped"),
    ).toHaveLength(1);
  });

  it("uses invitee uri for dedupe id", () => {
    expect(
      calendlyScheduledDedupeId("au", {
        invitee: { uri: "https://api.calendly.com/invitees/xyz" },
      }),
    ).toBe("https://api.calendly.com/invitees/xyz");
  });

  it("parses scheduled payload from postMessage data", () => {
    expect(
      calendlyScheduledPayloadFromMessage({
        event: "calendly.date_and_time_selected",
      }),
    ).toBeNull();
    expect(
      calendlyScheduledPayloadFromMessage({
        event: "calendly.event_scheduled",
        payload: { invitee: { uri: "inv-1" } },
      }),
    ).toEqual({ invitee: { uri: "inv-1" } });
  });
});
