import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { CATEGORIES, CATEGORY_SLUGS } from "../config/categories";

/**
 * Public-copy lint: buyer-facing LP strings must not carry internal QA / PPC jargon.
 * Banned list: ./public-copy-banned.json (also scanned by ads-launch builder qa()).
 */

type BannedFile = { phrases: string[] };

const BANNED_PATH = join(__dirname, "public-copy-banned.json");
const banned: BannedFile = JSON.parse(readFileSync(BANNED_PATH, "utf8"));

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

describe("public copy lint", () => {
  it("has a maintainable banned-phrase list", () => {
    expect(banned.phrases.length).toBeGreaterThan(10);
    for (const p of banned.phrases) {
      expect(p.trim().toLowerCase()).toBe(p);
      expect(p.length).toBeGreaterThan(2);
    }
  });

  it("rejects banned QA jargon in category LP copy", () => {
    const strings = visibleCategoryStrings();
    const hits: string[] = [];

    for (const { path, text } of strings) {
      const lower = text.toLowerCase();
      for (const phrase of banned.phrases) {
        if (lower.includes(phrase)) {
          hits.push(`${path}: "${phrase}" in ${JSON.stringify(text)}`);
        }
      }
    }

    expect(hits, hits.join("\n") || "clean").toEqual([]);
  });
});
