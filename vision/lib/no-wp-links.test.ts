import { describe, expect, it } from "vitest";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { DEFAULT_CAREERS_URL } from "../config/markets";

/**
 * Paid employer surfaces must not link to US/AU WordPress hosts.
 * Intentional job-seeker egress to virtualcoworker.com.ph is allowed.
 */

const ROOT = join(__dirname, "..");
const EMPLOYER_WP_HREF_RE =
  /(?:href\s*=\s*["'`](?!mailto:)|url\s*\(\s*["']?|redirect\s*\(\s*["'`]|window\.location\s*=\s*["'`])[^"'`)]*virtualcoworker\.com(?!\.ph)(?:\.au)?/i;
const EMPLOYER_WP_BARE_URL_RE =
  /https?:\/\/(?:www\.)?virtualcoworker\.com(?!\.ph)(?:\.au)?\b/gi;

const SCAN_DIRS = ["app", "components", "config", "lib"];
const EXT_RE = /\.(tsx?|jsx?|mjs|css)$/;

function stripPhCareersUrls(text: string): string {
  return text.replace(
    /https?:\/\/(?:www\.)?virtualcoworker\.com\.ph\b[^"'`\s]*/gi,
    "",
  );
}

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

describe("no employer WordPress egress on paid microsite", () => {
  it("rejects navigable US/AU virtualcoworker.com links (PH careers allowed)", () => {
    const files = SCAN_DIRS.flatMap((d) => walk(join(ROOT, d)));
    const hits: string[] = [];

    for (const file of files) {
      const text = stripPhCareersUrls(readFileSync(file, "utf8"));
      const rel = relative(ROOT, file);
      if (EMPLOYER_WP_HREF_RE.test(text)) {
        hits.push(`${rel}: href/url-style employer WP link`);
        continue;
      }
      const abs = text.match(EMPLOYER_WP_BARE_URL_RE);
      if (abs) {
        hits.push(`${rel}: absolute employer WP URL ${[...new Set(abs)].join(", ")}`);
      }
    }

    expect(hits, hits.join("\n") || "clean").toEqual([]);
  });

  it("defaults careers to PH WordPress and blocks employer WP env", async () => {
    const prev = process.env.NEXT_PUBLIC_CAREERS_URL;
    delete process.env.NEXT_PUBLIC_CAREERS_URL;
    // Fresh import not required — functions read env at call time
    const { resolveCareersUrl, careersUrlIsBlocker } = await import("../config/markets");
    expect(resolveCareersUrl()).toBe(DEFAULT_CAREERS_URL);

    process.env.NEXT_PUBLIC_CAREERS_URL = "https://virtualcoworker.com/careers";
    expect(resolveCareersUrl()).toBe(DEFAULT_CAREERS_URL);
    expect(careersUrlIsBlocker()).toBe(true);

    process.env.NEXT_PUBLIC_CAREERS_URL = DEFAULT_CAREERS_URL;
    expect(resolveCareersUrl()).toBe(DEFAULT_CAREERS_URL);
    expect(careersUrlIsBlocker()).toBe(false);

    if (prev === undefined) delete process.env.NEXT_PUBLIC_CAREERS_URL;
    else process.env.NEXT_PUBLIC_CAREERS_URL = prev;
  });
});
