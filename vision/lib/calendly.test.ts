import { afterEach, describe, expect, it } from "vitest";
import { calendlyUrlForMarket } from "./calendly";

const ENV_KEYS = ["NEXT_PUBLIC_CALENDLY_US", "NEXT_PUBLIC_CALENDLY_AU"] as const;

afterEach(() => {
  for (const k of ENV_KEYS) delete process.env[k];
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
});
