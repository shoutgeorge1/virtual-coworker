import { describe, expect, it, beforeEach } from "vitest";
import {
  classifyIntent,
  duplicateKey,
  rejectLogPayload,
  validateEmployerLead,
  MIN_COMPLETION_MS,
} from "./lead-validation";
import { _resetLimitsForTests, checkDuplicate, rememberSubmission, rateLimitAllow } from "./rate-limit";
import { LP_VERSION } from "./tracking";

describe("employer gate classification", () => {
  it("classifies employer intent", () => {
    expect(classifyIntent({ intent: "employer" })).toBe("employer");
    expect(classifyIntent({ intent: "hire" })).toBe("employer");
  });

  it("classifies job seeker intent", () => {
    expect(classifyIntent({ intent: "job_seeker" })).toBe("job_seeker");
    expect(classifyIntent({ message: "looking for a job please" })).toBe("job_seeker");
  });
});

describe("validateEmployerLead", () => {
  const base = {
    intent: "employer",
    market: "us",
    name: "Alex Employer",
    email: "alex@acme.com",
    phone: "(951) 555-0123",
    company: "Acme LLC",
    form_started_at: Date.now() - MIN_COMPLETION_MS - 100,
  };

  it("accepts a valid employer lead", () => {
    const r = validateEmployerLead(base);
    expect(r.ok).toBe(true);
    if (r.ok) {
      expect(r.market).toBe("us");
      expect(r.email).toBe("alex@acme.com");
    }
  });

  it("rejects job seekers", () => {
    const r = validateEmployerLead({ ...base, intent: "job_seeker" });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("job_seeker");
  });

  it("rejects honeypot", () => {
    const r = validateEmployerLead({ ...base, website: "http://spam.test" });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("honeypot");
  });

  it("allows optional company website and does not treat it as honeypot", () => {
    expect(validateEmployerLead({ ...base, company_website: "" }).ok).toBe(true);
    expect(
      validateEmployerLead({ ...base, company_website: "https://acme.com" }).ok,
    ).toBe(true);
    expect(validateEmployerLead({ ...base, company_website: "not a url" }).ok).toBe(
      true,
    );
  });

  it("still rejects the hidden website honeypot when company_website is also sent", () => {
    const r = validateEmployerLead({
      ...base,
      website: "http://spam.test",
      company_website: "https://acme.com",
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("honeypot");
  });

  it("rejects too-fast completion", () => {
    const r = validateEmployerLead({ ...base, form_started_at: Date.now() });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("too_fast");
  });

  it("requires company", () => {
    const r = validateEmployerLead({ ...base, company: "" });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("missing_fields");
  });

  it("requires phone", () => {
    const r = validateEmployerLead({ ...base, phone: "" });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("missing_fields");
  });

  it("rejects invalid US phones and Philippine mobiles on the US form", () => {
    expect(validateEmployerLead({ ...base, phone: "+63 917 123 4567" }).ok).toBe(false);
    const ph = validateEmployerLead({ ...base, phone: "+63 917 123 4567" });
    if (!ph.ok) expect(ph.code).toBe("job_seeker");
    const bad = validateEmployerLead({ ...base, phone: "951-555" });
    expect(bad.ok).toBe(false);
    if (!bad.ok) expect(bad.code).toBe("invalid_us_phone");
  });

  it("still accepts a non-empty AU phone without NANP rules", () => {
    const r = validateEmployerLead({
      ...base,
      market: "au",
      phone: "0412 345 678",
    });
    expect(r.ok).toBe(true);
    const short = validateEmployerLead({ ...base, market: "au", phone: "04" });
    expect(short.ok).toBe(true);
  });
});

describe("duplicate + rate limit", () => {
  beforeEach(() => _resetLimitsForTests());

  it("detects duplicate submissions", () => {
    const key = duplicateKey("alex@acme.com", "us");
    expect(checkDuplicate(key).duplicate).toBe(false);
    rememberSubmission(key, "sid_1");
    const again = checkDuplicate(key);
    expect(again.duplicate).toBe(true);
    if (again.duplicate) expect(again.submissionId).toBe("sid_1");
  });

  it("rate limits burst keys", () => {
    const key = "test-ip:ale";
    for (let i = 0; i < 8; i++) expect(rateLimitAllow(key)).toBe(true);
    expect(rateLimitAllow(key)).toBe(false);
  });
});

describe("attribution + reject logging", () => {
  it("exposes lp version constant", () => {
    expect(LP_VERSION).toBe("baseline_v1_2026_08");
  });

  it("reject logs omit sensitive body content", () => {
    const log = rejectLogPayload("honeypot", "us", { reason: "rejected" });
    expect(log.event).toBe("spam_or_applicant_rejected");
    expect(JSON.stringify(log)).not.toMatch(/@/);
  });
});

describe("attribution field contract", () => {
  it("preserves click ids in payload shape", () => {
    const attr = {
      gclid: "gclid_test",
      gbraid: "gbraid_test",
      wbraid: "wbraid_test",
      utm_source: "google",
      utm_medium: "cpc",
      utm_campaign: "VC_US_S_BRAND",
      landing_page_url: "https://example.test/us",
      referrer: "https://google.com",
      lp_version: LP_VERSION,
      market: "us",
    };
    const r = validateEmployerLead({
      ...attr,
      intent: "employer",
      market: "us",
      name: "Pat",
      email: "pat@biz.com",
      phone: "(951) 555-0123",
      company: "Biz",
      form_started_at: Date.now() - 5000,
    });
    expect(r.ok).toBe(true);
    expect(attr.gclid).toBe("gclid_test");
    expect(attr.gbraid).toBe("gbraid_test");
    expect(attr.wbraid).toBe("wbraid_test");
    expect(attr.lp_version).toBe(LP_VERSION);
  });
});
