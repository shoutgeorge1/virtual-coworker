"use client";

import { useEffect, useState, type MouseEvent } from "react";
import { trackPhoneClick } from "../../lib/tracking";
import { focusGate } from "../../lib/focus-gate";
import { trackExperimentConvert } from "../../lib/experiments";
import type { MarketId } from "../../config/markets";
import type { AbVariant } from "../../config/categories";

/**
 * Mobile conversion bar — form / book is the hero.
 * Phone (if passed) is a quiet text link, never co-equal weight.
 * Hidden while the gate (or quiz) target is still on screen so short LPs
 * can absorb first without a competing sticky strip.
 */
export default function StickyCta({
  href,
  label,
  phoneDisplay,
  phoneHref,
  market,
  category,
  variant,
  observeSubmit = false,
}: {
  href: string;
  label: string;
  phoneDisplay?: string;
  phoneHref?: string | null;
  market: MarketId;
  category?: string;
  variant?: AbVariant;
  /** Ungated employer LPs: keep the bar until the form submit button is on screen. */
  observeSubmit?: boolean;
}) {
  const [quizFormReady, setQuizFormReady] = useState(false);
  const [targetInView, setTargetInView] = useState(true);

  useEffect(() => {
    const onReady = () => setQuizFormReady(true);
    const onRetake = () => setQuizFormReady(false);
    window.addEventListener("vc-quiz-form-ready", onReady);
    window.addEventListener("vc-quiz-retake", onRetake);
    return () => {
      window.removeEventListener("vc-quiz-form-ready", onReady);
      window.removeEventListener("vc-quiz-retake", onRetake);
    };
  }, []);

  useEffect(() => {
    const id = href.includes("#role-quiz") ? "role-quiz" : "gate";
    const el = observeSubmit
      ? document.querySelector("#gate .gate-submit") || document.getElementById(id)
      : document.getElementById(id);
    if (!el || typeof IntersectionObserver === "undefined") {
      setTargetInView(false);
      return;
    }
    const io = new IntersectionObserver(
      ([entry]) => {
        setTargetInView(entry.isIntersecting && entry.intersectionRatio > 0.12);
      },
      { threshold: [0, 0.12, 0.35, 0.6] },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [href, observeSubmit]);

  const goHref = quizFormReady ? "#gate" : href;
  const goLabel = quizFormReady
    ? market === "au"
      ? "Leave a brief"
      : "Leave a brief"
    : label;

  const goTarget = (e: MouseEvent<HTMLAnchorElement>) => {
    if (goHref.includes("#gate")) {
      e.preventDefault();
      focusGate({ behavior: "smooth" });
      return;
    }
    if (goHref.includes("#role-quiz")) {
      e.preventDefault();
      document.getElementById("role-quiz")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  };

  // Gate/quiz still visible → let the page breathe; no sticky fight.
  if (targetInView && !quizFormReady) return null;

  return (
    <div className="sticky-cta sticky-cta-book-first">
      <a className="sticky-cta-go" href={goHref} onClick={goTarget}>
        {goLabel}
      </a>
      {phoneHref && phoneDisplay ? (
        <a
          className="sticky-cta-phone-quiet"
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
          Prefer to talk? {phoneDisplay}
        </a>
      ) : null}
    </div>
  );
}
