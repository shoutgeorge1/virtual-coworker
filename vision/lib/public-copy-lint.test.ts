import { describe, expect, it } from "vitest";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { CATEGORIES, CATEGORY_SLUGS } from "../config/categories";
import { MARKETS } from "../config/markets";
import {
  FOOTER_SOCIAL_MARKS,
  INDUSTRY_STATS,
  PUBLIC_QUOTES,
  SITE,
} from "../config/site";

/**
 * Public-copy lint: buyer-facing LP strings must not carry internal QA / PPC jargon.
 * Banned list: ./public-copy-banned.json (also scanned by ads-launch builder qa()).
 */

type BannedFile = { phrases: string[] };

const BANNED_PATH = join(__dirname, "public-copy-banned.json");
const banned: BannedFile = JSON.parse(readFileSync(BANNED_PATH, "utf8"));
const VISION_ROOT = join(__dirname, "..");

function collectStrings(value: unknown, path: string, out: { path: string; text: string }[]): void {
  if (typeof value === "string") {
    out.push({ path, text: value });
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((item, i) => collectStrings(item, `${path}[${i}]`, out));
    return;
  }
  if (value && typeof value === "object") {
    for (const [k, v] of Object.entries(value)) {
      collectStrings(v, path ? `${path}.${k}` : k, out);
    }
  }
}

/** User-visible fields on each category LP config. */
function visibleCategoryStrings(): { path: string; text: string }[] {
  const out: { path: string; text: string }[] = [];
  for (const slug of CATEGORY_SLUGS) {
    const cat = CATEGORIES[slug];
    collectStrings(
      {
        label: cat.label,
        formLabel: cat.formLabel,
        shortLabel: cat.shortLabel,
        title: cat.title,
        description: cat.description,
        variants: cat.variants,
        benefits: cat.benefits,
        faq: cat.faq,
      },
      slug,
      out,
    );
  }
  return out;
}

function visibleMarketStrings(): { path: string; text: string }[] {
  const out: { path: string; text: string }[] = [];
  for (const id of ["us", "au"] as const) {
    const m = MARKETS[id];
    collectStrings(
      {
        headline: m.headline,
        prop: m.prop,
        staffingExplain: m.staffingExplain,
        label: m.label,
      },
      `markets.${id}`,
      out,
    );
  }
  return out;
}

function visibleSiteStrings(): { path: string; text: string }[] {
  const out: { path: string; text: string }[] = [];
  collectStrings(
    {
      tagline: SITE.tagline,
      disclaimer: SITE.disclaimer,
      footerLegal: SITE.footerLegal,
      trademark: SITE.trademark,
      quotes: PUBLIC_QUOTES,
      industryStats: INDUSTRY_STATS.map((s) => ({
        figure: s.figure,
        headline: s.headline,
        body: s.body,
        sourceLabel: s.sourceLabel,
      })),
      footerSocial: FOOTER_SOCIAL_MARKS.map((p) => p.name),
    },
    "site",
    out,
  );
  return out;
}

/** Pull human-facing string literals from TSX/TS marketing surfaces. */
function extractQuotedStrings(source: string): string[] {
  // Drop block + line comments so trackEvent / prop names in comments don't trip lint.
  const stripped = source
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/^\s*\/\/.*$/gm, "");
  const out: string[] = [];
  const re = /(["'`])((?:\\.|(?!\1)[\s\S])*?)\1/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(stripped))) {
    const text = m[2];
    if (text.length < 12) continue;
    // Skip code-ish tokens (event names, paths, class lists).
    if (!/\s/.test(text)) continue;
    if (text.includes("node_modules") || text.startsWith("./") || text.startsWith("../")) {
      continue;
    }
    if (/^(flex|grid|absolute|relative|inline)/.test(text)) continue;
    out.push(text);
  }
  return out;
}

const PUBLIC_SURFACE_FILES = [
  "app/components/MarketLanding.tsx",
  "app/components/TrustBand.tsx",
  "app/components/PressBand.tsx",
  "app/components/TrustQuotes.tsx",
  "app/components/RoleQuiz.tsx",
  "app/components/QuizTeaser.tsx",
  "app/components/ExitIntent.tsx",
  "app/components/EngageChat.tsx",
  "app/components/LeadGate.tsx",
  "app/components/SiteFooter.tsx",
  "app/components/SiteNav.tsx",
  "app/components/StickyCta.tsx",
  "app/components/StopCloser.tsx",
  "app/components/PainGain.tsx",
  "app/components/RoleOutcomes.tsx",
  "app/how-it-works/page.tsx",
  "app/thank-you/page.tsx",
  "app/services/page.tsx",
  "app/us/page.tsx",
  "app/au/page.tsx",
  "app/privacy/page.tsx",
  "app/terms/page.tsx",
  "app/layout.tsx",
  "config/employer-cro.ts",
  "config/hiring-process.ts",
];

function visibleSurfaceFileStrings(): { path: string; text: string }[] {
  const out: { path: string; text: string }[] = [];
  for (const rel of PUBLIC_SURFACE_FILES) {
    const abs = join(VISION_ROOT, rel);
    try {
      if (!statSync(abs).isFile()) continue;
    } catch {
      continue;
    }
    const src = readFileSync(abs, "utf8");
    extractQuotedStrings(src).forEach((text, i) => {
      out.push({ path: `${rel}[${i}]`, text });
    });
  }
  return out;
}

function findHits(strings: { path: string; text: string }[]): string[] {
  const hits: string[] = [];
  for (const { path, text } of strings) {
    const lower = text.toLowerCase();
    for (const phrase of banned.phrases) {
      if (lower.includes(phrase)) {
        hits.push(`${path}: "${phrase}" in ${JSON.stringify(text)}`);
      }
    }
  }
  return hits;
}

describe("public copy lint", () => {
  it("has a maintainable banned-phrase list", () => {
    expect(banned.phrases.length).toBeGreaterThan(20);
    for (const p of banned.phrases) {
      expect(p.trim().toLowerCase()).toBe(p);
      expect(p.length).toBeGreaterThan(2);
    }
  });

  it("rejects banned QA jargon in category LP copy", () => {
    const hits = findHits(visibleCategoryStrings());
    expect(hits, hits.join("\n") || "clean").toEqual([]);
  });

  it("rejects banned jargon in market + site public strings", () => {
    const hits = findHits([...visibleMarketStrings(), ...visibleSiteStrings()]);
    expect(hits, hits.join("\n") || "clean").toEqual([]);
  });

  it("rejects banned jargon in public surface TSX/TS", () => {
    const hits = findHits(visibleSurfaceFileStrings());
    expect(hits, hits.join("\n") || "clean").toEqual([]);
  });
});
