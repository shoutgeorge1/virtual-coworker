"use client";

import { useEffect, useState } from "react";
import { trackEvent } from "../../lib/tracking";
import type { MarketId } from "../../config/markets";
import type { AbVariant } from "../../config/categories";

const SESSION_KEY = "vc_exit_intent_seen";

/**
 * Soft employer conversion assist — exit-intent OR one timed nudge.
 * Employer microsites only. Never mount on /ph.
 * Behind NEXT_PUBLIC_ENABLE_EXIT_INTENT=true + once/session frequency cap.
 */
export default function ExitIntent({
  market,
  gateHref = "#gate",
  category,
  variant,
}: {
  market: MarketId;
  gateHref?: string;
  category?: string;
  variant?: AbVariant;
}) {
  const [open, setOpen] = useState(false);
  const enabled =
    typeof process !== "undefined" &&
    (process.env.NEXT_PUBLIC_ENABLE_EXIT_INTENT || "").trim() === "true";

  useEffect(() => {
    if (!enabled) return;
    if (typeof window === "undefined") return;
    try {
      if (sessionStorage.getItem(SESSION_KEY) === "1") return;
    } catch {
      /* ignore */
    }

    let shown = false;
    const show = (reason: string) => {
      if (shown) return;
      shown = true;
      try {
        sessionStorage.setItem(SESSION_KEY, "1");
      } catch {
        /* ignore */
      }
      setOpen(true);
      trackEvent("conversion_assist_opened", {
        market,
        category: category || "",
        variant: variant || "",
        reason,
        assist_type: "exit_intent",
      });
      // Legacy alias for existing GTM drafts
      trackEvent("exit_intent_shown", {
        market,
        category: category || "",
        variant: variant || "",
        reason,
      });
    };

    const onLeave = (e: MouseEvent) => {
      if (e.clientY <= 8) show("exit_intent");
    };

    const timer = window.setTimeout(() => show("timed_45s"), 45_000);
    document.addEventListener("mouseout", onLeave);

    return () => {
      window.clearTimeout(timer);
      document.removeEventListener("mouseout", onLeave);
    };
  }, [enabled, market, category, variant]);

  if (!enabled || !open) return null;

  const dismiss = () => setOpen(false);

  return (
    <div
      className="exit-intent"
      role="dialog"
      aria-modal="true"
      aria-labelledby="exit-intent-title"
    >
      <button
        type="button"
        className="exit-intent-scrim"
        aria-label="Close"
        onClick={dismiss}
      />
      <div className="exit-intent-card">
        <p className="exit-intent-eyebrow">Businesses · about a minute</p>
        <h2 id="exit-intent-title">Still need to hire someone?</h2>
        <p>
          Tell us the role — we’ll follow up to talk through next steps. Looking
          for work? Use careers in the footer.
        </p>
        <div className="exit-intent-actions">
          <a
            href={gateHref}
            className="exit-intent-primary"
            onClick={() => {
              trackEvent("conversion_assist_cta_clicked", {
                market,
                category: category || "",
                variant: variant || "",
                assist_type: "exit_intent",
              });
              trackEvent("exit_intent_accepted", {
                market,
                category: category || "",
                variant: variant || "",
              });
              dismiss();
            }}
          >
            Tell us who you need →
          </a>
          <button type="button" className="exit-intent-ghost" onClick={dismiss}>
            Not now
          </button>
        </div>
      </div>
    </div>
  );
}
