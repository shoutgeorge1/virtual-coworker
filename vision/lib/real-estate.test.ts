import { describe, expect, it } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import {
  REAL_ESTATE_H1,
  REAL_ESTATE_PATH,
  REAL_ESTATE_ROLE_CARDS,
  REAL_ESTATE_SUPPORTING,
  buildRealEstateRoute,
} from "../config/real-estate";
import { TRUST_FIRST_PAGES } from "../config/trust-first";
import { CATEGORY_SLUGS } from "../config/categories";
import { sitemapPaths } from "./seo";

const ROOT = join(__dirname, "..");
const BANNED_RE = /cold call|appointment setter|appointment setting|\bisa\b|pay per lead|pay-per-lead|cost per lead|commission-only|lead buying/i;

describe("US real-estate industry page", () => {
  it("is not a 10th paid category slug", () => {
    expect(CATEGORY_SLUGS).not.toContain("real-estate");
    expect(CATEGORY_SLUGS).toHaveLength(9);
  });

  it("ships a US-only production route", () => {
    expect(existsSync(join(ROOT, "app/us/real-estate/page.tsx"))).toBe(true);
    expect(existsSync(join(ROOT, "app/au/real-estate/page.tsx"))).toBe(false);
    const page = readFileSync(join(ROOT, "app/us/real-estate/page.tsx"), "utf8");
    expect(page).toContain("StaffingBaselineLanding");
    expect(page).toContain("buildRealEstateRoute");
    expect(sitemapPaths().some((row) => row.path === REAL_ESTATE_PATH)).toBe(true);
  });

  it("names the five supported seats and keeps generic Real Estate VA out of the H1", () => {
    const titles = REAL_ESTATE_ROLE_CARDS.map((role) => role.title);
    expect(titles).toEqual([
      "Assistant Property Manager",
      "Guest Relations Specialist",
      "Lead Generation",
      "Bookkeeper",
      "Executive Assistant",
    ]);
    expect(REAL_ESTATE_H1).not.toMatch(/real estate virtual assistant/i);
    expect(REAL_ESTATE_H1).not.toMatch(BANNED_RE);
    expect(REAL_ESTATE_H1).toMatch(/Property Staff/);
    expect(REAL_ESTATE_H1).toMatch(/Your Hours/);
    expect(REAL_ESTATE_H1).not.toMatch(/\$/);
  });

  it("does not sell cold calling, ISAs, or lead-buying", () => {
    const route = buildRealEstateRoute();
    const offer = [route.h1, ...route.role_tasks.map((role) => role.title)].join("\n");
    expect(offer).not.toMatch(BANNED_RE);
    expect(REAL_ESTATE_SUPPORTING).toMatch(/staffing hire/i);
    expect(REAL_ESTATE_SUPPORTING).toMatch(/not a cold-calling desk/i);
    expect(REAL_ESTATE_SUPPORTING).toMatch(/not a lead-buying service/i);
    expect(route.rate_text).toBe("");
  });

  it("keeps the trust-first challenger on the same supported seats", () => {
    const page = TRUST_FIRST_PAGES["real-estate"];
    expect(page.h1).not.toMatch(/real estate virtual assistant/i);
    expect(page.h1).not.toMatch(BANNED_RE);
    expect(page.roles.map((role) => role.title)).toEqual([
      "Assistant Property Manager",
      "Guest Relations Specialist",
      "Lead Generation",
      "Bookkeeper",
      "Executive Assistant",
    ]);
    const blob = JSON.stringify(page);
    expect(blob).toMatch(/not a lead-buying/i);
    expect(blob).not.toMatch(/Appointment support is available/i);
  });
});
