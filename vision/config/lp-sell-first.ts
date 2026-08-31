/**
 * Sell-first above-fold challenger. Sibling of /us and /au (control).
 * Same conversion machine: GuidedMatchGate role → hours → people → contact.
 *
 * Principle: MESSAGE → BENEFIT → CTA → TRUST → HUMAN PROOF → QUALIFICATION.
 * Do not invent prices. Headline A is the default; ?h=b|c|d is QA only.
 */

import type { MarketId } from "./markets";
import { CATEGORY_SLUGS } from "./categories";
import { marketLandingCopy } from "./guided-match";
import { TRUST_PROOF, googleBusinessForMarket } from "./site";

export const SELL_FIRST_VARIANT = "sell-first" as const;

export const SELL_FIRST_PATHS = {
  us: "/us/start",
  au: "/au/start",
} as const;

export const SELL_FIRST_HEADLINE_IDS = ["a", "b", "c", "d"] as const;
export type SellFirstHeadlineId = (typeof SELL_FIRST_HEADLINE_IDS)[number];

export function sellFirstSlugCollidesWithCategory(): boolean {
  return (CATEGORY_SLUGS as readonly string[]).includes("start");
}

export function normalizeSellFirstHeadline(
  raw?: string | string[],
): SellFirstHeadlineId {
  const v = (Array.isArray(raw) ? raw[0] : raw || "a").trim().toLowerCase();
  if (v === "b" || v === "c" || v === "d") return v;
  return "a";
}

export function sellFirstCopy(
  market: MarketId,
  headlineId: SellFirstHeadlineId = "a",
) {
  const base = marketLandingCopy(market);
  const google = googleBusinessForMarket(market);
  const au = market === "au";
  const headlines: Record<SellFirstHeadlineId, string> = {
    a: au
      ? "Hire experienced Filipino staff who work Australian hours."
      : "Hire experienced Filipino staff who work your hours.",
    b: "Build your team with experienced Filipino virtual staff.",
    c: "Find reliable Filipino talent for the roles slowing your business down.",
    d: au
      ? "Hire pre-vetted Filipino virtual assistants for your Australian business."
      : "Hire pre-vetted Filipino virtual assistants for your business.",
  };
  return {
    market,
    au,
    variant: SELL_FIRST_VARIANT,
    path: SELL_FIRST_PATHS[market],
    headlineId,
    h1: headlines[headlineId],
    lead: au
      ? "We recruit, vet and introduce candidates for admin, bookkeeping, marketing, customer support and more. Dedicated staff for Australian business hours."
      : "We recruit, vet and introduce candidates for admin, bookkeeping, marketing, customer support and more.",
    cta: "Find my virtual assistant",
    compactProof: `${google.rating} Google · ${TRUST_PROOF.clutch.rating} Clutch`,
    sinceLine: `Trusted by businesses since ${base.sinceYear}`,
    phoneDisplay: base.phoneDisplay,
    phoneHref: base.phoneHref,
    heroSrc: base.heroSrc,
    heroAlt: base.heroAlt,
    sinceYear: base.sinceYear,
  };
}
