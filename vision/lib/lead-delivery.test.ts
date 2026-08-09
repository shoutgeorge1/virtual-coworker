import { describe, expect, it } from "vitest";
import {
  allowLogOnlyLeads,
  configuredChannels,
  deliveryBlockerMessage,
  durableTrafficChannels,
  formatLeadEmailText,
  parseLeadCc,
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

  it("parses CC list", () => {
    expect(parseLeadCc({ LEAD_EMAIL_CC: "a@x.com, b@y.com" })).toEqual([
      "a@x.com",
      "b@y.com",
    ]);
  });

  it("formats lead email like Gravity Forms style", () => {
    const text = formatLeadEmailText({
      firstName: "Ada",
      lastName: "Lovelace",
      email: "ada@example.com",
      phone: "555",
      company: "Analytical Engines",
      market: "us",
      utm_source: "google",
      gclid: "abc",
      submission_id: "vc_us_test",
    });
    expect(text).toContain("Name\n  Ada Lovelace");
    expect(text).toContain("Email Address\n  ada@example.com");
    expect(text).toContain("GCLID\n  abc");
    expect(text).toContain("Submission ID\n  vc_us_test");
  });

  it("includes modeled lead value without calling it revenue", () => {
    const text = formatLeadEmailText({
      firstName: "Ada",
      lastName: "Lovelace",
      email: "ada@example.com",
      company: "Analytical Engines",
      market: "us",
      company_size: "11-50",
      positions_needed: "2-3",
      lead_score: 61,
      estimated_lead_value: 420,
      value_kind: "estimated_modeled",
      submission_id: "vc_us_test",
    });
    expect(text).toContain("Company size\n  11-50");
    expect(text).toContain("Positions needed\n  2-3");
    expect(text).toContain("Modeled lead score (not revenue)\n  61");
    expect(text).toContain("website estimate only");
    expect(text.toLowerCase()).not.toContain("revenue\n  420");
  });
});
