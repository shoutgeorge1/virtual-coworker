/**
 * Hero-image badge copy for ?hero=badge|pill|hot.
 *
 * Hourly “from $X” lines are only emitted when the public Price Guide lists a
 * starting rate for that role. Sources (fetched 2026-08-06; cite full URLs in
 * git commit — keep WP hosts out of vision source per no-wp-links):
 *   US Price Guide — “Hourly Rates Starting At” (Digital Marketing Manager $12,
 *   Accountant $10, etc.)
 *   AU Price Guide — “Hourly Rates Starting At” AUD (Digital Marketing Manager
 *   $14 AUD, Accountant $12 AUD, etc.)
 *
 * Do not invent rates for roles without a published starting figure (e.g. HR).
 */

import type { MarketId } from "../config/markets";
import type { CategorySlug } from "../config/categories";

export type HeroRateBadge = {
  /** Short display, e.g. "from $12" */
  amount: string;
  /** Unit line, e.g. "/hr" or "AUD/hr" */
  unit: string;
  /** Accessible label */
  aria: string;
  /** Role label used on the public price guide */
  roleLabel: string;
};

/** Published starting rates only — see file header for sources. */
const PUBLIC_STARTING_RATES: Partial<
  Record<CategorySlug, Record<MarketId, { amountUsdOrAud: number; roleLabel: string }>>
> = {
  "digital-marketing": {
    us: { amountUsdOrAud: 12, roleLabel: "Digital Marketing Manager" },
    au: { amountUsdOrAud: 14, roleLabel: "Digital Marketing Manager" },
  },
  "social-media": {
    us: { amountUsdOrAud: 8, roleLabel: "Social Media Manager" },
    au: { amountUsdOrAud: 11, roleLabel: "Social Media Manager" },
  },
  accounting: {
    us: { amountUsdOrAud: 10, roleLabel: "Accountant" },
    au: { amountUsdOrAud: 12, roleLabel: "Accountant" },
  },
  bookkeeping: {
    us: { amountUsdOrAud: 8, roleLabel: "Bookkeeper" },
    au: { amountUsdOrAud: 11, roleLabel: "Bookkeeper" },
  },
  "administrative-support": {
    us: { amountUsdOrAud: 7, roleLabel: "Virtual Assistant" },
    au: { amountUsdOrAud: 8, roleLabel: "Virtual Assistant" },
  },
  "customer-service": {
    us: { amountUsdOrAud: 7, roleLabel: "Customer Support" },
    au: { amountUsdOrAud: 8, roleLabel: "Customer Support" },
  },
  recruitment: {
    us: { amountUsdOrAud: 9, roleLabel: "Recruitment Assistant" },
    au: { amountUsdOrAud: 12, roleLabel: "Recruitment Assistant" },
  },
  sales: {
    us: { amountUsdOrAud: 8, roleLabel: "Lead Generation Specialist" },
    au: { amountUsdOrAud: 10, roleLabel: "Lead Generation Specialist" },
  },
  // hr — no published HR starting rate on the Price Guide; omit.
};

export function resolveHeroRateBadge(
  market: MarketId,
  category: CategorySlug | null | undefined,
): HeroRateBadge | null {
  if (!category) return null;
  const entry = PUBLIC_STARTING_RATES[category]?.[market];
  if (!entry) return null;
  const n = entry.amountUsdOrAud;
  if (market === "au") {
    return {
      amount: `from $${n}`,
      unit: "AUD/hr",
      aria: `Starting from ${n} Australian dollars per hour for ${entry.roleLabel}`,
      roleLabel: entry.roleLabel,
    };
  }
  return {
    amount: `from $${n}`,
    unit: "/hr",
    aria: `Starting from ${n} dollars per hour for ${entry.roleLabel}`,
    roleLabel: entry.roleLabel,
  };
}

export type HeroSecondaryBadge =
  | { kind: "rate"; rate: HeroRateBadge }
  | { kind: "ph"; label: string; sub: string; aria: string };

/** Second badge: published rate when available, else Philippines dedicated. */
export function resolveHeroSecondaryBadge(
  market: MarketId,
  category: CategorySlug | null | undefined,
): HeroSecondaryBadge {
  const rate = resolveHeroRateBadge(market, category);
  if (rate) return { kind: "rate", rate };
  return {
    kind: "ph",
    label: "Philippines",
    sub: "Dedicated hire",
    aria: "Philippines dedicated hire",
  };
}
