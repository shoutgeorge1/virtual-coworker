import { describe, expect, it } from "vitest";
import {
  APPROVED_TESTIMONIALS,
  DOCUMENTED_ADS_NEGATIVES,
  DOCUMENTED_DO_NOT_NEGATIVE,
  TRUST_FIRST_LP_VERSION,
  TRUST_FIRST_NAMESPACE,
  TRUST_FIRST_PAGE_KEYS,
  TRUST_FIRST_PAGES,
  TRUST_FIRST_SPLIT_LIVE,
  VERIFIED_PROOF,
} from "../config/trust-first";
import {
  assignTrustFirstVariant,
  normalizeTrustFirstVariant,
  previewRobots,
  variantHref,
} from "./trust-first";

const BANNED_CLAIMS = [
  "70%",
  "0.7%",
  "soc 2",
  "hipaa",
  "pci",
  "myoutdesk",
  "{keyword",
  "{keyWord",
];

describe("trust-first preview family", () => {
  it("covers the ten preview pages under the isolated namespace", () => {
    expect(TRUST_FIRST_PAGE_KEYS).toHaveLength(10);
    for (const key of TRUST_FIRST_PAGE_KEYS) {
      const page = TRUST_FIRST_PAGES[key];
      expect(page.previewPath.startsWith(TRUST_FIRST_NAMESPACE)).toBe(true);
      expect(page.h1.length).toBeGreaterThan(12);
      expect(page.h1.includes("{")).toBe(false);
      expect(page.title.length).toBeGreaterThan(8);
    }
  });

  it("does not swap live /us as a production path", () => {
    expect(TRUST_FIRST_PAGES.us.proposedProductionPath).toMatch(/challenger/i);
    expect(TRUST_FIRST_PAGES.us.currentProductionEquivalent).toBe("/us");
  });

  it("keeps the experiment split disabled", () => {
    expect(TRUST_FIRST_SPLIT_LIVE).toBe(false);
    expect(assignTrustFirstVariant({}).variant).toBe("simple");
    expect(assignTrustFirstVariant({ query: "proof" }).variant).toBe("proof_heavy");
    expect(normalizeTrustFirstVariant("b")).toBe("proof_heavy");
  });

  it("writes noindex robots for preview", () => {
    const robots = previewRobots();
    expect(robots.index).toBe(false);
    expect(robots.follow).toBe(false);
    expect(robots.noarchive).toBe(true);
  });

  it("uses verified founding year and does not invent competitor claims", () => {
    expect(VERIFIED_PROOF.foundedYear).toBe(2011);
    const blob = JSON.stringify(TRUST_FIRST_PAGES).toLowerCase();
    for (const phrase of BANNED_CLAIMS) {
      expect(blob.includes(phrase)).toBe(false);
    }
  });

  it("only lists approved testimonials", () => {
    expect(APPROVED_TESTIMONIALS.length).toBeGreaterThan(0);
    for (const t of APPROVED_TESTIMONIALS) {
      expect(t.name).toBeTruthy();
      expect(t.quote).toBeTruthy();
    }
  });

  it("documents job-seeker negatives without blocking hire", () => {
    expect(DOCUMENTED_ADS_NEGATIVES).toContain("jobs");
    expect(DOCUMENTED_DO_NOT_NEGATIVE).toContain("hiring");
  });

  it("stamps a preview lp version", () => {
    expect(TRUST_FIRST_LP_VERSION).toContain("preview");
    expect(variantHref("/preview/trust-first/us", "proof_heavy")).toContain("v=proof");
  });
});
