"use client";

import { useEffect } from "react";
import type { TrackingSurface } from "../../lib/market-tracking";

/**
 * Pushes a durable site identity onto dataLayer once per mount.
 * GTM containers should key off `market` / `site_surface` — not one shared bag.
 */
export default function MarketIdentity({
  surface,
}: {
  surface: TrackingSurface;
}) {
  useEffect(() => {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: "site_identity",
      market: surface,
      site_surface: surface,
      site_type:
        surface === "ph" ? "talent_careers" : "employer_hiring",
    });
  }, [surface]);

  return null;
}
