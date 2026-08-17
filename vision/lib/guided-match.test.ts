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

  it("uses approved hire headlines and the job-seeker line", () => {
    expect(roleHeadline({ market: "us" }).h1).toBe(
      "Hire reliable Filipino staff who work your hours.",
    );
    expect(roleHeadline({ market: "au" }).h1).toMatch(/Australian hours/);
    expect(JOB_SEEKER_LINE).toBe(
      "Looking for work? View careers in the Philippines →",
    );
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
