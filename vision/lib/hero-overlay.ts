/**
 * Optional hero-image overlay treatments for QA / Stage-1 A/B review.
 * Independent of copy variant (?variant=a|b). Default = current LP chrome.
 *
 * badge — polished circular commitment badge on the photo
 * pill  — horizontal pill badge on the photo
 * hot   — circular badge + hot-pink H1 accent (Meta-energy, still same LP)
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
