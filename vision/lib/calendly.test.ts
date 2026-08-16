import { afterEach, describe, expect, it } from "vitest";
import {
  calendlyEmbedDomain,
  calendlyPopupUrl,
  calendlyUrlForMarket,
  claimCalendlyAutoOpen,
  resetCalendlyAutoOpenForTests,
  shouldCalendlyAutoOpen,
  THANK_YOU_BOOKING_COPY,
} from "./calendly";

const ENV_KEYS = [
  "NEXT_PUBLIC_CALENDLY_US",
  "NEXT_PUBLIC_CALENDLY_AU",
  "NEXT_PUBLIC_SITE_URL",
] as const;

afterEach(() => {
  for (const k of ENV_KEYS) delete process.env[k];
  resetCalendlyAutoOpenForTests();
});

describe("calendlyUrlForMarket", () => {
  it("defaults to live WP US / AU calendly hosts", () => {
    expect(calendlyUrlForMarket("us")).toBe(
      "https://calendly.com/cheyenne-virtualcoworker/30min",
    );
    expect(calendlyUrlForMarket("au")).toBe(
      "https://calendly.com/apac-virtualcoworker/30min",
    );
  });

  it("prefers env overrides when valid", () => {
    process.env.NEXT_PUBLIC_CALENDLY_US =
      "https://calendly.com/vc-us-test/45min/?hide_landing_page_details=1";
    expect(calendlyUrlForMarket("us")).toBe(
      "https://calendly.com/vc-us-test/45min",
    );
  });

  it("rejects non-calendly env values and falls back to corporate default", () => {
    process.env.NEXT_PUBLIC_CALENDLY_AU = "https://example.com/not-calendly";
    expect(calendlyUrlForMarket("au")).toBe(
      "https://calendly.com/apac-virtualcoworker/30min",
    );
  });

  it("builds popup widget url without inline iframe params", () => {
    const src = calendlyPopupUrl(
      "https://calendly.com/cheyenne-virtualcoworker/30min",
      { embedDomain: "www.virtualcoworker.app" },
    );
    expect(src).toContain(
      "https://calendly.com/cheyenne-virtualcoworker/30min?",
    );
    expect(src).toContain("embed_domain=www.virtualcoworker.app");
    expect(src).toContain("hide_gdpr_banner=1");
    expect(src).toContain("hide_event_type_details=1");
    expect(src).toContain("primary_color=214873");
    expect(src).not.toMatch(/embed_type=Inline/i);
    expect(src).not.toMatch(/popup/i);
  });

  it("defaults embed domain to production host", () => {
    delete process.env.NEXT_PUBLIC_SITE_URL;
    expect(calendlyEmbedDomain()).toBe("www.virtualcoworker.app");
  });

  it("claims one auto-open per widget url", () => {
    expect(claimCalendlyAutoOpen("https://calendly.com/cheyenne-virtualcoworker/30min")).toBe(
      true,
    );
    expect(claimCalendlyAutoOpen("https://calendly.com/cheyenne-virtualcoworker/30min")).toBe(
      false,
    );
    expect(claimCalendlyAutoOpen("https://calendly.com/apac-virtualcoworker/30min")).toBe(true);
  });

  it("does not auto-open on eligible=0 / test-hidden thank-you", () => {
    expect(shouldCalendlyAutoOpen(true)).toBe(true);
    expect(shouldCalendlyAutoOpen(false)).toBe(false);
  });

  it("uses Caitlin booking copy without demo or fake urgency", () => {
    expect(THANK_YOU_BOOKING_COPY.us.headline).toBe("Book your free consultation");
    expect(THANK_YOU_BOOKING_COPY.au.headline).toBe("Book a free consultation");
    for (const copy of [THANK_YOU_BOOKING_COPY.us, THANK_YOU_BOOKING_COPY.au]) {
      expect(copy.sub.toLowerCase()).toContain("obligation free, at no cost");
      expect(copy.sub.toLowerCase()).toContain("a member of our team");
      expect(copy.headline.toLowerCase()).not.toMatch(/demo/);
      expect(copy.sub.toLowerCase()).not.toMatch(/demo|#1|limited time|only \d+ spots/);
      expect(`${copy.headline}${copy.sub}${copy.micro}`).not.toMatch(/\u2014|&mdash;/);
    }
  });
});
