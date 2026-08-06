import { describe, expect, it } from "vitest";
import { allowLogOnlyLeads, configuredChannels, deliveryBlockerMessage } from "./lead-delivery";

describe("lead delivery honesty", () => {
  it("reports no channels when env empty", () => {
    const cfg = configuredChannels({});
    expect(cfg.channels).toEqual([]);
  });

  it("detects email channel only when to+from+resend present", () => {
    const cfg = configuredChannels({
      LEAD_EMAIL_US: "ops@example.com",
      LEAD_FROM_EMAIL: "from@example.com",
      RESEND_API_KEY: "re_test",
    });
    expect(cfg.channels).toContain("email");
  });

  it("does not treat Zoho alone as inventing success — just configured", () => {
    const cfg = configuredChannels({ ZOHO_WEBHOOK_URL: "https://example.com/zoho" });
    expect(cfg.channels).toEqual(["zoho"]);
  });

  it("log-only requires explicit flag", () => {
    expect(allowLogOnlyLeads({})).toBe(false);
    expect(allowLogOnlyLeads({ ALLOW_LOG_ONLY_LEADS: "true" })).toBe(true);
  });

  it("blocker message is honest", () => {
    expect(deliveryBlockerMessage().toLowerCase()).toMatch(/not configured/);
  });
});
