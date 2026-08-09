/**
 * Master 4-step hiring process copy.
 * Used by How it works + Start hiring (market landing) so wording cannot drift.
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
      t: "Free hiring consult",
      d: isAu
        ? "Tell us the role. We’ll have a short chat, talk through Australian hours, and map the seat — free, no pressure."
        : "Tell us the role. We jump on a short call, share what works, and map the seat — free, no pressure.",
    },
    {
      k: "02 · Hunt",
      t: "We recruit. You get the shortlist.",
      d: "Our Philippines team finds and screens people. Huge English-speaking talent pool. You get strong candidates handed over — not a pile of random resumes.",
    },
    {
      k: "03 · Pick",
      t: "You pick who you want",
      d: "Meet them on video. Screen who you like. These candidates are that good — you’re going to find someone fast.",
    },
    {
      k: "04 · Go",
      t: "Forget the paperwork",
      d: isAu
        ? "Onboarding, employment admin, emails — we handle it. Teammate ready to work Australian hours. You’re sorted."
        : "Onboarding, payroll, emails — we handle it. Gift-wrapped teammate, on your desk, ready to go.",
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
