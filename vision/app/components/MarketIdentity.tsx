"use client";

import { useEffect } from "react";
import {
  resolveGa4Id,
  resolveGtmId,
  type TrackingSurface,
} from "../../lib/market-tracking";

/**
 * Pushes a durable site identity onto dataLayer once per mount.
 * GTM containers should key off `market` / `site_surface` — not one shared bag.
 * ga4_measurement_id is informational for GTM maps (empty until env is set).
 */
export default function MarketIdentity({
  surface,
}: {
  surface: TrackingSurface;
}) {
  useEffect(() => {
    const gtmId = resolveGtmId(surface);
    const ga4Id = resolveGa4Id(surface);
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: "site_identity",
      market: surface,
      site_surface: surface,
      site_type:
        surface === "ph" ? "talent_careers" : "employer_hiring",
      gtm_container_id: gtmId || undefined,
      ga4_measurement_id: ga4Id || undefined,
      measurement_configured: Boolean(gtmId || ga4Id),
    });
  }, [surface]);

  return null;
}
