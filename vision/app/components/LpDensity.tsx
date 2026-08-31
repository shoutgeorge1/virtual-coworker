"use client";

import { useEffect } from "react";
import {
  assignExperiment,
  densityFromVariant,
  trackExperimentView,
} from "../../lib/experiments";
import type { MarketId } from "../../config/markets";

/**
 * lp_density A/B — wordy (a) vs lean (b) landing page.
 *
 * The lean variant hides everything marked `data-lp="secondary"` and tightens
 * section rhythm via CSS. CTAs, the lead form, the phone number and the core
 * trust marks are never marked secondary, so conversion paths are identical in
 * both arms — only the amount of supporting copy changes.
 *
 * PARKED 2026-08-12: form money LPs force lean; site A/B is off
 * (`EXPERIMENTS_LIVE = false`). This component still paints lean and is
 * ready to resume random assignment when the flag flips back on.
 */
export default function LpDensity({
  market,
  forceLean = false,
}: {
  market: MarketId;
  /** Simplified form LPs: lean is the control (park wordy arm on money pages). */
  forceLean?: boolean;
}) {
  useEffect(() => {
    if (forceLean) {
      document.documentElement.dataset.lpDensity = "lean";
      trackExperimentView("lp_density", "b", {
        surface: "market_landing",
        market,
        density: "lean",
        forced: "1",
      });
      return;
    }
    const variant = assignExperiment("lp_density");
    const density = densityFromVariant(variant);
    document.documentElement.dataset.lpDensity = density;
    trackExperimentView("lp_density", variant, {
      surface: "market_landing",
      market,
      density,
    });
  }, [market, forceLean]);

  return null;
}
