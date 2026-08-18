import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  BASELINE_HOME_ALIASES,
  BASELINE_LABEL,
  BASELINE_LP_VARIANT,
  BASELINE_LP_VERSION,
  US_PUBLISHED_RATES,
  baselineSharedCopy,
  buildBaselineRoute,
} from "../config/lp-baseline";
import { CATEGORY_SLUGS } from "../config/categories";

const ROOT = join(__dirname, "..");

describe("Paid Landing Page Baseline v1 — August 2026", () => {
  it("labels the production baseline (not a winning A/B variant)", () => {
    expect(BASELINE_LABEL).toBe("Paid Landing Page Baseline v1 - August 2026");
    expect(BASELINE_LP_VERSION).toBe("baseline_v1_2026_08");
    expect(BASELINE_LP_VARIANT).toBe("price_staffing_v1");
  });

  it("ships StaffingBaselineLanding on live /us and /au", () => {
    const us = readFileSync(join(ROOT, "app/us/page.tsx"), "utf8");
    const au = readFileSync(join(ROOT, "app/au/page.tsx"), "utf8");
    expect(us).toContain("StaffingBaselineLanding");
    expect(au).toContain("StaffingBaselineLanding");
    expect(us).not.toContain("GuidedMatchLanding");
    expect(au).not.toContain("GuidedMatchLanding");
  });

  it("shares the same template on role pages", () => {
    const usRole = readFileSync(join(ROOT, "app/us/[category]/page.tsx"), "utf8");
    const auRole = readFileSync(join(ROOT, "app/au/[category]/page.tsx"), "utf8");
    expect(usRole).toContain("StaffingBaselineLanding");
    expect(auRole).toContain("StaffingBaselineLanding");
    expect(usRole).not.toContain("GuidedMatchLanding");
  });

  it("keeps US CORE price-led H1 and omits unverified AU $7", () => {
    const us = buildBaselineRoute({ market: "us" });
    const au = buildBaselineRoute({ market: "au" });
    expect(us.h1.replace(/\u200b/g, "")).toBe(
      "Hire Dedicated Filipino Remote Staff From $7/Hour",
    );
    expect(au.h1).toBe("Hire Dedicated Filipino Remote Staff");
    expect(au.h1).not.toMatch(/\$/);
  });

  it("applies published role rates only when a single rate is verified", () => {
    const books = buildBaselineRoute({ market: "us", role: "bookkeeping" });
    expect(books.h1.replace(/\u200b/g, "")).toContain("Bookkeeper From $8/Hour");
    const admin = buildBaselineRoute({
      market: "us",
      role: "administrative-support",
    });
    expect(admin.h1).not.toMatch(/\$/);
    expect(US_PUBLISHED_RATES["administrative-support"]?.rateHour).toBeNull();
    for (const slug of CATEGORY_SLUGS) {
      const au = buildBaselineRoute({ market: "au", role: slug });
      expect(au.h1).not.toMatch(/\$/);
    }
  });

  it("restores logos + LinkedIn immediately after hero, with stars in hero", () => {
    const landing = readFileSync(
      join(ROOT, "app/components/StaffingBaselineLanding.tsx"),
      "utf8",
    );
    const heroEnd = landing.indexOf("</section>");
    const logos = landing.indexOf('className="gm-logos"');
    const stories = landing.indexOf('id="stories"');
    const stars = landing.indexOf("sp-hero-stars");
    expect(stars).toBeGreaterThan(-1);
    expect(stars).toBeLessThan(heroEnd);
    expect(logos).toBeGreaterThan(heroEnd);
    expect(logos).toBeLessThan(stories);
    expect(landing).toContain("linkedin} LinkedIn");
    expect(landing).toContain("sceneSrc");
    expect(landing).toContain("teamSrc");
    expect(landing).toContain("closerSrc");
    expect(landing).not.toContain("Upwork");
  });

  it("keeps JOB_SEEKER_LINE secondary near quiz and footer (no hard gate)", () => {
    const landing = readFileSync(
      join(ROOT, "app/components/StaffingBaselineLanding.tsx"),
      "utf8",
    );
    const gate = readFileSync(
      join(ROOT, "app/components/GuidedMatchGate.tsx"),
      "utf8",
    );
    expect(landing).toContain("seekerLine");
    expect(landing).toContain("job_seeker_redirected");
    expect(landing).not.toContain("employer-only");
    expect(gate).toContain("JOB_SEEKER_LINE");
    expect(gate).toContain("Seeker");
  });

  it("uses sequential quiz + phone closer, not role chips in hero", () => {
    const landing = readFileSync(
      join(ROOT, "app/components/StaffingBaselineLanding.tsx"),
      "utf8",
    );
    const hero = landing.slice(
      landing.indexOf('className="gm-hero"'),
      landing.indexOf('className="gm-logos"'),
    );
    expect(hero).toContain("{copy.primaryCta}");
    expect(hero).toContain("sp-hero-cta");
    expect(hero).not.toContain("GuidedMatchGate");
    expect(hero).not.toContain("gm-chip");
    expect(landing).toContain("sequentialNeeds");
    expect(landing).toContain("{copy.finalTitle}");
    expect(landing).toContain("finalPhoneCta");
  });

  it("stays lean: no FAQ wall, no dual competing CTAs, no infocall clutter", () => {
    const landing = readFileSync(
      join(ROOT, "app/components/StaffingBaselineLanding.tsx"),
      "utf8",
    );
    expect(landing).not.toMatch(/<details|Questions employers|faq|FAQ/i);
    expect(landing).not.toMatch(/Book an|infocall|Trustpilot/i);
    expect(landing).not.toContain("gm-cta-row");
    expect(landing).not.toContain('id="model"');
    expect(landing).not.toContain('id="faq"');
    // Exactly one form-scroll CTA class in hero; closer is phone-only.
    const hero = landing.slice(
      landing.indexOf('className="gm-hero"'),
      landing.indexOf('className="gm-logos"'),
    );
    expect((hero.match(/sp-hero-cta/g) || []).length).toBe(1);
    const closer = landing.slice(landing.indexOf('id="again"'));
    expect(closer).toContain("phone_href");
    expect(closer).not.toContain('href="#gate"');
  });

  it("redirects retired challenger aliases to market home", () => {
    expect(BASELINE_HOME_ALIASES).not.toContain("offer");
    for (const alias of BASELINE_HOME_ALIASES) {
      const us = readFileSync(join(ROOT, `app/us/${alias}/page.tsx`), "utf8");
      const au = readFileSync(join(ROOT, `app/au/${alias}/page.tsx`), "utf8");
      expect(us).toContain('redirectPreservingQuery("/us"');
      expect(au).toContain('redirectPreservingQuery("/au"');
    }
    const proto = readFileSync(
      join(ROOT, "app/prototype/staffing-partner/us/page.tsx"),
      "utf8",
    );
    expect(proto).toContain('redirectPreservingQuery("/us"');
  });

  it("does not invent competitor prices or em dashes in baseline copy", () => {
    const blob = JSON.stringify({
      us: buildBaselineRoute({ market: "us" }),
      au: buildBaselineRoute({ market: "au" }),
      shared: baselineSharedCopy("us"),
    }).toLowerCase();
    expect(blob).not.toMatch(/\$4/);
    expect(blob).not.toMatch(/80%/);
    expect(blob).not.toMatch(/\u2014|&mdash;/);
    expect(blob).not.toContain("upwork");
    expect(blob).not.toContain("guaranteed");
  });
});
