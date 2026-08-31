import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { staffingAgencyCopy, STAFFING_AGENCY_PATH } from "../config/lp-staffing-agency";
import { CATEGORY_SLUGS } from "../config/categories";

const ROOT = join(__dirname, "..");

describe("US staffing-agency candidate", () => {
  it("keeps /us/staffing as the unused noindex candidate, not trust-first", () => {
    expect(STAFFING_AGENCY_PATH).toBe("/us/staffing");
    expect(CATEGORY_SLUGS).not.toContain("staffing");
    const us = readFileSync(join(ROOT, "app/us/page.tsx"), "utf8");
    const candidate = readFileSync(join(ROOT, "app/us/staffing/page.tsx"), "utf8");
    expect(us).toContain("StaffingBaselineLanding");
    expect(us).not.toContain("TrustFirstUsPage");
    expect(candidate).toContain("StaffingBaselineLanding");
    expect(candidate).toContain('profile="staffing_agency"');
    expect(candidate).toContain("indexable: false");
    expect(candidate).not.toContain("TrustFirstUsPage");
  });

  it("explains the staffing model without invented prices or guarantees", () => {
    const copy = staffingAgencyCopy();
    const blob = JSON.stringify(copy).toLowerCase();
    expect(copy.h1).toMatch(/dedicated Filipino staff/i);
    expect(copy.supporting_copy).toMatch(/recruits and vets/i);
    expect(copy.supporting_copy).toMatch(/interview/i);
    expect(copy.supporting_copy).toMatch(/employ/i);
    expect(copy.supporting_copy).toMatch(/not a gig marketplace/i);
    expect(copy.howLead).toMatch(/20 hours/i);
    expect(blob).not.toMatch(/\$7/);
    expect(blob).not.toMatch(/\$4/);
    expect(blob).not.toMatch(/guaranteed/);
    expect(blob).not.toMatch(/top 1%/);
  });
});
