"use client";

import { useEffect } from "react";
import {
  trackCalendlyClick,
  trackEvent,
  trackPhoneClick,
} from "../../lib/tracking";

/**
 * Fires dataLayer events for anchors/buttons marked with data-track="…".
 * Phone / Calendly use helpers that also emit short aliases for GTM maps.
 */
export default function DataTrackClicks() {
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const target = e.target;
      if (!(target instanceof Element)) return;
      const el = target.closest("[data-track]");
      if (!(el instanceof HTMLElement)) return;
      const name = (el.getAttribute("data-track") || "").trim();
      if (!name) return;

      const market =
        el.getAttribute("data-market") ||
        document.body?.getAttribute("data-market") ||
        "";
      const href =
        el instanceof HTMLAnchorElement
          ? el.href
          : el.getAttribute("href") || undefined;

      if (name === "phone_cta_clicked" || name === "phone_click") {
        trackPhoneClick({ market, href });
        return;
      }
      if (name === "calendly_cta_clicked" || name === "calendly_click") {
        trackCalendlyClick({ market, href });
        return;
      }

      trackEvent(name, { market, href });
    };

    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);

  return null;
}
