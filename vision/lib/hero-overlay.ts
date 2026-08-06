/**
 * Optional hero-image overlay treatments for QA / Stage-1 A/B review.
 * Independent of copy variant (?variant=a|b). Default = current LP chrome
 * (small role tag only — not forced onto Ads Final URLs).
 *
 * badge — circular commitment + rate/PH secondary (nicest preview path)
 * pill  — stacked horizontal pills on the photo
 * hot   — badge treatment + hot-pink H1 accent (Meta-energy, still same LP)
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
