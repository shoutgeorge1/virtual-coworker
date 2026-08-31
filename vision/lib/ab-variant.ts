/**
 * Stable A/B assignment for paid LPs.
 * Prefer cookie set by middleware (SSR-safe). Client helpers for QA override + persist.
 *
 * PARKED 2026-08-12: LP_CREATIVE_AB_LIVE = false. Freeze to A (current simplified
 * category copy). Ignore old B cookies. `?variant=` still works for QA.
 */

import type { AbVariant } from "../config/categories";

export const AB_COOKIE = "vc_ab_variant";
export const AB_STORAGE_KEY = "vc_ab_variant";

/** false = everyone gets variant A unless `?variant=` is in the URL. */
export const LP_CREATIVE_AB_LIVE = false;
export const PARKED_LP_VARIANT: AbVariant = "a";

export function normalizeVariant(raw: string | null | undefined): AbVariant | null {
  if (!raw) return null;
  const v = raw.trim().toLowerCase();
  if (v === "a" || v === "b") return v;
  return null;
}

/** Deterministic ~50/50 from a seed string (cookie id / random token). */
export function variantFromSeed(seed: string): AbVariant {
  let h = 0;
  for (let i = 0; i < seed.length; i++) {
    h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return h % 2 === 0 ? "a" : "b";
}

export function assignVariant(opts: {
  queryVariant?: string | null;
  cookieVariant?: string | null;
  seed?: string;
}): { variant: AbVariant; source: "query" | "cookie" | "assigned" } {
  const fromQuery = normalizeVariant(opts.queryVariant);
  if (fromQuery) return { variant: fromQuery, source: "query" };

  if (!LP_CREATIVE_AB_LIVE) {
    return { variant: PARKED_LP_VARIANT, source: "assigned" };
  }

  const fromCookie = normalizeVariant(opts.cookieVariant);
  if (fromCookie) return { variant: fromCookie, source: "cookie" };

  const seed = opts.seed || `seed_${Date.now()}_${Math.random()}`;
  return { variant: variantFromSeed(seed), source: "assigned" };
}
