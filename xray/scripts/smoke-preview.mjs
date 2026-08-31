#!/usr/bin/env node
/**
 * Smoke-test static dashboard URLs on a preview (or prod) host.
 * Usage: node scripts/smoke-preview.mjs https://preview-url.vercel.app
 */
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";

const base = (process.argv[2] || "").replace(/\/$/, "");
if (!base) {
  console.error("Usage: node scripts/smoke-preview.mjs <base-url>");
  process.exit(2);
}

const root = new URL("..", import.meta.url).pathname;
const pub = existsSync(join(root, "public", "launch-control.html"))
  ? join(root, "public")
  : root;

const htmlFiles = readdirSync(pub).filter((f) => f.endsWith(".html"));
const must = [
  "/launch-control",
  "/executive",
  "/tracking",
  "/conversion-path",
  "/attribution",
  "/xray.css",
  "/nav.js",
];

const paths = new Set(must);
for (const f of htmlFiles) {
  paths.add(`/${f}`);
  paths.add(`/${f.replace(/\.html$/, "")}`);
}

// assets referenced from nav if present
const navPath = join(pub, "nav.js");
if (existsSync(navPath)) {
  const nav = readFileSync(navPath, "utf8");
  for (const m of nav.matchAll(/href:\s*["']([^"']+)["']/g)) {
    paths.add(m[1].startsWith("/") ? m[1] : `/${m[1]}`);
  }
}

let failed = 0;
const results = [];
for (const path of [...paths].sort()) {
  const url = `${base}${path}`;
  try {
    const res = await fetch(url, { redirect: "follow" });
    const ok = res.status >= 200 && res.status < 400;
    results.push({ path, status: res.status, ok });
    if (!ok) failed += 1;
  } catch (err) {
    results.push({ path, status: 0, ok: false, error: String(err) });
    failed += 1;
  }
}

const bad = results.filter((r) => !r.ok);
console.log(
  JSON.stringify(
    {
      base,
      checked: results.length,
      failed,
      bad: bad.slice(0, 30),
    },
    null,
    2,
  ),
);
process.exit(failed ? 1 : 0);
