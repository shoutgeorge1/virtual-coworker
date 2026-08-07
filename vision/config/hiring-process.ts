/**
 * Master 4-step hiring process copy.
 * Used by How it works + Start hiring (market landing) so wording cannot drift.
 * Streamlined Aug 2026 after VC stakeholder review (one sentence per step).
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
      t: "Hiring conversation",
      d: isAu
        ? "Tell us the role, and we’ll follow up with a short conversation about your hours, tools, and must-haves — including Australian business hours — to confirm it’s a fit before recruiting starts."
        : "Tell us the role, and we’ll follow up with a short conversation about your hours, tools, and must-haves to confirm it’s a fit before recruiting starts.",
    },
    {
      k: "02 · Brief",
      t: "We recruit and screen",
      d: "Share your job brief, and our Filipino recruitment team sources and screens candidates against it — you get a ready-made shortlist, not a pile of resumes.",
    },
    {
      k: "03 · Choose",
      t: "You interview and decide",
      d: "Meet your shortlist on video, run any testing you need, and decide on your own schedule — with no pressure to hire.",
    },
    {
      k: "04 · Start",
      t: "Onboard with support",
      d: isAu
        ? "Once you hire, we handle onboarding, employment ops, and account support so your new teammate settles in and stays productive from day one."
        : "Once you hire, we handle onboarding, payroll, and account support so your new teammate settles in and stays productive from day one.",
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
