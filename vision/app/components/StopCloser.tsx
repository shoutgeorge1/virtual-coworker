import type { MarketId } from "../../config/markets";
import {
  primaryHireCta,
  stopCloserCopy,
  type StopCloserSurface,
} from "../../config/employer-cro";

/**
 * End-of-page closing CTA — same sell-band language as the rest of the LP.
 * No stop-sign imagery; calm next-step copy + form / phone CTAs.
 */
export default function StopCloser({
  market,
  light = false,
  showPhone,
  phoneDisplay,
  phoneHref,
  surface = "home",
  ctaHref = "#gate",
}: {
  market: MarketId;
  light?: boolean;
  showPhone: boolean;
  phoneDisplay?: string;
  phoneHref?: string | null;
  surface?: StopCloserSurface;
  /** Hub pages point at /us#gate or /au#gate — not a local #gate. */
  ctaHref?: string;
}) {
  const shell = market === "us" ? "us" : "au";
  const copy = stopCloserCopy(market, surface);
  const cta = primaryHireCta(market);
  const callLabel =
    market === "au"
      ? `Give us a call · ${phoneDisplay}`
      : `Call our team · ${phoneDisplay}`;

  return (
    <section
      className={`lp-close ${shell}-sell${light ? " lp-close-light" : ""}`}
      aria-labelledby="lp-close-title"
    >
      <div className={`${shell}-sell-inner lp-close-inner`}>
        <header className="lp-close-head">
          <p className={market === "us" ? "us-proof-label" : "au-proof-label"}>
            {copy.eyebrow}
          </p>
          <h2 id="lp-close-title">{copy.title}</h2>
          <p className="lp-close-lead">{copy.lead}</p>
        </header>
        <div className="lp-close-actions">
          <a
            href={ctaHref}
            className={`${shell}-btn ${shell}-btn-primary lp-close-primary`}
          >
            {cta}
          </a>
          {showPhone && phoneHref ? (
            <a
              href={phoneHref}
              className={`${shell}-btn ${shell}-btn-ghost lp-close-call`}
            >
              {callLabel}
            </a>
          ) : null}
        </div>
      </div>
    </section>
  );
}
