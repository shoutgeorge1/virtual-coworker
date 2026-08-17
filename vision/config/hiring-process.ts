/**
 * Master 4-step hiring process copy.
 * Used by How it works + Start hiring (market landing) so wording cannot drift.
 *
 * Maps the CEO / WordPress white-glove flow into four scannable cards:
 * consult + job description → recruit/vet → profiles + hourly rates + interviews
 * → onboarding, payroll/HR, time tracking, ongoing support.
 */

import type { MarketId } from "./markets";

export type HiringProcessStep = {
  /** Display key, e.g. "01 · Talk" or "01" */
  k: string;
  t: string;
  d: string;
};

/** Full labels for the How it works page. */
export function hiringProcessSteps(market: MarketId): HiringProcessStep[] {
  const isAu = market === "au";
  return [
    {
      k: "01 · Talk",
      t: "Free strategy call",
      d: isAu
        ? "A short chat to understand your company, the role, and how many people you need. Then we write the job description with you - obligation free, at no cost."
        : "A short call to understand your company, the role, and how many people you need. Then we write the job description with you - obligation free, at no cost.",
    },
    {
      k: "02 · Hunt",
      t: "We recruit and rigorously vet",
      d: "Our Philippines team sources and screens candidates. Hundreds of applications get filtered so you review people who fit the role - not a pile of random resumes, and not a freelancer marketplace.",
    },
    {
      k: "03 · Pick",
      t: "Profiles, interviews, you choose",
      d: "You receive candidate profiles with transparent hourly rates. Meet them on video. Nobody starts until you say yes.",
    },
    {
      k: "04 · Go",
      t: "We stay on after they start",
      d: isAu
        ? "Onboarding, employment admin, and our time tracker. Ongoing support so the seat keeps working on Australian hours."
        : "Onboarding, payroll, HR, and our time tracker. Ongoing support so the seat keeps working on your hours.",
    },
  ];
}

/** Compact keys for the market landing process strip. */
export function hiringProcessStrip(market: MarketId): HiringProcessStep[] {
  return hiringProcessSteps(market).map((s) => ({
    ...s,
    k: s.k.slice(0, 2),
  }));
}
