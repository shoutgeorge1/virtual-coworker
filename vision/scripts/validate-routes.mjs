#!/usr/bin/env node
/**
 * Static route inventory for Stage 1 paid microsites.
 * Fails if expected category / market / legal routes are missing from app/.
 */
import { existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const app = join(root, "app");

const CATEGORIES = [
  "digital-marketing",
  "social-media",
  "accounting",
  "bookkeeping",
  "administrative-support",
  "customer-service",
  "hr",
  "recruitment",
  "sales",
];

const required = [
  "page.tsx", // / → /us
  "us/page.tsx",
  "au/page.tsx",
  "ph/page.tsx",
  "ph/apply/page.tsx",
  "privacy/page.tsx",
  "terms/page.tsx",
  "thank-you/page.tsx",
  "services/page.tsx",
  "how-it-works/page.tsx",
  "api/lead/route.ts",
  "us/[category]/page.tsx",
  "au/[category]/page.tsx",
];

const missing = required.filter((p) => !existsSync(join(app, p)));
if (missing.length) {
  console.error("Missing route files:", missing);
  process.exit(1);
}

console.log("Route files OK:");
console.log("  / → /us");
console.log("  /us · /au · /ph · /ph/apply");
console.log("  /privacy · /terms · /thank-you · /services · /how-it-works");
for (const m of ["us", "au"]) {
  for (const slug of CATEGORIES) {
    console.log(`  /${m}/${slug}`);
  }
}
console.log(`  alias: /{us|au}/human-resources → /{us|au}/hr (middleware 308)`);
console.log(`Categories: ${CATEGORIES.length} × 2 markets`);
