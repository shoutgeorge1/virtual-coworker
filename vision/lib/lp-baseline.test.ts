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
    expect(BASELINE_LABEL).toBe("US_BASELINE_2026-08-18");
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

  it("keeps US CORE price-led H1 and pins AU CORE to Australian hours", () => {
    const us = buildBaselineRoute({ market: "us" });
    const au = buildBaselineRoute({ market: "au" });
    expect(us.h1.replace(/\u200b/g, "")).toBe(
      "Hire Dedicated Filipino Remote Staff From $7/Hour",
    );
    expect(au.h1).toBe(
      "Hire Dedicated Filipino Remote Staff Who Work Australian Hours",
    );
    expect(au.h1).not.toMatch(/\$/);
    expect(au.eyebrow).toBe("Dedicated Filipino Remote Staff");
  });

  it("uses RSA hours language on role H1s and omits $ from the first screen", () => {
    const books = buildBaselineRoute({ market: "us", role: "bookkeeping" });
    expect(books.h1).toBe(
      "Hire a Dedicated Filipino Bookkeeper Who Works Your Hours",
    );
    expect(books.h1).not.toMatch(/\$/);
    expect(books.supporting_copy).not.toMatch(/\$/);
    expect(books.rate_text).toBe("");

    const auAdmin = buildBaselineRoute({
      market: "au",
      role: "administrative-support",
    });
    expect(auAdmin.h1).toBe(
      "Hire a Dedicated Filipino Executive Assistant Who Works Australian Hours",
    );
    expect(auAdmin.h1).not.toMatch(/\$/);
    expect(auAdmin.supporting_copy).toMatch(/Australian hours/);
    expect(auAdmin.supporting_copy).not.toMatch(/\$/);

    const admin = buildBaselineRoute({
      market: "us",
      role: "administrative-support",
    });
    expect(admin.h1).toBe(
      "Hire a Dedicated Filipino Executive Assistant Who Works Your Hours",
    );
    expect(US_PUBLISHED_RATES["administrative-support"]?.rateHour).toBeNull();

    const usCs = buildBaselineRoute({ market: "us", role: "customer-service" });
    const auCs = buildBaselineRoute({ market: "au", role: "customer-service" });
    expect(usCs.h1).toBe(
      "Hire Dedicated Filipino Customer Support Staff Who Work Your Hours",
    );
    expect(auCs.h1).toBe(
      "Hire Dedicated Filipino Customer Support Staff Who Work Australian Hours",
    );
    expect(usCs.h1).not.toMatch(/Customer Support Who/);

    const usSales = buildBaselineRoute({ market: "us", role: "sales" });
    expect(usSales.h1).toBe(
      "Hire Dedicated Filipino Sales Support Staff Who Work Your Hours",
    );
    expect(usSales.h1).not.toMatch(/Sales Support Who/);

    const usHr = buildBaselineRoute({ market: "us", role: "hr" });
    expect(usHr.h1).toBe(
      "Hire a Dedicated Filipino HR Assistant Who Works Your Hours",
    );
    expect(usHr.h1).not.toMatch(/HR Support Who/);

    for (const slug of CATEGORY_SLUGS) {
      const usRole = buildBaselineRoute({ market: "us", role: slug });
      const auRole = buildBaselineRoute({ market: "au", role: slug });
      const collective = Boolean(US_PUBLISHED_RATES[slug]?.collective);
      const usHours = collective
        ? /Who Work Your Hours/
        : /Who Works Your Hours/;
      const auHours = collective
        ? /Who Work Australian Hours/
        : /Who Works Australian Hours/;
      expect(usRole.h1).toMatch(/Dedicated Filipino/);
      expect(usRole.h1).toMatch(usHours);
      expect(usRole.h1).not.toMatch(/\$/);
      expect(usRole.h1).not.toMatch(/\u2014|&mdash;/);
      expect(usRole.supporting_copy).not.toMatch(/\$/);
      expect(usRole.rate_text).toBe("");
      expect(auRole.h1).toMatch(auHours);
      expect(auRole.h1).not.toMatch(/\$/);
      expect(auRole.rate_text).toBe("");
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
    expect(landing).toContain("exitToCareers");
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

  it("does not wire an H1 traffic split", () => {
    const src = readFileSync(join(ROOT, "config/lp-baseline.ts"), "utf8");
    expect(src).not.toMatch(/vc_exp/);
    expect(src).not.toMatch(/Math\.random/);
    expect(src).not.toMatch(/experiment_id/);
  });

  it("does not invent competitor prices or em dashes in baseline copy", () => {
    const blob = JSON.stringify({
      us: buildBaselineRoute({ market: "us" }),
      au: buildBaselineRoute({ market: "au" }),
      usCs: buildBaselineRoute({ market: "us", role: "customer-service" }),
      usSales: buildBaselineRoute({ market: "us", role: "sales" }),
      shared: baselineSharedCopy("us"),
    }).toLowerCase();
    expect(blob).not.toMatch(/\$4/);
    expect(blob).not.toMatch(/80%/);
    expect(blob).not.toMatch(/\u2014|&mdash;/);
    expect(blob).not.toContain("upwork");
    expect(blob).not.toContain("guaranteed");
  });
});
