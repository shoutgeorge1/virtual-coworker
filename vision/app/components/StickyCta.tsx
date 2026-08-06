"use client";

import { trackEvent } from "../../lib/tracking";
import type { MarketId } from "../../config/markets";
import type { AbVariant } from "../../config/categories";

/* Mobile conversion bar — form + phone only. */
export default function StickyCta({
  href,
  label,
  phoneDisplay,
  phoneHref,
  market,
  category,
  variant,
}: {
  href: string;
  label: string;
  phoneDisplay?: string;
  phoneHref?: string | null;
  market: MarketId;
  category?: string;
  variant?: AbVariant;
}) {
  return (
    <div className="sticky-cta">
      {phoneHref ? (
        <a
          className="sticky-cta-call"
          href={phoneHref}
          onClick={() =>
            trackEvent("phone_cta_clicked", {
              market,
              category: category || "",
              variant: variant || "",
              is_qualified_call: false,
            })
          }
        >
          <span aria-hidden>☎</span>
          <b>{phoneDisplay}</b>
        </a>
      ) : null}
      <a className="sticky-cta-go" href={href}>
        {label}
      </a>
    </div>
  );
}
