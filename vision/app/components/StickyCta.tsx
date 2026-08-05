"use client";

import { trackEvent } from "../../lib/tracking";
import type { MarketId } from "../../config/markets";

/* Mobile conversion bar — form + phone only. */
export default function StickyCta({
  href,
  label,
  phoneDisplay,
  phoneHref,
  market,
}: {
  href: string;
  label: string;
  phoneDisplay?: string;
  phoneHref?: string | null;
  market: MarketId;
}) {
  return (
    <div className="sticky-cta">
      {phoneHref ? (
        <a
          className="sticky-cta-call"
          href={phoneHref}
          onClick={() => trackEvent("phone_click", { market })}
        >
          <span aria-hidden>☎</span>
          <b>{phoneDisplay}</b>
        </a>
      ) : phoneDisplay ? (
        <span className="sticky-cta-call" aria-label="Business phone placeholder">
          <span aria-hidden>☎</span>
          <b>{phoneDisplay}</b>
        </span>
      ) : null}
      <a className="sticky-cta-go" href={href}>
        {label}
      </a>
    </div>
  );
}
