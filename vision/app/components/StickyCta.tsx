"use client";

import { trackPhoneClick } from "../../lib/tracking";
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
            trackPhoneClick({
              market,
              category: category || "",
              variant: variant || "",
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
