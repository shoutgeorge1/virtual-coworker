import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  STAFFING_PARTNER_PATH,
  STAFFING_PARTNER_VARIANT,
  staffingPartnerCopy,
} from "../config/lp-staffing-partner";
import { CATEGORY_SLUGS } from "../config/categories";
import { guidedMatchLandingFlags } from "./guided-match";

const ROOT = join(__dirname, "..");

describe("staffing-partner challenger (promoted to baseline)", () => {
  it("promotes approved copy onto live /us via StaffingBaselineLanding", () => {
    expect(STAFFING_PARTNER_PATH).toBe("/prototype/staffing-partner/us");
    expect(STAFFING_PARTNER_VARIANT).toBe("price_staffing_v1");
    expect(CATEGORY_SLUGS).not.toContain("staffing-partner");
    const us = readFileSync(join(ROOT, "app/us/page.tsx"), "utf8");
    expect(us).toContain("StaffingBaselineLanding");
    expect(us).not.toContain("GuidedMatchLanding");
    expect(us).not.toContain("sellFirst");
  });

  it("keeps locked challenger copy helpers and redirects the prototype", () => {
    const copy = staffingPartnerCopy();
    expect(copy.eyebrow).toBe("Dedicated Filipino Remote Staff");
    expect(copy.h1.replace(/\u200b/g, "")).toBe(
      "Hire Dedicated Filipino Remote Staff From $7/Hour",
    );
    expect(copy.lead).toMatch(/recruits and vets/);
    expect(copy.primaryCta).toBe("Tell Us Who You Need");
    const page = readFileSync(
      join(ROOT, "app/prototype/staffing-partner/us/page.tsx"),
      "utf8",
    );
    const landing = readFileSync(
      join(ROOT, "app/components/StaffingPartnerLanding.tsx"),
      "utf8",
    );
    expect(page).toContain('redirectPreservingQuery("/us"');
    expect(landing).toContain("GuidedMatchGate");
    expect(landing).toContain("explicitContinue");
    expect(landing).toContain("sequentialNeeds");
  });

  it("makes the quiz the conversion card and the final CTA a phone path", () => {
    const copy = staffingPartnerCopy();
    expect(copy.gateTitle).toBe("Tell Us Who You Need");
    expect(copy.gateLead).not.toMatch(/\u2014|&mdash;/);
    expect(copy.finalTitle).toBe("Prefer to Talk It Through?");
    expect(copy.finalLead).toMatch(/Call our staffing team/);
    expect(copy.finalPhoneCta).toBe("Call (888) 964-8644");

    const landing = readFileSync(
      join(ROOT, "app/components/StaffingBaselineLanding.tsx"),
      "utf8",
    );
    const gate = readFileSync(
      join(ROOT, "app/components/GuidedMatchGate.tsx"),
      "utf8",
    );

    expect(landing).toMatch(/className="sp-hero-cta"[\s\S]*?href="#gate"/);
    expect(landing).toMatch(/className="gm-qualify"\s+id="gate"/);
    expect(landing).toContain("includeGateId={false}");
    expect(landing).toContain("{copy.gateTitle}");
    expect(landing).toContain("{copy.gateLead}");
    expect(landing).toContain("tabIndex={-1}");
    expect(landing).toContain("progressLabel=\"step\"");
    expect(landing).toContain("hoursQuestionSplit");
    expect(landing).toContain("spQuiz");

    const qualifyStart = landing.indexOf('className="gm-qualify"');
    const closerStart = landing.indexOf('id="again"');
    expect(qualifyStart).toBeGreaterThan(-1);
    expect(closerStart).toBeGreaterThan(qualifyStart);
    const qualifyBlock = landing.slice(qualifyStart, closerStart);
    expect(qualifyBlock).toContain("GuidedMatchGate");
    expect(qualifyBlock).toContain("sp-quiz-card");
    expect(qualifyBlock).not.toContain("{copy.primaryCta}");
    expect(qualifyBlock).not.toContain("quietStart");

    const closerBlock = landing.slice(closerStart);
    expect(closerBlock).toContain("{copy.finalPhoneCta}");
    expect(closerBlock).toContain("cfg.phone_href");
    expect(closerBlock).not.toContain('href="#gate"');
    expect(closerBlock).not.toContain("{copy.primaryCta}");

    // Parent owns #gate; /us defaults stay chip-advance and "1 of 3".
    expect(gate).toContain("includeGateId = true");
    expect(gate).toContain("explicitContinue = false");
    expect(gate).toContain("sequentialNeeds = false");
    expect(gate).toContain('id={includeGateId ? "gate" : undefined}');
    expect(gate).toContain("What role are you hiring for?");
    expect(gate).toContain("How many hours per week?");
    expect(gate).toContain("How many people do you need?");
    expect(gate).toContain("About how many people in your company?");
    expect(gate).toContain("useSequentialNeeds");
    expect(gate).toContain("gm-chips");
    expect(gate).toContain("hideQuizChrome");
    expect(gate).toContain("Get my hiring brief");
    expect(gate).toContain("if (!explicitContinue) setStep(\"needs\")");
    expect(gate).toContain('setStep(useSequentialNeeds ? "hours" : "needs")');
    expect(gate).toContain("gm-needs-split");
    expect(gate).toContain("gm-pair");
    expect(gate).toContain("Full-time or part-time");
    expect(gate).toContain('step === "needs" && !useSequentialNeeds');
  });

  it("splits staffing-partner needs into one question per screen", () => {
    const gate = readFileSync(
      join(ROOT, "app/components/GuidedMatchGate.tsx"),
      "utf8",
    );
    const helpers = readFileSync(join(ROOT, "lib/guided-match.ts"), "utf8");
    expect(gate).toContain("continueHours");
    expect(gate).toContain("continuePeople");
    expect(gate).toContain("continueSize");
    expect(gate).toContain("skipSize");
    expect(gate).toContain("disabled={!schedule}");
    expect(gate).toContain("disabled={!positions}");
    expect(helpers).toContain("SEQUENTIAL_WITH_ROLE");
    expect(helpers).toContain('"hours"');
    expect(helpers).toContain('"people"');
    expect(helpers).toContain('"size"');
  });

  it("enlarges below-hero type and widens the quiz without touching hero H1", () => {
    const css = readFileSync(join(ROOT, "app/staffing-partner.css"), "utf8");
    expect(css).toContain("clamp(1.875rem, 8.2vw, 2.125rem)");
    expect(css).toContain("clamp(1.875rem, 2.5vw, 2rem)");
    expect(css).toContain("font-size: 1.25rem");
    expect(css).toContain("max-width: 50rem");
    expect(css).toContain(".gm-logo-row img");
    expect(css).toMatch(/\.gm-logo-row img \{[\s\S]*?height: 44px/);
    expect(css).toContain("gm-needs-split");
    expect(css).toContain("gm-pair");
    expect(css).toMatch(/\.sp \.gm-quote \{/);
    expect(css).toMatch(/\.sp-quiz-card > h2:focus \{[\s\S]*?outline: none/);
    expect(css).toContain("h2:focus-visible");
    expect(css).not.toMatch(
      /\.sp-quiz-card > h2:focus \{\s*outline: 2px solid/,
    );
  });

  it("allows published $7/hr start rate and does not invent other claims", () => {
    const blob = JSON.stringify(staffingPartnerCopy()).toLowerCase();
    expect(blob.replace(/\u200b/g, "")).toContain("$7/hour");
    expect(blob).not.toMatch(/\$4|\$8/);
    expect(blob).not.toMatch(/80%/);
    expect(blob).not.toMatch(/\u2014|&mdash;/);
    expect(blob).toContain("\u2013"); // en dash in 20–40
    expect(blob).not.toContain("upwork");
    expect(blob).not.toContain("bpo");
    expect(blob).not.toContain("outsourcing");
    expect(blob).not.toContain("guaranteed");
    expect((blob.match(/virtual assistant/g) || []).length).toBeLessThanOrEqual(
      1,
    );
  });

  it("keeps production guided-match flags empty unless a preview override is passed", () => {
    expect(guidedMatchLandingFlags().lp_variant).toBe("");
    expect(guidedMatchLandingFlags("price_staffing_v1").lp_variant).toBe(
      "price_staffing_v1",
    );
  });
});
