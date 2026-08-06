/**
 * Optional hero-image overlay treatments for QA / Stage-1 A/B review.
 * Independent of copy variant (?variant=a|b). Default LP chrome stays clean
 * (small role tag only — never the default for all Ads traffic).
 *
 * badge — large circular commitment + rate/PH secondary; soft spectrum ring
 * pill  — large vivid commitment pill + rate/PH secondary
 * hot   — badge + subtle image-side energy (no H1 recolor — overlays only)
 *
 * Max 2 badges. Rate lines only when published on the public Price Guide
 * (see lib/hero-badge-copy.ts).
 */

export type HeroOverlay = "none" | "badge" | "pill" | "hot";

export const HERO_OVERLAYS: HeroOverlay[] = ["none", "badge", "pill", "hot"];

export function normalizeHeroOverlay(
  raw: string | string[] | null | undefined,
): HeroOverlay {
  const v = (Array.isArray(raw) ? raw[0] : raw)?.trim().toLowerCase();
  if (v === "badge" || v === "pill" || v === "hot") return v;
  return "none";
}
