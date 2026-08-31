import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  GUIDED_MATCH_ROLES,
  JOB_SEEKER_LINE,
  buildHiringMessage,
  firstGuidedMatchStep,
  hoursDefaultForMarket,
  roleForCategory,
  roleHeadline,
} from "../config/guided-match";
import {
  canGoBack,
  chipClickIsFormStart,
  diagnosticMatchPayload,
  guidedMatchLandingFlags,
  guidedMatchStepIndex,
  previousStep,
  shouldStartEmployerFormOnPii,
} from "./guided-match";
import { LP_VERSION } from "./tracking";

describe("guided-match contract", () => {
  it("keeps the existing form_lp conversion flags and lp_version", () => {
    const flags = guidedMatchLandingFlags();
    expect(flags.lp_surface).toBe("form");
    expect(flags.cta_mode).toBe("form_primary");
    expect(flags.landing_type).toBe("form_lp");
    expect(flags.lp_variant).toBe("");
    expect(flags.lp_version).toBe(LP_VERSION);
    expect(LP_VERSION).toBe("stage1-v8");
  });

  it("includes Other / Not sure on Core and skips the chooser on role pages", () => {
    expect(GUIDED_MATCH_ROLES.some((r) => r.chip === "Other / Not sure")).toBe(
      true,
    );
    expect(GUIDED_MATCH_ROLES.find((r) => r.id === "other")?.category).toBe("");
    expect(firstGuidedMatchStep(null)).toBe("role");
    expect(firstGuidedMatchStep("bookkeeping")).toBe("needs");
    expect(firstGuidedMatchStep("accounting")).toBe("needs");
    expect(roleForCategory("accounting").formLabel).toBe("Accounting support");
  });

  it("defaults hours by market without a US vs AU force-choice", () => {
    expect(hoursDefaultForMarket("us")).toBe("US business hours");
    expect(hoursDefaultForMarket("au")).toBe("AU business hours");
    expect(buildHiringMessage({ hoursDefault: "US business hours" })).toBe(
      "Hours requested: US business hours",
    );
    expect(
      buildHiringMessage({
        hoursDefault: "US business hours",
        timezoneNote: "Pacific",
      }),
    ).toContain("Time zone notes: Pacific");
  });

  it("keeps diagnostic quiz events off Ads Primary", () => {
    const p = diagnosticMatchPayload({
      market: "us",
      category: "bookkeeping",
      step: "1",
      answer: "Bookkeeping",
      rolePreselected: true,
    });
    expect(p.assist_type).toBe("guided_match");
    expect(p.ads_conversion).toBe(false);
    expect(p.bidding_primary).toBe(false);
    expect(p.role_preselected).toBe(true);
    expect(chipClickIsFormStart()).toBe(false);
    expect(shouldStartEmployerFormOnPii(false)).toBe(true);
    expect(shouldStartEmployerFormOnPii(true)).toBe(false);
  });

  it("progresses Core 3 steps and role pages 2 steps with Back", () => {
    expect(guidedMatchStepIndex("role")).toEqual({
      shown: 1,
      total: 3,
      pct: "33%",
    });
    expect(guidedMatchStepIndex("needs", "bookkeeping")).toEqual({
      shown: 1,
      total: 2,
      pct: "50%",
    });
    expect(canGoBack("role")).toBe(false);
    expect(canGoBack("needs", "bookkeeping")).toBe(false);
    expect(canGoBack("contact", "bookkeeping")).toBe(true);
    expect(previousStep("contact", "bookkeeping")).toBe("needs");
    expect(previousStep("needs", null)).toBe("role");
    expect(canGoBack("contact", null, true)).toBe(false);
    expect(guidedMatchStepIndex("contact", null, true).total).toBe(1);
  });

  it("counts sequential staffing-partner screens honestly", () => {
    expect(guidedMatchStepIndex("role", null, false, true)).toEqual({
      shown: 1,
      total: 5,
      pct: "20%",
    });
    expect(guidedMatchStepIndex("hours", null, false, true)).toEqual({
      shown: 2,
      total: 5,
      pct: "40%",
    });
    expect(guidedMatchStepIndex("people", null, false, true)).toEqual({
      shown: 3,
      total: 5,
      pct: "60%",
    });
    expect(guidedMatchStepIndex("size", null, false, true)).toEqual({
      shown: 4,
      total: 5,
      pct: "80%",
    });
    expect(guidedMatchStepIndex("contact", null, false, true)).toEqual({
      shown: 5,
      total: 5,
      pct: "100%",
    });
    expect(previousStep("people", null, true)).toBe("hours");
    expect(previousStep("hours", null, true)).toBe("role");
    expect(previousStep("contact", null, true)).toBe("size");
    expect(canGoBack("hours", null, false, true)).toBe(true);
    expect(canGoBack("role", null, false, true)).toBe(false);
    expect(firstGuidedMatchStep("bookkeeping", true)).toBe("hours");
    expect(firstGuidedMatchStep("bookkeeping")).toBe("needs");
  });

  it("uses approved hire headlines and the job-seeker line", () => {
    expect(roleHeadline({ market: "us" }).h1).toBe(
      "Hire reliable Filipino staff who work your hours.",
    );
    expect(roleHeadline({ market: "au" }).h1).toMatch(/Australian hours/);
    expect(JOB_SEEKER_LINE).toBe(
      "Looking for work? View careers in the Philippines →",
    );
  });

  it("keeps GuidedMatchGate defaults off unless baseline opts in", () => {
    const gate = readFileSync(
      join(__dirname, "..", "app/components/GuidedMatchGate.tsx"),
      "utf8",
    );
    expect(gate).toContain("includeGateId = true");
    expect(gate).toContain("explicitContinue = false");
    expect(gate).toContain("sequentialNeeds = false");
    expect(gate).toContain("hoursQuestionSplit = false");
    expect(gate).toContain("spQuiz = false");
    expect(gate).toContain("allowRoleChange = false");
    expect(gate).toContain('name="company"');
    expect(gate).toContain("required");
    expect(gate).toContain("Enter your company name.");
    const us = readFileSync(join(__dirname, "..", "app/us/page.tsx"), "utf8");
    expect(us).toContain("StaffingBaselineLanding");
    expect(us).not.toContain("GuidedMatchLanding");
  });

  it("does not ship internal mock language or seat jargon", () => {
    const files = [
      "config/guided-match.ts",
      "app/components/GuidedMatchLanding.tsx",
      "app/components/GuidedMatchGate.tsx",
    ].map((rel) => readFileSync(join(__dirname, "..", rel), "utf8").toLowerCase());
    const blob = files.join("\n");
    for (const banned of [
      "stage 1",
      "mock form",
      "review controls",
      "unverified",
      "top 1%",
      "lead api is mock",
      "what does the bookkeeping seat",
      "reviews the seat",
    ]) {
      expect(blob.includes(banned), banned).toBe(false);
    }
  });
});
