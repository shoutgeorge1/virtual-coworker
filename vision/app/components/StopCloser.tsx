import type { MarketId } from "../../config/markets";
import {
  primaryHireCta,
  stopCloserCopy,
  type StopCloserSurface,
} from "../../config/employer-cro";

const STOP_VA = {
  src: "/brand/vc-stop-va-v2.png",
  alt: "Virtual assistant at her desk with both hands up beside a stop sign",
} as const;

/**
 * End-of-page closer — photoreal VA + real metal stop sign in the photo + CTAs.
 * Same *reason* on US + AU; wording is market-native. Role/hub surfaces get
 * a specific second line — not one generic closer pasted everywhere.
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
      className={`lp-stop${light ? " lp-stop-light" : ""}`}
      aria-labelledby="lp-stop-title"
    >
      <div className="lp-stop-inner">
        <figure className="lp-stop-visual">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={STOP_VA.src} alt={STOP_VA.alt} />
        </figure>

        <div className="lp-stop-copy">
          <h2 id="lp-stop-title">{copy.title}</h2>
          <p className="lp-stop-lead">
            {copy.lines.map((line, i) => (
              <span key={line}>
                {i > 0 ? <br /> : null}
                {line}
              </span>
            ))}
          </p>
          <div className="lp-stop-actions">
            <a
              href={ctaHref}
              className={`${shell}-btn ${shell}-btn-primary lp-stop-primary`}
            >
              {cta}
            </a>
            {showPhone && phoneHref ? (
              <a
                href={phoneHref}
                className={`${shell}-btn ${shell}-btn-ghost lp-stop-call`}
              >
                {callLabel}
              </a>
            ) : null}
          </div>
        </div>
      </div>
    </section>
  );
}
