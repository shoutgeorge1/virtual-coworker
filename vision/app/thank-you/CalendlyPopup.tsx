"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import {
  calendlyAssetsReady,
  loadCalendlyAssets,
  waitForInlineWidget,
} from "../../lib/calendly-assets";
import { claimCalendlyAutoOpen, THANK_YOU_BOOKING_COPY } from "../../lib/calendly";
import { trackEvent } from "../../lib/tracking";

/** Short pause so Call paints before the overlay. Do not wait long enough to bounce. */
const AUTO_OPEN_DELAY_MS = 300;
const CAL_HEIGHT_PX = 660;

/** One embed-view event per widget URL for this page load. Not Ads Primary. */
let embedViewedPopupUrl = "";

function claimCalendlyEmbedViewed(widgetUrl: string): boolean {
  if (!widgetUrl || embedViewedPopupUrl === widgetUrl) return false;
  embedViewedPopupUrl = widgetUrl;
  return true;
}

/**
 * Thank-you overlay: hiring consult + Call + Calendly initInlineWidget.
 * Native Calendly popup chrome cannot take our copy and its Close is unreliable
 * on this page, so we finish this widget (portaled to body) instead.
 * Eligible thank-you auto-opens once. "Schedule a call" reopens after dismiss,
 * or opens a new tab if the widget fails. Overlay open is calendly_embed_viewed
 * only (not Ads Primary). GTM already maps Calendly calendly.event_scheduled
 * to calendly_event_scheduled - do not push that event from here.
 */
export default function CalendlyPopup({
  widgetUrl,
  bookUrl,
  market,
  label,
  autoOpen = false,
  phoneDisplay,
  phoneHref,
}: {
  widgetUrl: string;
  bookUrl: string;
  market: string;
  label: string;
  autoOpen?: boolean;
  phoneDisplay?: string;
  phoneHref?: string | null;
}) {
  const isAu = market === "au";
  const copy = isAu ? THANK_YOU_BOOKING_COPY.au : THANK_YOU_BOOKING_COPY.us;
  const showPhone = Boolean(phoneHref && phoneDisplay);
  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const preloaded = useRef(false);
  const calBox = useRef<HTMLDivElement>(null);
  const initedForOpen = useRef(false);
  const closeBtn = useRef<HTMLButtonElement>(null);
  const triggerRef = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  const close = useCallback(() => {
    setOpen(false);
    initedForOpen.current = false;
    window.setTimeout(() => triggerRef.current?.focus(), 0);
  }, []);

  const openOverlay = useCallback(() => {
    setOpen(true);
  }, []);

  useEffect(() => {
    let cancelled = false;
    let timer: number | undefined;

    loadCalendlyAssets()
      .then(() => {
        if (cancelled || !window.Calendly) return;
        if (!preloaded.current && window.Calendly.preload) {
          preloaded.current = true;
          window.Calendly.preload(widgetUrl);
        }
        if (!autoOpen) return;
        timer = window.setTimeout(() => {
          if (cancelled) return;
          if (!claimCalendlyAutoOpen(widgetUrl)) return;
          setOpen(true);
        }, AUTO_OPEN_DELAY_MS);
      })
      .catch(() => {
        /* hosted Calendly link still works */
      });

    return () => {
      cancelled = true;
      if (timer !== undefined) window.clearTimeout(timer);
    };
  }, [widgetUrl, autoOpen]);

  useEffect(() => {
    if (!open) return;
    document.documentElement.classList.add("vc-popup-open");
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    window.addEventListener("keydown", onKey);
    window.setTimeout(() => closeBtn.current?.focus(), 0);
    return () => {
      document.documentElement.classList.remove("vc-popup-open");
      document.body.style.overflow = prevOverflow;
      window.removeEventListener("keydown", onKey);
    };
  }, [open, close]);

  useEffect(() => {
    if (!open) return;
    if (!claimCalendlyEmbedViewed(widgetUrl)) return;
    trackEvent("calendly_embed_viewed", {
      market,
      href: bookUrl,
      bidding_primary: false,
      is_qualified_call: false,
    });
  }, [open, widgetUrl, bookUrl, market]);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    loadCalendlyAssets()
      .then(() => waitForInlineWidget())
      .then((ready) => {
        if (cancelled || !calBox.current) return;
        if (initedForOpen.current) return;
        if (!ready || !window.Calendly?.initInlineWidget) return;
        initedForOpen.current = true;
        calBox.current.innerHTML = "";
        window.Calendly.initInlineWidget({
          url: widgetUrl,
          parentElement: calBox.current,
        });
      })
      .catch(() => {
        /* hosted Schedule a call link still works */
      });
    return () => {
      cancelled = true;
    };
  }, [open, widgetUrl]);

  const overlay =
    open && mounted ? (
      <div
        className={`ty-cal-overlay${isAu ? " ty-cal-overlay-au" : " ty-cal-overlay-us"}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="ty-cal-title"
        style={{ zIndex: 120 }}
      >
        <button
          type="button"
          className="ty-cal-scrim"
          aria-label="Close calendar"
          onClick={close}
        />
        <div className="ty-cal-panel">
          <button
            ref={closeBtn}
            type="button"
            className="ty-cal-close"
            aria-label="Close"
            onClick={close}
          >
            ×
          </button>
          <p className="ty-cal-eyebrow">{copy.eyebrow}</p>
          <h2 id="ty-cal-title">{copy.headline}</h2>
          <p className="ty-cal-sub">{copy.sub}</p>
          {showPhone ? (
            <a
              href={phoneHref!}
              className="ty-cal-call"
              data-track="phone_cta_clicked"
            >
              Or call {phoneDisplay}
            </a>
          ) : null}
          <div
            ref={calBox}
            className="ty-cal-box"
            style={{ height: CAL_HEIGHT_PX }}
          />
        </div>
      </div>
    ) : null;

  return (
    <>
      <a
        ref={triggerRef}
        href={bookUrl}
        className="micro-btn micro-btn-primary thank-you-book-primary"
        target="_blank"
        rel="noopener noreferrer"
        data-track="calendly_cta_clicked"
        data-market={market}
        onClick={(event) => {
          if (!calendlyAssetsReady()) return;
          event.preventDefault();
          openOverlay();
        }}
      >
        {label}
      </a>
      {overlay && createPortal(overlay, document.body)}
    </>
  );
}
