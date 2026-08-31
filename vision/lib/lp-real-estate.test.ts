import { describe, expect, it } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { CATEGORY_SLUGS } from "../config/categories";
import {
  BASELINE_LP_VARIANT,
  BASELINE_LP_VERSION,
} from "../config/lp-baseline";
import {
  REAL_ESTATE_FORM_LABEL,
  REAL_ESTATE_PATH,
  REAL_ESTATE_SLUG,
  buildRealEstateRoute,
  isRealEstateSlug,
} from "../config/lp-real-estate";
import { roleForCategory } from "../config/guided-match";

const ROOT = join(__dirname, "..");

describe("US real-estate vertical LP", () => {
  it("is US-only and is not a shared category slug", () => {
    expect(CATEGORY_SLUGS).not.toContain("real-estate");
    expect(existsSync(join(ROOT, "app/us/real-estate/page.tsx"))).toBe(true);
    expect(existsSync(join(ROOT, "app/au/real-estate/page.tsx"))).toBe(false);
    const us = readFileSync(join(ROOT, "app/us/page.tsx"), "utf8");
    expect(us).toContain("StaffingBaselineLanding");
    expect(us).not.toContain("TrustFirstUsPage");
    expect(us).not.toContain("real-estate");
  });

  it("keeps live /us/real-estate on the previous baseline template", () => {
    const page = readFileSync(join(ROOT, "app/us/real-estate/page.tsx"), "utf8");
    const tf = readFileSync(join(ROOT, "app/us/tf/real-estate/page.tsx"), "utf8");
    expect(page).toContain("StaffingBaselineLanding");
    expect(page).toContain("real-estate");
    expect(page).not.toContain("TrustFirstUsPage");
    expect(tf).toContain("TrustFirstUsPage");
    expect(tf).toContain("real-estate");
    expect(page).not.toContain("GuidedMatchLanding");
    const cfg = buildRealEstateRoute("us");
    expect(cfg.h1).toBe("Hire a Real Estate Virtual Assistant");
    expect(cfg.route).toBe(REAL_ESTATE_PATH);
    expect(cfg.rate_text).toBe("");
    expect(cfg.h1).not.toMatch(/\$/);
    expect(cfg.supporting_copy).not.toMatch(/\$/);
    expect(cfg.lp_version).toBe(BASELINE_LP_VERSION);
    expect(cfg.lp_variant).toBe(BASELINE_LP_VARIANT);
    expect(cfg.role_tasks.length).toBe(6);
    expect(cfg.supporting_copy).toMatch(/brokerages/i);
    expect(cfg.supporting_copy).toMatch(/investors/i);
    expect(cfg.supporting_copy).toMatch(/property managers/i);
    expect(JSON.stringify(cfg)).not.toMatch(/\u2014/);
    expect(JSON.stringify(cfg).toLowerCase()).not.toContain("appfolio");
    expect(JSON.stringify(cfg).toLowerCase()).not.toContain("looking for a va");
  });

  it("locks the employer form to real-estate support", () => {
    expect(isRealEstateSlug(REAL_ESTATE_SLUG)).toBe(true);
    const role = roleForCategory(REAL_ESTATE_SLUG);
    expect(role.formLabel).toBe(REAL_ESTATE_FORM_LABEL);
    expect(role.chip).toBe("Real estate");
    const landing = readFileSync(
      join(ROOT, "app/components/StaffingBaselineLanding.tsx"),
      "utf8",
    );
    expect(landing).toContain("exitToCareers");
    expect(landing).toContain("GuidedMatchGate");
  });
});
