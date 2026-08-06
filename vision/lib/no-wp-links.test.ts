import { describe, expect, it } from "vitest";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

/**
 * Automated audit: paid microsite source must not href/link to WordPress hosts.
 * Fails CI/local test if virtualcoworker.com(.au) appears as a navigable URL.
 */

const ROOT = join(__dirname, "..");
const WP_HREF_RE =
  /(?:href\s*=\s*["'`]|url\s*\(\s*["']?|redirect\s*\(\s*["'`]|window\.location\s*=\s*["'`])[^"'`)]*virtualcoworker\.com(?:\.au)?/i;
const WP_BARE_URL_RE = /https?:\/\/(?:www\.)?virtualcoworker\.com(?:\.au)?/gi;

const SCAN_DIRS = ["app", "components", "config", "lib"];
const EXT_RE = /\.(tsx?|jsx?|mjs|css)$/;

function walk(dir: string, out: string[] = []): string[] {
  let entries: string[];
  try {
    entries = readdirSync(dir);
  } catch {
    return out;
  }
  for (const name of entries) {
    if (name === "node_modules" || name === ".next") continue;
    const full = join(dir, name);
    const st = statSync(full);
    if (st.isDirectory()) walk(full, out);
    else if (EXT_RE.test(name) && !/\.test\.(tsx?|jsx?)$/.test(name)) out.push(full);
  }
  return out;
}

describe("no WordPress egress on paid microsite", () => {
  it("rejects navigable virtualcoworker.com links in vision source", () => {
    const files = SCAN_DIRS.flatMap((d) => walk(join(ROOT, d)));
    const hits: string[] = [];

    for (const file of files) {
      const text = readFileSync(file, "utf8");
      const rel = relative(ROOT, file);
      // Allow prose that forbids WP (comments / disclaimer strings) if no href/url()
      if (WP_HREF_RE.test(text)) {
        hits.push(`${rel}: href/url-style WP link`);
        continue;
      }
      // Absolute WP URLs anywhere in TSX/JS (string literals used as destinations)
      const abs = text.match(WP_BARE_URL_RE);
      if (abs) {
        // site.ts disclaimer mentions WP in prose — allow only non-http bare mentions
        // already caught by https? pattern; site disclaimer uses "WordPress" word only
        hits.push(`${rel}: absolute WP URL ${[...new Set(abs)].join(", ")}`);
      }
    }

    expect(hits, hits.join("\n") || "clean").toEqual([]);
  });

  it("rejects WP careers env fallback", async () => {
    const prev = process.env.NEXT_PUBLIC_CAREERS_URL;
    process.env.NEXT_PUBLIC_CAREERS_URL = "https://virtualcoworker.com/careers";
    const { resolveCareersUrl, careersUrlIsBlocker } = await import("../config/markets");
    expect(resolveCareersUrl()).toBe("/ph");
    expect(careersUrlIsBlocker()).toBe(true);
    if (prev === undefined) delete process.env.NEXT_PUBLIC_CAREERS_URL;
    else process.env.NEXT_PUBLIC_CAREERS_URL = prev;
  });
});
