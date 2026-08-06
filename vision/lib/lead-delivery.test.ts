import { describe, expect, it } from "vitest";
import {
  allowLogOnlyLeads,
  configuredChannels,
  deliveryBlockerMessage,
  durableTrafficChannels,
} from "./lead-delivery";

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

  it("treats ZOHO_WEBHOOK_URL as zoho_webhook not CRM", () => {
    const cfg = configuredChannels({ ZOHO_WEBHOOK_URL: "https://example.com/zoho" });
    expect(cfg.channels).toEqual(["zoho_webhook"]);
    expect(cfg.zohoCrm).toBe(false);
    expect(durableTrafficChannels({ ZOHO_WEBHOOK_URL: "https://example.com/zoho" })).toEqual([
      "zoho_webhook",
    ]);
  });

  it("zoho CRM alone is not a traffic durable channel", () => {
    const env = {
      ZOHO_CRM_ENABLED: "true",
      ZOHO_CRM_CLIENT_ID: "cid",
      ZOHO_CRM_CLIENT_SECRET: "sec",
      ZOHO_CRM_REFRESH_TOKEN: "rt",
    };
    const cfg = configuredChannels(env);
    expect(cfg.channels).toContain("zoho_crm");
    expect(durableTrafficChannels(env)).toEqual([]);
  });

  it("log-only requires explicit flag", () => {
    expect(allowLogOnlyLeads({})).toBe(false);
    expect(allowLogOnlyLeads({ ALLOW_LOG_ONLY_LEADS: "true" })).toBe(true);
  });

  it("blocker message is honest", () => {
    expect(deliveryBlockerMessage().toLowerCase()).toMatch(/not configured/);
  });
});
