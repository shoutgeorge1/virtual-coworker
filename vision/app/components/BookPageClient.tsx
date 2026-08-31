"use client";

import { useEffect } from "react";
import { captureAttribution } from "../../lib/tracking";
import { trackLpView } from "../../lib/lp-events";

/** Capture URL attribution + one lp_view for the direct booking page. */
export default function BookPageClient({
  market,
}: {
  market: "us" | "au";
}) {
  useEffect(() => {
    captureAttribution(market, { lp_variant: "calendly_book" });
    trackLpView({
      market,
      page_path: market === "au" ? "/au/book" : "/us/book",
      landing_page_type: "calendly_book",
    });
  }, [market]);

  return null;
}
