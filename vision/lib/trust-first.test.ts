import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import {
  APPROVED_H1_BOOKKEEPING,
  APPROVED_H1_CORE,
  APPROVED_H1_CUSTOMER_SERVICE,
  APPROVED_H1_DIGITAL_MARKETING,
  APPROVED_H1_EA,
  APPROVED_H1_REAL_ESTATE,
  APPROVED_H1_SALES,
  APPROVED_H1_SENTENCE_2,
  APPROVED_TESTIMONIALS,
  DOCUMENTED_ADS_NEGATIVES,
  DOCUMENTED_DO_NOT_NEGATIVE,
  H1_HIGHLIGHTS,
  PH_MARKET_FACTS,
  REVIEW_BADGES,
  TRUST_FIRST_LP_VERSION,
  TRUST_FIRST_NAMESPACE,
  TRUST_FIRST_PAGE_KEYS,
  TRUST_FIRST_PAGES,
  TRUST_FIRST_SPLIT_LIVE,
  VERIFIED_PROOF,
} from "../config/trust-first";
import {
  assignTrustFirstVariant,
  highlightPhrase,
  normalizeTrustFirstVariant,
  previewRobots,
  splitHeadline,
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

  it("maps TF production paths onto isolated test URLs, not live CORE/ROLES Final URLs", () => {
    expect(TRUST_FIRST_PAGES.us.productionPath).toBe("/us/tf/hire");
    expect(TRUST_FIRST_PAGES.bookkeeping.productionPath).toBe("/us/tf/bookkeeping");
    expect(TRUST_FIRST_PAGES["real-estate"].productionPath).toBe("/us/tf/real-estate");
    expect(TRUST_FIRST_PAGES["philippines-virtual-assistants"].productionPath).toBe(
      "/us/philippines-virtual-assistants",
    );
    const liveBlocked = [
      "/us/bookkeeping",
      "/us/customer-service",
      "/us/sales",
      "/us/administrative-support",
      "/us/digital-marketing",
      "/us/staffing",
      "/us/real-estate",
    ];
    for (const key of TRUST_FIRST_PAGE_KEYS) {
      const page = TRUST_FIRST_PAGES[key];
      expect(page.productionPath.startsWith("/us")).toBe(true);
      expect(page.productionPath).not.toContain("preview");
      if (key !== "philippines-virtual-assistants") {
        expect(page.productionPath === "/us" || liveBlocked.includes(page.productionPath)).toBe(
          false,
        );
      }
    }
  });

  it("keeps the experiment split disabled", () => {
    expect(TRUST_FIRST_SPLIT_LIVE).toBe(false);
    expect(assignTrustFirstVariant({}).variant).toBe("proof_heavy");
    expect(assignTrustFirstVariant({ query: "simple" }).variant).toBe("simple");
    expect(assignTrustFirstVariant({ query: "proof" }).variant).toBe("proof_heavy");
    expect(normalizeTrustFirstVariant("b")).toBe("proof_heavy");
  });

  it("writes noindex robots for preview", () => {
    const robots = previewRobots();
    expect(robots.index).toBe(false);
    expect(robots.follow).toBe(false);
    expect(robots.noarchive).toBe(true);
  });

  it("uses verified founding year and does not invent competitor claims in body copy", () => {
    expect(VERIFIED_PROOF.foundedYear).toBe(2011);
    const pagesWithoutH1 = Object.values(TRUST_FIRST_PAGES).map((page) => {
      const { h1, h1_alt, ...rest } = page;
      return rest;
    });
    const blob = JSON.stringify(pagesWithoutH1).toLowerCase();
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

  it("highlights a written H1 phrase on every page", () => {
    for (const key of TRUST_FIRST_PAGE_KEYS) {
      const hit = highlightPhrase(TRUST_FIRST_PAGES[key].h1, H1_HIGHLIGHTS[key]);
      expect(hit?.accent.toLowerCase()).toBe(H1_HIGHLIGHTS[key].toLowerCase());
    }
  });

  it("splits two-sentence H1s into a navy clause and a light-blue clause", () => {
    for (const key of TRUST_FIRST_PAGE_KEYS) {
      const parts = splitHeadline(TRUST_FIRST_PAGES[key].h1);
      expect(parts.lead.length).toBeGreaterThan(8);
      expect(parts.accent).toBe(APPROVED_H1_SENTENCE_2);
    }
  });

  it("keeps 80% in a short sentence 2 without dropping Philippines from sentence 1", () => {
    expect(APPROVED_H1_SENTENCE_2).toContain("80%");
    expect(APPROVED_H1_SENTENCE_2.toLowerCase()).toContain("no recruitment fees");
    expect(APPROVED_H1_SENTENCE_2.length).toBeLessThan(95);
    expect(APPROVED_H1_SENTENCE_2.toLowerCase()).not.toContain("traditional hiring overhead");
    expect(APPROVED_H1_CORE).toMatch(/^Hire a Virtual Assistant From the Philippines\./);
    expect(APPROVED_H1_BOOKKEEPING).toMatch(
      /^Hire a Bookkeeping Virtual Assistant From the Philippines\./,
    );
    expect(APPROVED_H1_EA).toMatch(/^Hire an Executive Assistant From the Philippines\./);
  });

  it("stores a second H1 for a later A/B and does not turn the split on", () => {
    expect(TRUST_FIRST_SPLIT_LIVE).toBe(false);
    for (const key of TRUST_FIRST_PAGE_KEYS) {
      const page = TRUST_FIRST_PAGES[key];
      expect(page.h1_alt.length).toBeGreaterThan(12);
      expect(page.h1_alt).not.toBe(page.h1);
      const alt = splitHeadline(page.h1_alt);
      expect(alt.lead.length).toBeGreaterThan(8);
      expect(alt.accent.length).toBeGreaterThan(8);
    }
  });

  it("uses George-approved H1s only (body copy stays original; no competitor name)", () => {
    expect(TRUST_FIRST_PAGES.us.h1).toBe(APPROVED_H1_CORE);
    expect(TRUST_FIRST_PAGES["philippines-virtual-assistants"].h1).toBe(APPROVED_H1_CORE);
    expect(TRUST_FIRST_PAGES["virtual-assistant-agency"].h1).toBe(APPROVED_H1_CORE);
    expect(TRUST_FIRST_PAGES.staffing.h1).toBe(APPROVED_H1_CORE);
    expect(TRUST_FIRST_PAGES.bookkeeping.h1).toBe(APPROVED_H1_BOOKKEEPING);
    expect(TRUST_FIRST_PAGES["customer-service"].h1).toBe(APPROVED_H1_CUSTOMER_SERVICE);
    expect(TRUST_FIRST_PAGES.sales.h1).toBe(APPROVED_H1_SALES);
    expect(TRUST_FIRST_PAGES["administrative-support"].h1).toBe(APPROVED_H1_EA);
    expect(TRUST_FIRST_PAGES["digital-marketing"].h1).toBe(APPROVED_H1_DIGITAL_MARKETING);
    expect(TRUST_FIRST_PAGES["real-estate"].h1).toBe(APPROVED_H1_REAL_ESTATE);
    expect(TRUST_FIRST_PAGES.us.h1).toContain("80%");
    expect(TRUST_FIRST_PAGES.us.h1.toLowerCase()).not.toContain("70%");
    expect(JSON.stringify(TRUST_FIRST_PAGES.us.supporting).toLowerCase()).not.toContain("70%");
    expect(JSON.stringify(TRUST_FIRST_PAGES.us.supporting).toLowerCase()).not.toContain("80%");
    expect(JSON.stringify(TRUST_FIRST_PAGES.us.comparison).toLowerCase()).not.toContain("soc 2");
  });

  it("uses published Google and Clutch marks, not invented ratings", () => {
    expect(REVIEW_BADGES.google.rating).toBe("5.0");
    expect(REVIEW_BADGES.google.reviewCount).toBe(39);
    expect(REVIEW_BADGES.google.showCount).toBe(true);
    expect(REVIEW_BADGES.clutch.rating).toBe("4.9");
    expect(REVIEW_BADGES.clutch.reviewCount).toBe(7);
    expect(REVIEW_BADGES.clutch.showCount).toBe(false);
    expect(REVIEW_BADGES.clutch.caption.toLowerCase()).toBe("rated on clutch");
  });

  it("labels Philippines facts as market sources, not company stats", () => {
    const blob = JSON.stringify(PH_MARKET_FACTS).toLowerCase();
    expect(blob).toContain("ef english proficiency");
    expect(blob).toContain("ibpap");
    expect(blob).toContain("not a virtual coworker");
  });

  it("writes an honest compare table without competitor claims", () => {
    const labels = TRUST_FIRST_PAGES.us.comparison.map((row) => row.label);
    expect(labels).toEqual([
      "Time to a shortlist",
      "Vetting",
      "The seat",
      "Cost",
      "If it is not a fit",
      "Day-to-day",
      "Employment",
    ]);
    const blob = JSON.stringify({
      pages: Object.values(TRUST_FIRST_PAGES).map((page) => {
        const { h1, h1_alt, ...rest } = page;
        return rest;
      }),
    }).toLowerCase();
    for (const phrase of [
      ...BANNED_CLAIMS,
      "mytimein",
      "free rematch",
      "as little as one week",
      "$1988",
      "8,500",
    ]) {
      expect(blob.includes(phrase)).toBe(false);
    }
    expect(TRUST_FIRST_PAGES["philippines-virtual-assistants"].comparison[1].vc).toMatch(
      /Philippines team/,
    );
  });
});

describe("trust-first production wiring", () => {
  const ROOT = join(__dirname, "..");

  it("does not import the preview toolbar on isolated TF or restored live /us routes", () => {
    const files = [
      "app/us/page.tsx",
      "app/us/layout.tsx",
      "app/us/staffing/page.tsx",
      "app/us/real-estate/page.tsx",
      "app/us/tf/page.tsx",
      "app/us/tf/hire/page.tsx",
      "app/us/tf/real-estate/page.tsx",
      "app/us/tf/bookkeeping/page.tsx",
      "app/us/philippines-virtual-assistants/page.tsx",
      "app/us/[category]/page.tsx",
      "app/components/trust-first/TrustFirstUsPage.tsx",
      "app/components/trust-first/TrustFirstLanding.tsx",
    ];
    for (const rel of files) {
      const src = readFileSync(join(ROOT, rel), "utf8");
      expect(src).not.toContain("PreviewVariantToolbar");
      expect(src).not.toContain("PREVIEW ONLY — NOTHING LAUNCHED");
    }
    const previewLayout = readFileSync(
      join(ROOT, "app/preview/trust-first/layout.tsx"),
      "utf8",
    );
    expect(previewLayout).toContain("PreviewVariantToolbar");
  });

  it("marks trust-first phone links so site click tracking can fire", () => {
    const header = readFileSync(
      join(ROOT, "app/components/trust-first/CompanyHeader.tsx"),
      "utf8",
    );
    const footer = readFileSync(
      join(ROOT, "app/components/trust-first/CompanyFooter.tsx"),
      "utf8",
    );
    expect(header).toContain('data-track="phone_cta_clicked"');
    expect(footer).toContain('data-track="phone_cta_clicked"');
  });

  it("posts live forms to /api/lead and keeps preview on the sink", () => {
    const form = readFileSync(
      join(ROOT, "app/components/trust-first/EmployerQualificationForm.tsx"),
      "utf8",
    );
    expect(form).toContain('fetch("/api/lead"');
    expect(form).toContain('fetch("/api/lead-preview"');
    expect(form).toContain('surface === "production"');
    expect(form).toContain("trackValidEmployerSubmit");
  });
});
