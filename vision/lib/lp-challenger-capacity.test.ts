import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  CAPACITY_CHALLENGER_ID,
  CAPACITY_CHALLENGER_PATHS,
  TEAMMATE_CHALLENGER_PATHS,
  TIME_CHALLENGER_PATHS,
  capacityChallengerCopy,
  challengerCopy,
} from "../config/lp-challenger-capacity";
import { chipClickIsFormStart, shouldStartEmployerFormOnPii } from "./guided-match";

describe("capacity challenger preview", () => {
  it("keeps live money routes untouched and isolates preview paths", () => {
    expect(CAPACITY_CHALLENGER_PATHS.us).toBe("/us/capacity");
    expect(CAPACITY_CHALLENGER_PATHS.au).toBe("/au/capacity");
    expect(CAPACITY_CHALLENGER_ID).toBe("capacity-a");
    const usPage = readFileSync(join(__dirname, "../app/us/page.tsx"), "utf8");
    const auPage = readFileSync(join(__dirname, "../app/au/page.tsx"), "utf8");
    expect(usPage).not.toContain("CapacityChallengerLanding");
    expect(auPage).not.toContain("CapacityChallengerLanding");
    expect(usPage).toContain('path: "/us"');
    expect(auPage).toContain('path: "/au"');
  });

  it("localises US vs AU without changing form_start rules", () => {
    const us = capacityChallengerCopy("us");
    const au = capacityChallengerCopy("au");
    expect(us.h1).toContain("without another expensive local hire");
    expect(us.lead).toContain("US business hours");
    expect(us.lead).toContain("payroll");
    expect(us.phoneDisplay).toBe("(888) 964-8644");
    expect(au.lead).toContain("Australian business hours");
    expect(au.lead).toContain("employment administration");
    expect(au.phoneDisplay).toBe("1300 886 740");
    expect(us.proofStrip).toContain("Save up to 80% of staffing costs");
    expect(us.proofStrip).toContain("No recruitment fees");
    expect(chipClickIsFormStart()).toBe(false);
    expect(shouldStartEmployerFormOnPii(false)).toBe(true);
    expect(shouldStartEmployerFormOnPii(true)).toBe(false);
  });

  it("does not use em dashes in challenger copy", () => {
    const blob = JSON.stringify([
      capacityChallengerCopy("us"),
      capacityChallengerCopy("au"),
      challengerCopy("time", "us"),
      challengerCopy("teammate", "au"),
    ]);
    expect(blob).not.toMatch(/\u2014|&mdash;/);
  });

  it("keeps time and teammate paths off category slugs with distinct headlines", () => {
    expect(TIME_CHALLENGER_PATHS.us).toBe("/us/time");
    expect(TIME_CHALLENGER_PATHS.au).toBe("/au/time");
    expect(TEAMMATE_CHALLENGER_PATHS.us).toBe("/us/teammate");
    expect(TEAMMATE_CHALLENGER_PATHS.au).toBe("/au/teammate");
    expect(challengerCopy("time", "us").h1).toContain("mornings");
    expect(challengerCopy("teammate", "us").h1).toContain("not another freelancer");
    expect(challengerCopy("time", "us").phoneDisplay).toBe("(888) 964-8644");
    expect(challengerCopy("teammate", "au").phoneDisplay).toBe("1300 886 740");
    expect(challengerCopy("capacity", "us").h1).toBe(capacityChallengerCopy("us").h1);
  });
});
