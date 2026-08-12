import { describe, expect, it } from "vitest";
import {
  COMPANY_SIZE_OPTIONS,
  LEAD_VALUE_MODEL,
  POSITIONS_OPTIONS,
  scoreLeadFromSignals,
  scoreLeadValue,
} from "../config/lead-value";

describe("scoreLeadValue", () => {
  it("zeros job seekers", () => {
    const r = scoreLeadValue({ intent: "job_seeker" });
    expect(r.lead_score).toBe(0);
    expect(r.estimated_lead_value).toBe(0);
    expect(r.fit_label).toBe("Not a fit");
  });

  it("keeps unknown intent low", () => {
    const r = scoreLeadValue({ intent: "unknown" });
    expect(r.lead_score).toBeLessThan(30);
    expect(r.estimated_lead_value).toBeLessThan(100);
    expect(r.fit_label).toBe("Let’s discuss");
    expect(r.value_kind).toBe("estimated_modeled");
  });

  it("puts 1–10 / 1 seat near the modest base ($200–350)", () => {
    const r = scoreLeadValue({
      intent: "employer",
      companySize: "1-10",
      positionsNeeded: "1",
    });
    expect(r.estimated_lead_value).toBeGreaterThanOrEqual(200);
    expect(r.estimated_lead_value).toBeLessThanOrEqual(350);
    expect(r.fit_label).not.toBe("Strong fit");
  });

  it("scores a strong multi-seat SMB higher than a 1-seat micro", () => {
    const weak = scoreLeadValue({
      intent: "employer",
      companySize: "1-10",
      positionsNeeded: "1",
      urgencyBoost: 0.2,
    });
    const strong = scoreLeadValue({
      intent: "employer",
      companySize: "51-200",
      positionsNeeded: "4-10",
      urgencyBoost: 0.8,
    });
    expect(strong.lead_score).toBeGreaterThan(weak.lead_score);
    expect(strong.estimated_lead_value).toBeGreaterThan(weak.estimated_lead_value);
    expect(strong.estimated_lead_value).toBeLessThanOrEqual(LEAD_VALUE_MODEL.capUsd);
    expect(strong.lead_score).toBeLessThanOrEqual(100);
    expect(strong.value_kind).toBe("estimated_modeled");
    expect(strong.fit_label).toBe("Strong fit");
    expect(weak.fit_label).not.toBe("Strong fit");
  });

  it("uses positions as a bigger $ lever than company size", () => {
    const manySeatsTinyCo = scoreLeadValue({
      intent: "employer",
      companySize: "1-10",
      positionsNeeded: "4-10",
    });
    const oneSeatEnterprise = scoreLeadValue({
      intent: "employer",
      companySize: "201+",
      positionsNeeded: "1",
    });
    expect(manySeatsTinyCo.estimated_lead_value).toBeGreaterThan(
      oneSeatEnterprise.estimated_lead_value,
    );
  });

  it("does not over-score 201+ vs 51–200 at the same seat count", () => {
    const smb = scoreLeadValue({
      intent: "employer",
      companySize: "51-200",
      positionsNeeded: "2-3",
    });
    const enterprise = scoreLeadValue({
      intent: "employer",
      companySize: "201+",
      positionsNeeded: "2-3",
    });
    expect(smb.estimated_lead_value).toBeGreaterThan(enterprise.estimated_lead_value);
    expect(smb.lead_score).toBeGreaterThan(enterprise.lead_score);
  });

  it("caps exceptional multi-seat leads around $1k–$1.2k", () => {
    const r = scoreLeadValue({
      intent: "employer",
      companySize: "51-200",
      positionsNeeded: "11+",
      hiringTimeline: "asap",
    });
    expect(r.estimated_lead_value).toBeLessThanOrEqual(LEAD_VALUE_MODEL.capUsd);
    expect(r.estimated_lead_value).toBeGreaterThanOrEqual(1000);
  });

  it("treats 11–50 + 2–3 as the sweet zone", () => {
    const r = scoreLeadValue({
      intent: "employer",
      companySize: "11-50",
      positionsNeeded: "2-3",
    });
    expect(r.fit_label).toBe("Strong fit");
    expect(r.estimated_lead_value).toBeGreaterThan(500);
    expect(r.estimated_lead_value).toBeLessThan(900);
  });

  it("uses timeline urgency as a small modifier only", () => {
    const exploring = scoreLeadValue({
      intent: "employer",
      companySize: "11-50",
      positionsNeeded: "2-3",
      hiringTimeline: "exploring",
    });
    const asap = scoreLeadValue({
      intent: "employer",
      companySize: "11-50",
      positionsNeeded: "2-3",
      hiringTimeline: "asap",
    });
    expect(asap.lead_score).toBeGreaterThan(exploring.lead_score);
    expect(asap.estimated_lead_value).toBeGreaterThan(exploring.estimated_lead_value);
    const spread =
      (asap.estimated_lead_value - exploring.estimated_lead_value) /
      exploring.estimated_lead_value;
    expect(spread).toBeLessThan(0.2);
  });

  it("keeps missing chips modest, not $0", () => {
    const r = scoreLeadValue({ intent: "employer" });
    expect(r.estimated_lead_value).toBeGreaterThanOrEqual(
      LEAD_VALUE_MODEL.weakEmployerFloorUsd,
    );
    expect(r.estimated_lead_value).toBeLessThan(300);
    expect(r.fit_label).toBe("Let’s discuss");
  });

  it("exposes short tap chip labels", () => {
    expect(COMPANY_SIZE_OPTIONS.map((o) => o.label)).toEqual([
      "1–10 people",
      "11–50 people",
      "51–200 people",
      "201+ people",
    ]);
    expect(POSITIONS_OPTIONS.map((o) => o.label)).toEqual([
      "1 role",
      "2–3 roles",
      "4–10 roles",
      "11+ roles",
    ]);
  });
});

describe("scoreLeadFromSignals", () => {
  it("maps job_seeker aliases to zero", () => {
    expect(scoreLeadFromSignals({ intent: "applicant" }).estimated_lead_value).toBe(0);
  });

  it("scores employer payload fields", () => {
    const r = scoreLeadFromSignals({
      intent: "employer",
      company_size: "11-50",
      positions_needed: "2-3",
      hiring_timeline: "this-month",
    });
    expect(r.lead_score).toBeGreaterThan(40);
    expect(r.estimated_lead_value).toBeGreaterThan(200);
    expect(r.value_kind).toBe("estimated_modeled");
  });
});
