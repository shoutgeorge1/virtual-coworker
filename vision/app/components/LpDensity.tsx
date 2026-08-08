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
 * Assignment is written to `<html data-lp-density>` by the inline script in
 * layout.tsx before first paint; this component only re-confirms it and fires
 * the view event once per session.
 */
export default function LpDensity({ market }: { market: MarketId }) {
  useEffect(() => {
    const variant = assignExperiment("lp_density");
    const density = densityFromVariant(variant);
    document.documentElement.dataset.lpDensity = density;
    trackExperimentView("lp_density", variant, {
      surface: "market_landing",
      market,
      density,
    });
  }, [market]);

  return null;
}
