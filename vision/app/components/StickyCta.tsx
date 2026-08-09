"use client";

import type { MouseEvent } from "react";
import { trackPhoneClick } from "../../lib/tracking";
import { focusGate } from "../../lib/focus-gate";
import { trackExperimentConvert } from "../../lib/experiments";
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
  const goTarget = (e: MouseEvent<HTMLAnchorElement>) => {
    if (href.includes("#gate")) {
      e.preventDefault();
      focusGate({ behavior: "smooth" });
      return;
    }
    if (href.includes("#role-quiz")) {
      e.preventDefault();
      document.getElementById("role-quiz")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  };

  return (
    <div className="sticky-cta">
      {phoneHref ? (
        <a
          className="sticky-cta-call"
          href={phoneHref}
          onClick={() => {
            trackPhoneClick({
              market,
              category: category || "",
              variant: variant || "",
            });
            trackExperimentConvert("phone_click", {
              market,
              source: "sticky_cta",
            });
          }}
        >
          <span aria-hidden>☎</span>
          <b>{phoneDisplay}</b>
        </a>
      ) : null}
      <a className="sticky-cta-go" href={href} onClick={goTarget}>
        {label}
      </a>
    </div>
  );
}
