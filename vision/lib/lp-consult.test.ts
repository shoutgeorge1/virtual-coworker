import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  CONSULT_PATHS,
  CONSULT_VARIANT,
  consultCopy,
  consultSlugCollidesWithCategory,
} from "../config/lp-consult";
import { CATEGORY_SLUGS } from "../config/categories";
import { GUIDED_MATCH_HOURS_MINIMUM_NOTE } from "../config/guided-match";
import { PUBLIC_QUOTES } from "../config/site";

const ROOT = join(__dirname, "..");

describe("consult-truth employer LP", () => {
  it("keeps consult config paths as aliases that redirect to baseline", () => {
    expect(CONSULT_PATHS.us).toBe("/us/consult");
    expect(CONSULT_PATHS.au).toBe("/au/consult");
    expect(CONSULT_VARIANT).toBe("consult-truth");
    expect(consultSlugCollidesWithCategory()).toBe(false);
    expect(CATEGORY_SLUGS).not.toContain("consult");
    const us = readFileSync(join(ROOT, "app/us/page.tsx"), "utf8");
    const au = readFileSync(join(ROOT, "app/au/page.tsx"), "utf8");
    expect(us).toContain("StaffingBaselineLanding");
    expect(au).toContain("StaffingBaselineLanding");
    expect(us).not.toContain("ConsultLanding");
    expect(au).not.toContain("ConsultLanding");
  });

  it("redirects /us/consult and /au/consult to market home (challenger retired)", () => {
    const usConsult = readFileSync(join(ROOT, "app/us/consult/page.tsx"), "utf8");
    const auConsult = readFileSync(join(ROOT, "app/au/consult/page.tsx"), "utf8");
    expect(usConsult).toContain('redirectPreservingQuery("/us"');
    expect(auConsult).toContain('redirectPreservingQuery("/au"');
    expect(usConsult).not.toContain("ConsultLanding");
  });

  it("keeps ConsultLanding component available for reference", () => {
    const landing = readFileSync(
      join(ROOT, "app/components/ConsultLanding.tsx"),
      "utf8",
    );
    expect(landing).toContain("GuidedMatchGate");
    expect(landing).toContain("gm-consult");
    expect(landing).toContain("consult-landing.css");
  });

  it("keeps consult craft scoped and makes the quiz the first tap", () => {
    const css = readFileSync(join(ROOT, "app/consult-landing.css"), "utf8");
    expect(css).toContain(".gm-consult");
    expect(css).toContain(".gm-gate-card");
    expect(css).toContain("grid-template-columns: 1fr 1fr");
    expect(css).toContain("min-height: 52px");
    expect(css).toContain("font-size: 1.125rem");
    expect(css).not.toContain(".gm-hero-grid");
  });

  it("encodes consult pain, enquire reasons, value, and mix-ups", () => {
    const us = consultCopy("us");
    const au = consultCopy("au");
    expect(us.h1).toMatch(/maxed/i);
    expect(us.h1).not.toBe(
      "Hire reliable Filipino staff who work your hours.",
    );
    expect(us.pains.map((p) => p.t).join(" ")).toMatch(/capacity/i);
    expect(us.pains.map((p) => p.t).join(" ")).toMatch(/sensitive data/i);
    expect(us.pains.map((p) => p.d).join(" ")).toMatch(/Simple Practice|Klaviyo/);
    expect(au.pains.map((p) => p.t).join(" ")).toMatch(/AU and NZ/i);
    expect(us.enquire.map((e) => e.d).join(" ")).toMatch(/Reddit/i);
    expect(us.enquire.map((e) => e.t).join(" ")).toMatch(/generic VA/i);
    expect(us.values.map((v) => v.d).join(" ")).toMatch(/role-specific/);
    expect(us.values.map((v) => v.t).join(" ")).toMatch(/part-time/i);
    expect(us.values.map((v) => v.d).join(" ")).toContain(
      GUIDED_MATCH_HOURS_MINIMUM_NOTE,
    );
    expect(us.values.map((v) => v.d).join(" ")).toMatch(/13-month/);
    expect(us.values.map((v) => v.d).join(" ")).toMatch(/3-5 days/);
    expect(us.values.map((v) => v.d).join(" ")).toMatch(/1\.5-2 weeks/);
    expect(us.mixTitle).toMatch(/Mix-ups we clear/i);
    expect(us.mixups.map((m) => m.t).join(" ")).toMatch(/\$7/);
    expect(us.mixups.map((m) => m.d).join(" ")).toMatch(/not cheap labor/i);
    expect(us.mixups.map((m) => m.d).join(" ")).toMatch(/1-2 weeks/);
    expect(us.mixups.map((m) => m.d).join(" ")).toMatch(/English fluency/);
    expect(us.mixups.map((m) => m.d).join(" ")).toMatch(/password manager/);
    expect(us.mixups.map((m) => m.d).join(" ")).toMatch(/\bMFA\b/);
    expect(us.lead).toMatch(/20 hours\/week/);
    expect(us.pains).toHaveLength(4);
    expect(us.mixups).toHaveLength(4);
    expect(us.steps[2].d).toContain(
      "You conduct a video interview with your chosen candidate.",
    );
    expect(us.gateLead).toMatch(/A member of our team/);
    expect(us.gateLead).toMatch(/Obligation free/);
    expect(us.phoneDisplay).toBe("(888) 964-8644");
    expect(au.phoneDisplay).toBe("1300 886 740");
    expect(au.howLead).toMatch(/employment admin/);
    expect(au.lead).toMatch(/Australian business hours/);
    expect(us.googleLine).toMatch(/5\.0 Google · 39/);
    expect(us.clutchLine).toMatch(/4\.9 Clutch · 7/);
  });

  it("does not promise a $7 rate or invent proof", () => {
    const blob = JSON.stringify([consultCopy("us"), consultCopy("au")]);
    expect(blob).not.toMatch(/\$7\/hour starting|from \$7|only \$7/i);
    expect(blob).not.toMatch(/\u2014|&mdash;/);
    expect(blob).not.toMatch(/Fortune 500/i);
    expect(blob.toLowerCase()).not.toContain("engagechat");
    const quotes = PUBLIC_QUOTES.map((q) => q.name);
    expect(quotes).toContain("Kyrstin H.");
    expect(quotes).toContain("David Boyd");
  });
});

describe("hours minimum on the shared gate", () => {
  it("prints 20 hours/week minimum next to Full-time / Part-time", () => {
    const gate = readFileSync(
      join(ROOT, "app/components/GuidedMatchGate.tsx"),
      "utf8",
    );
    expect(GUIDED_MATCH_HOURS_MINIMUM_NOTE).toBe("20 hours/week minimum.");
    expect(gate).toContain("GUIDED_MATCH_HOURS_MINIMUM_NOTE");
    expect(gate).toContain("Full-time or part-time");
    expect(gate).toContain('name="company"');
    const leadGate = readFileSync(
      join(ROOT, "app/components/LeadGate.tsx"),
      "utf8",
    );
    expect(leadGate).toContain("GUIDED_MATCH_HOURS_MINIMUM_NOTE");
    expect(leadGate).toContain("Full-time or part-time?");
    const how = readFileSync(
      join(ROOT, "app/components/GuidedMatchLanding.tsx"),
      "utf8",
    ).replace(/\s+/g, " ");
    expect(how).toContain(
      "You conduct a video interview with your chosen candidate.",
    );
  });
});
