import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  SELL_FIRST_PATHS,
  SELL_FIRST_VARIANT,
  normalizeSellFirstHeadline,
  sellFirstCopy,
  sellFirstSlugCollidesWithCategory,
} from "../config/lp-sell-first";
import { CATEGORY_SLUGS } from "../config/categories";

const ROOT = join(__dirname, "..");

describe("sell-first fold challenger", () => {
  it("keeps sell-first config paths as aliases that redirect to baseline", () => {
    expect(SELL_FIRST_PATHS.us).toBe("/us/start");
    expect(SELL_FIRST_PATHS.au).toBe("/au/start");
    expect(SELL_FIRST_VARIANT).toBe("sell-first");
    expect(sellFirstSlugCollidesWithCategory()).toBe(false);
    expect(CATEGORY_SLUGS).not.toContain("start");
    const us = readFileSync(join(ROOT, "app/us/page.tsx"), "utf8");
    const au = readFileSync(join(ROOT, "app/au/page.tsx"), "utf8");
    expect(us).toContain("StaffingBaselineLanding");
    expect(au).toContain("StaffingBaselineLanding");
    expect(us).not.toContain("sellFirst");
    expect(au).not.toContain("sellFirst");
  });

  it("redirects /us/start and /au/start to market home (challenger retired)", () => {
    const usStart = readFileSync(join(ROOT, "app/us/start/page.tsx"), "utf8");
    const auStart = readFileSync(join(ROOT, "app/au/start/page.tsx"), "utf8");
    expect(usStart).toContain('redirectPreservingQuery("/us"');
    expect(auStart).toContain('redirectPreservingQuery("/au"');
    expect(usStart).not.toContain("sellFirst");
  });

  it("keeps fold CSS scoped so control /us is not restyled", () => {
    const css = readFileSync(join(ROOT, "app/sell-first.css"), "utf8");
    expect(css).toContain(".gm-sell");
    expect(css).toContain("min-height: 52px");
    expect(css).toContain(".gm-sell .gm-hero-grid");
    expect(css).not.toMatch(/^\.gm-hero-grid \{/m);
  });

  it("sells first: compact proof, no invented price, headline A/B ready", () => {
    const us = sellFirstCopy("us");
    const au = sellFirstCopy("au");
    expect(us.h1).toBe(
      "Hire experienced Filipino staff who work your hours.",
    );
    expect(au.h1).toMatch(/Australian hours/);
    expect(us.cta).toBe("Find my virtual assistant");
    expect(us.compactProof).toMatch(/5\.0 Google · 4\.9 Clutch/);
    expect(us.sinceLine).toMatch(/since 2011/);
    expect(us.lead).toMatch(/admin, bookkeeping, marketing, customer support/);
    expect(sellFirstCopy("us", "b").h1).toMatch(/Build your team/);
    expect(sellFirstCopy("us", "c").h1).toMatch(/slowing your business/);
    expect(sellFirstCopy("us", "d").h1).toMatch(/pre-vetted/);
    expect(normalizeSellFirstHeadline("b")).toBe("b");
    expect(normalizeSellFirstHeadline("nope")).toBe("a");
    expect(us.phoneDisplay).toBe("(888) 964-8644");
    expect(au.phoneDisplay).toBe("1300 886 740");
  });

  it("does not invent a live rate or use em dashes", () => {
    const blob = JSON.stringify([
      sellFirstCopy("us"),
      sellFirstCopy("au"),
      sellFirstCopy("us", "b"),
      sellFirstCopy("us", "c"),
      sellFirstCopy("us", "d"),
    ]);
    expect(blob).not.toMatch(/\$4|\$8|\$7/);
    expect(blob).not.toMatch(/\u2014|&mdash;/);
    expect(blob.toLowerCase()).not.toContain("outsourcing");
    expect(blob.toLowerCase()).not.toContain("bpo");
  });
});

describe("quiet quiz chrome on sell-first", () => {
  it("hides 1 of 3 until the visitor is in the quiz", () => {
    const gate = readFileSync(
      join(ROOT, "app/components/GuidedMatchGate.tsx"),
      "utf8",
    );
    expect(gate).toContain("quietStart");
    expect(gate).toContain("hideQuizChrome");
  });
});
