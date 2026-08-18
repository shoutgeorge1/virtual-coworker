import { describe, expect, it } from "vitest";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import {
  OFFER_FUNNEL_PATHS,
  PROOF_FUNNEL_PATHS,
  funnelSlugCollidesWithCategory,
  offerFunnelCopy,
  proofFunnelCopy,
} from "../config/lp-funnel-challengers";
import { CATEGORY_SLUGS } from "../config/categories";
import {
  canGoBack,
  chipClickIsFormStart,
  guidedMatchLandingFlags,
  guidedMatchStepIndex,
  shouldStartEmployerFormOnPii,
} from "./guided-match";
import { roleHeadline } from "../config/guided-match";

const ROOT = join(__dirname, "..");

describe("offer and proof funnel pages", () => {
  it("uses static slugs that do not collide with category routes", () => {
    expect(OFFER_FUNNEL_PATHS.us).toBe("/us/offer");
    expect(OFFER_FUNNEL_PATHS.au).toBe("/au/offer");
    expect(PROOF_FUNNEL_PATHS.us).toBe("/us/proof");
    expect(PROOF_FUNNEL_PATHS.au).toBe("/au/proof");
    expect(funnelSlugCollidesWithCategory()).toBe(false);
    expect(CATEGORY_SLUGS).not.toContain("offer");
    expect(CATEGORY_SLUGS).not.toContain("proof");
    expect(CATEGORY_SLUGS).not.toContain("capacity");
  });

  it("leaves live /us and /au on StaffingBaselineLanding (not funnel challengers)", () => {
    const us = readFileSync(join(ROOT, "app/us/page.tsx"), "utf8");
    const au = readFileSync(join(ROOT, "app/au/page.tsx"), "utf8");
    expect(us).toContain("StaffingBaselineLanding");
    expect(au).toContain("StaffingBaselineLanding");
    expect(us).not.toContain("OfferLanding");
    expect(us).not.toContain("ProofLanding");
    expect(us).not.toContain("ConsultLanding");
    expect(au).not.toContain("OfferLanding");
    expect(au).not.toContain("ProofLanding");
    expect(au).not.toContain("ConsultLanding");
  });

  it("keeps /us/offer and /au/offer on OfferLanding (live Ads test, not a baseline alias)", () => {
    const usOffer = readFileSync(join(ROOT, "app/us/offer/page.tsx"), "utf8");
    const auOffer = readFileSync(join(ROOT, "app/au/offer/page.tsx"), "utf8");
    expect(usOffer).toContain("OfferLanding");
    expect(auOffer).toContain("OfferLanding");
    expect(usOffer).not.toContain("redirectPreservingQuery");
    expect(auOffer).not.toContain("redirectPreservingQuery");
  });

  it("keeps the same conversion machine and form_start rule", () => {
    const flags = guidedMatchLandingFlags();
    expect(flags.lp_surface).toBe("form");
    expect(flags.cta_mode).toBe("form_primary");
    expect(chipClickIsFormStart()).toBe(false);
    expect(shouldStartEmployerFormOnPii(false)).toBe(true);
    expect(canGoBack("contact", null, true)).toBe(false);
    expect(guidedMatchStepIndex("contact", null, true)).toEqual({
      shown: 1,
      total: 1,
      pct: "100%",
    });
    const offer = readFileSync(join(ROOT, "app/components/OfferLanding.tsx"), "utf8");
    const proof = readFileSync(join(ROOT, "app/components/ProofLanding.tsx"), "utf8");
    expect(offer).toContain("contactFirst");
    expect(proof).toContain("contactFirst");
    expect(offer).toContain("GuidedMatchGate");
    expect(proof).toContain("GuidedMatchGate");
  });

  it("localises phones and hours without cloning capacity layout", () => {
    const usOffer = offerFunnelCopy("us");
    const auOffer = offerFunnelCopy("au");
    const usProof = proofFunnelCopy("us");
    const auProof = proofFunnelCopy("au");
    expect(usOffer.phoneDisplay).toBe("(888) 964-8644");
    expect(auOffer.phoneDisplay).toBe("1300 886 740");
    expect(usProof.phoneDisplay).toBe("(888) 964-8644");
    expect(auProof.phoneDisplay).toBe("1300 886 740");
    expect(usOffer.h1).toMatch(/your hours/);
    expect(auOffer.h1).toMatch(/Australian hours/);
    expect(existsSync(join(ROOT, "public/brand/offer-desk-staff.jpg"))).toBe(true);
    expect(usOffer.heroSrc).toBe("/brand/offer-desk-staff.jpg");
    expect(auOffer.heroSrc).toBe("/brand/offer-desk-staff.jpg");
    expect(usProof.heroSrc).toBe("/guided-match/trust-consult.jpg");
    expect(usProof.heroSrc).not.toBe(usOffer.heroSrc);
    expect(usOffer.heroSrc).not.toBe("/brand/va-us.jpg");
    expect(usProof.quote.by).toContain("David Boyd");
    expect(usProof.booksLine.toLowerCase()).toMatch(/books/);
    expect(usProof.eyebrow.toLowerCase()).toMatch(/finance/);
    const offerSrc = readFileSync(join(ROOT, "app/components/OfferLanding.tsx"), "utf8");
    const proofSrc = readFileSync(join(ROOT, "app/components/ProofLanding.tsx"), "utf8");
    expect(offerSrc).toContain("lp-logo-chip");
    expect(proofSrc).toContain("st-hero-plate");
    expect(offerSrc).not.toContain("tpc.googlesyndication");
    expect(offerSrc).not.toContain("cc-card-grid");
    expect(proofSrc).not.toContain("cc-compare");
    expect(offerSrc).not.toContain("gm-hero-grid");
    expect(proofSrc).not.toContain("gm-hero-grid");
  });

  it("does not use em dashes in funnel copy", () => {
    const blob = JSON.stringify([
      offerFunnelCopy("us"),
      offerFunnelCopy("au"),
      proofFunnelCopy("us"),
      proofFunnelCopy("au"),
    ]);
    expect(blob).not.toMatch(/\u2014|&mdash;/);
  });
});
