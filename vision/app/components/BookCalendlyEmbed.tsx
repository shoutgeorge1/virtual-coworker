"use client";

import { useEffect, useRef, useState } from "react";
import {
  loadCalendlyAssets,
  waitForInlineWidget,
} from "../../lib/calendly-assets";
import {
  calendlyScheduledPayloadFromMessage,
  trackCalendlyBookingComplete,
} from "../../lib/calendly-booking";

const CAL_HEIGHT_PX = 700;

/**
 * Inline Calendly for /us/book and /au/book.
 * Listens for calendly.event_scheduled only → calendly_booking_complete.
 */
export default function BookCalendlyEmbed({
  market,
  widgetUrl,
  bookUrl,
}: {
  market: "us" | "au";
  widgetUrl: string;
  bookUrl: string;
}) {
  const calBox = useRef<HTMLDivElement>(null);
  const inited = useRef(false);
  const [embedFailed, setEmbedFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    loadCalendlyAssets()
      .then(() => waitForInlineWidget())
      .then((ready) => {
        if (cancelled || !calBox.current) return;
        if (inited.current) return;
        if (!ready || !window.Calendly?.initInlineWidget) {
          setEmbedFailed(true);
          return;
        }
        inited.current = true;
        calBox.current.innerHTML = "";
        window.Calendly.initInlineWidget({
          url: widgetUrl,
          parentElement: calBox.current,
        });
      })
      .catch(() => {
        if (!cancelled) setEmbedFailed(true);
      });
    return () => {
      cancelled = true;
    };
  }, [widgetUrl]);

  useEffect(() => {
    const onMessage = (event: MessageEvent) => {
      const origin = String(event.origin || "");
      if (!origin.includes("calendly.com")) return;
      const payload = calendlyScheduledPayloadFromMessage(event.data);
      if (!payload) return;
      trackCalendlyBookingComplete({
        market,
        bookUrl,
        payload,
      });
    };
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [market, bookUrl]);

  return (
    <div className="book-cal">
      {!embedFailed ? (
        <div
          ref={calBox}
          className="book-cal-box ty-cal-box"
          style={{ height: CAL_HEIGHT_PX }}
          aria-label="Scheduling calendar"
        />
      ) : null}
      <p
        className={
          embedFailed
            ? "book-cal-fallback book-cal-fallback-strong"
            : "book-cal-fallback book-cal-fallback-quiet"
        }
      >
        {embedFailed ? (
          <a
            href={bookUrl}
            className="micro-btn micro-btn-primary"
            target="_blank"
            rel="noopener noreferrer"
            data-track="calendly_cta_clicked"
            data-market={market}
          >
            Open Scheduling Calendar
          </a>
        ) : (
          <>
            Calendar not loading?{" "}
            <a
              href={bookUrl}
              target="_blank"
              rel="noopener noreferrer"
              data-track="calendly_cta_clicked"
              data-market={market}
            >
              Open Scheduling Calendar
            </a>
          </>
        )}
      </p>
    </div>
  );
}
