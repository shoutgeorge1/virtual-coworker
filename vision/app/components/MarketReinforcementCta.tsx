"use client";

/**
 * Market-specific CTA reinforcement — sticky bottom bar, not a modal.
 * US → phone (same tel: as inline CTAs). AU → book (same /au/book path).
 * Trigger: ~42s dwell OR ~50% scroll, whichever first. Once per session.
 * Clicks reuse canonical phone_cta_clicked / calendly_cta_clicked only.
 * Impression/view is NOT a conversion.
 */

import { useEffect, useState, type MouseEvent } from "react";
import type { MarketId } from "../../config/markets";
import {
  CONVERSION_ASSIST,
  hasReachedReinforcementScroll,
  isFormBusy,
  markReinforcementSeen,
  wasPrimaryConverted,
  wasReinforcementSeen,
} from "../../lib/conversion-assist";
import { bookPathForMarket, withCurrentSearch } from "../../lib/preserve-query";
import {
  trackCalendlyClick,
  trackPhoneClick,
} from "../../lib/tracking";

const CTA_PLACEMENT = "reinforcement_sticky";

type Props = {
  market: MarketId;
  phoneHref: string;
  phoneDisplay: string;
  category?: string;
  variant?: string;
};

export default function MarketReinforcementCta({
  market,
  phoneHref,
  phoneDisplay,
  category = "",
  variant = "",
}: Props) {
  const [armed, setArmed] = useState(false);
  const [visible, setVisible] = useState(false);
  const [formBlocking, setFormBlocking] = useState(false);

  useEffect(() => {
    if (wasReinforcementSeen() || wasPrimaryConverted()) return;

    let timer: number | undefined;

    const arm = () => {
      setArmed(true);
      window.clearTimeout(timer);
      window.removeEventListener("scroll", onScroll);
    };

    const onScroll = () => {
      if (hasReachedReinforcementScroll()) arm();
    };

    const onConverted = () => {
      setVisible(false);
      markReinforcementSeen();
      window.clearTimeout(timer);
      window.removeEventListener("scroll", onScroll);
    };

    timer = window.setTimeout(arm, CONVERSION_ASSIST.reinforcementMs);
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("vc-primary-converted", onConverted);
    onScroll();

    return () => {
      window.clearTimeout(timer);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("vc-primary-converted", onConverted);
    };
  }, []);

  // Hide only when the quiz card itself is the focus — not the whole #gate band.
  useEffect(() => {
    const card =
      document.querySelector("#gate .sp-quiz-card") ||
      document.getElementById("gate");
    if (!card || typeof IntersectionObserver === "undefined") return;
    const io = new IntersectionObserver(
      ([entry]) => {
        setFormBlocking(
          entry.isIntersecting && entry.intersectionRatio >= 0.35,
        );
      },
      { threshold: [0, 0.2, 0.35, 0.55, 0.8] },
    );
    io.observe(card);
    return () => io.disconnect();
  }, []);

  // Reveal when armed and form is not blocking. Mark seen only on real display.
  useEffect(() => {
    if (!armed || wasReinforcementSeen() || wasPrimaryConverted()) return;
    if (formBlocking || isFormBusy()) {
      setVisible(false);
      return;
    }
    setVisible(true);
    markReinforcementSeen();
  }, [armed, formBlocking]);

  useEffect(() => {
    if (!visible) return;
    const onFocusIn = () => {
      if (isFormBusy()) setVisible(false);
    };
    document.addEventListener("focusin", onFocusIn);
    return () => document.removeEventListener("focusin", onFocusIn);
  }, [visible]);

  function dismiss() {
    setVisible(false);
    setArmed(false);
    markReinforcementSeen();
  }

  function onPhoneClick() {
    trackPhoneClick({
      market,
      category,
      variant,
      cta_location: CTA_PLACEMENT,
      cta_placement: CTA_PLACEMENT,
      cta_type: "phone",
      href: phoneHref,
    });
  }

  function onBookClick(e: MouseEvent<HTMLAnchorElement>) {
    const next = withCurrentSearch(bookPathForMarket(market));
    trackCalendlyClick({
      market,
      category,
      variant,
      cta_location: CTA_PLACEMENT,
      cta_placement: CTA_PLACEMENT,
      cta_type: "booking",
      href: next,
      bidding_primary: false,
    });
    if (next === bookPathForMarket(market)) return;
    e.preventDefault();
    window.location.assign(next);
  }

  if (!visible || formBlocking) return null;

  const isUs = market === "us";

  return (
    <aside
      className="mkt-reinforce"
      role="complementary"
      aria-label={isUs ? "Call reinforcement" : "Booking reinforcement"}
      data-market={market}
      data-cta-type={isUs ? "phone" : "booking"}
      data-cta-placement={CTA_PLACEMENT}
    >
      <div className="mkt-reinforce-inner">
        <p className="mkt-reinforce-copy">
          {isUs
            ? "Talk to a Staffing Specialist"
            : "Ready to Discuss Your Staffing Needs?"}
        </p>
        {isUs ? (
          <a
            className="mkt-reinforce-cta"
            href={phoneHref}
            onClick={onPhoneClick}
          >
            Call Now · {phoneDisplay}
          </a>
        ) : (
          <a
            className="mkt-reinforce-cta"
            href={bookPathForMarket(market)}
            onClick={onBookClick}
          >
            Book a Consultation
          </a>
        )}
        <button
          type="button"
          className="mkt-reinforce-dismiss"
          aria-label="Dismiss"
          onClick={dismiss}
        >
          ×
        </button>
      </div>
    </aside>
  );
}
