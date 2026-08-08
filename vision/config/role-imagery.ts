/**
 * Role + late-trust imagery for LPs / services.
 * One unique portrait per category title — no shared src across titles.
 * Experiment: `role_imagery` — A = live defaults, B = challenger set.
 * See vision/docs/IMAGE-CHOICES.md + SITE-EXPERIMENTS.md.
 */

import { CATEGORY_SLUGS, type CategorySlug } from "./categories";
import type { ExpVariant } from "../lib/experiments";

/** Per-category portrait paths — every slug must resolve to a distinct file. */
export type CategoryImageryArm = Record<CategorySlug, string> & {
  trust: string;
  trustAlt: string;
};

/**
 * A = live defaults (v2 on strongest fit; siblings fill paired titles).
 * B = sole challenger (remaining *-b + brand faces). Still unique per title.
 * Relevant face → relevant role. One experiment, two arms — no extra tests.
 */
export const ROLE_IMAGERY: Record<"a" | "b", CategoryImageryArm> = {
  a: {
    "digital-marketing": "/roles/marketing-v2.png",
    "social-media": "/roles/marketing-a.png",
    accounting: "/roles/accounting-v2.png",
    bookkeeping: "/roles/bookkeeper-v2.png",
    "administrative-support": "/roles/admin-a.png",
    "customer-service": "/roles/customer-service-v2.png",
    hr: "/roles/hr-v3.png",
    recruitment: "/roles/sales-a.png",
    sales: "/roles/sales-v2.png",
    trust: "/trust/choices/trust-consult.png",
    trustAlt:
      "Two Virtual Coworker teammates reviewing a role brief together",
  },
  b: {
    "digital-marketing": "/roles/marketing-b.png",
    "social-media": "/roles/marketing-a.png",
    accounting: "/roles/bookkeeper-b.png",
    bookkeeping: "/roles/bookkeeper-a.png",
    "administrative-support": "/roles/admin-b.png",
    "customer-service": "/brand/support.jpg",
    hr: "/brand/ea.jpg",
    recruitment: "/roles/sales-b.png",
    sales: "/brand/talent-john.jpeg",
    trust: "/trust/choices/trust-team-office.png",
    trustAlt: "Philippines team collaborating around a conference table",
  },
};

export const CATEGORY_PORTRAIT_ALT: Record<CategorySlug, string> = {
  "digital-marketing": "Philippines digital marketing professional at a desk",
  "social-media": "Philippines social media professional at work",
  accounting: "Philippines accounting professional at a spreadsheet desk",
  bookkeeping: "Philippines bookkeeping professional at a spreadsheet desk",
  "administrative-support":
    "Philippines administrative / virtual assistant professional",
  "customer-service": "Philippines customer service professional",
  hr: "Philippines human resources professional reviewing candidate notes",
  recruitment: "Philippines recruitment support professional",
  sales: "Philippines sales support professional",
};

export function roleImageryFor(
  variant: ExpVariant | "a" | "b" = "a",
): CategoryImageryArm {
  return variant === "b" ? ROLE_IMAGERY.b : ROLE_IMAGERY.a;
}

/** Unique portrait src for a category title (services card + LP hero). */
export function portraitSrcForCategory(
  slug: CategorySlug,
  variant: ExpVariant | "a" | "b" = "a",
): string {
  return roleImageryFor(variant)[slug];
}

export function portraitAltForCategory(slug: CategorySlug): string {
  return CATEGORY_PORTRAIT_ALT[slug];
}

/** Assert arm has 9 distinct category srcs (no shared picture across titles). */
export function assertUniqueCategoryImagery(
  arm: CategoryImageryArm,
): string[] {
  const paths = CATEGORY_SLUGS.map((s) => arm[s]);
  const seen = new Map<string, CategorySlug>();
  const dupes: string[] = [];
  for (let i = 0; i < CATEGORY_SLUGS.length; i++) {
    const slug = CATEGORY_SLUGS[i];
    const src = paths[i];
    const prior = seen.get(src);
    if (prior) dupes.push(`${prior} + ${slug} → ${src}`);
    else seen.set(src, slug);
  }
  return dupes;
}
