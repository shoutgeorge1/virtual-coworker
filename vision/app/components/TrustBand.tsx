import type { MarketId } from "../../config/markets";
import {
  PUBLIC_QUOTES,
  TRUST_PROOF,
  clientMarksForMarket,
  industryStatsForMarket,
  proofFigures,
} from "../../config/site";
import { ProofRow, StatsGrid } from "./TrustAnimated";

/**
 * Legitimacy band — recognition, client marks, reviews, stats.
 *
 * Hierarchy (designer pass 2026-08-07):
 *  1. Track-record figures
 *  2. Reviews + Clutch rating (human proof — must breathe; no logos on cards)
 *  3. Client logo strip (companies only)
 *  4. Slim recognition row (not four fat badge cards)
 *  5. Industry stats
 *  6. Trust chips (people/process — addresses live in footer only)
 *
 * No outbound links on marks. Reviews stay on both lp_density arms.
 */
export default function TrustBand({
  market,
  light = false,
}: {
  market: MarketId;
  light?: boolean;
}) {
  const stats = industryStatsForMarket(market);
  const figures = proofFigures();
  const clientMarks = clientMarksForMarket(market);
  const quotes = PUBLIC_QUOTES;

  /** Slim recognition — Clutch + Forbes + tenure. Google lives in hero chips. */
  const recog = [
    {
      src:
        market === "us"
          ? "/brand/trust/badge-clutch-us-2024.webp"
          : "/brand/badge-clutch-au.webp",
      alt:
        market === "us"
          ? "Clutch top virtual assistant company — United States 2024"
          : "Clutch top virtual assistant company — Australia",
      label: "Clutch",
    },
    {
      src:
        market === "us"
          ? "/brand/badge-forbes-white.webp"
          : "/brand/badge-forbes-navy.webp",
      alt: "Forbes Business Council",
      label: "Forbes",
    },
    {
      src: "/brand/trust/badge-14-year.webp",
      alt: `Founded ${TRUST_PROOF.sinceYear}`,
      label: `Since ${TRUST_PROOF.sinceYear}`,
    },
  ];

  return (
    <section
      className={`trust-band${light ? " trust-band-light" : ""}`}
      aria-labelledby="trust-band-title"
    >
      <div className="trust-band-inner">
        <header className="trust-band-head">
          <p className="trust-band-label">Happy customers</p>
          <h2 id="trust-band-title">
            Since {TRUST_PROOF.sinceYear}. Real reviews. Real hires.
          </h2>
        </header>

        <ProofRow figures={figures} />

        {/* Reviews lead — quotes need air, not a badge pile above them */}
        <div className="trust-band-quotes">
          <div className="trust-band-quotes-head">
            <p className="trust-band-quotes-label">What hiring managers say</p>
            <span
              className="trust-rating-pill"
              aria-label={`Clutch ${TRUST_PROOF.clutch.rating} out of 5 from ${TRUST_PROOF.clutch.reviewCount} reviews`}
            >
              <span aria-hidden="true">★★★★★</span>
              <b>
                {TRUST_PROOF.clutch.rating}
                <i>/5</i>
              </b>
              <span>Clutch · {TRUST_PROOF.clutch.reviewCount} reviews</span>
            </span>
          </div>
          <div className="trust-quotes-grid">
            {quotes.map((q) => (
              <figure className="trust-quote-card" key={q.name}>
                <blockquote>“{q.quote}”</blockquote>
                <figcaption>
                  <b>{q.name}</b>
                  <span>
                    {q.role}
                    {q.company ? ` · ${q.company}` : ""}
                  </span>
                </figcaption>
              </figure>
            ))}
          </div>
        </div>

        {clientMarks.length > 0 ? (
          <div
            className="trust-clients"
            aria-label="Companies that have hired through Virtual Coworker"
          >
            <p className="trust-press-label">Companies that hired through us</p>
            <ul className="trust-clients-row">
              {clientMarks.map((c) => {
                const label = c.alt || c.name;
                return (
                  <li
                    className={`trust-client-mark${c.caption ? " has-caption" : ""}`}
                    key={c.id}
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={c.src}
                      alt={label}
                      title={label}
                      loading="lazy"
                    />
                    {c.caption ? (
                      <span className="trust-client-caption" aria-hidden="true">
                        {c.caption}
                      </span>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          </div>
        ) : null}

        <div className="trust-recog" aria-label="Recognition">
          <p className="trust-press-label">Recognition</p>
          <ul className="trust-recog-row">
            {recog.map((b) => (
              <li className="trust-recog-item" key={b.src}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={b.src} alt={b.alt} width={72} height={72} />
                <span>{b.label}</span>
              </li>
            ))}
          </ul>
        </div>

        <div
          className="trust-band-stats"
          aria-labelledby="trust-stats-title"
          data-lp="secondary"
        >
          <p className="trust-band-stats-label">What you gain offshore</p>
          <h3 id="trust-stats-title">
            Good people. Your hours. More left in the budget.
          </h3>
          <p className="trust-band-stats-lead">
            Published research — not our marketing claims.
          </p>
          <StatsGrid stats={stats} />
        </div>

        <div className="trust-band-legit" aria-label="Company legitimacy">
          <div className="trust-legit-item">
            <span className="trust-legit-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
                <path
                  d="M12 3.5l1.6 4.2h4.4l-3.5 2.7 1.3 4.3L12 12.7 8.2 14.7l1.3-4.3-3.5-2.7h4.4L12 3.5z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            <div>
              <strong>Since {TRUST_PROOF.sinceYear}</strong>
              <span>Filipino staffing partner — still here</span>
            </div>
          </div>
          <div className="trust-legit-item">
            <span className="trust-legit-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
                <circle
                  cx="12"
                  cy="12"
                  r="8.25"
                  stroke="currentColor"
                  strokeWidth="1.5"
                />
                <path
                  d="M4.5 12h15M12 3.75c2.4 2.6 3.6 5.3 3.6 8.25S14.4 17.65 12 20.25C9.6 17.65 8.4 14.95 8.4 12S9.6 6.35 12 3.75z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            <div>
              <strong>US &amp; Australia</strong>
              <span>Built for both markets’ business hours</span>
            </div>
          </div>
          <div className="trust-legit-item">
            <span className="trust-legit-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
                <path
                  d="M8.5 11.5a2.75 2.75 0 115.5 0v1.25H8.5V11.5z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                />
                <path
                  d="M6.75 12.75h10.5v5.5a1.5 1.5 0 01-1.5 1.5H8.25a1.5 1.5 0 01-1.5-1.5v-5.5z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinejoin="round"
                />
                <path
                  d="M12 4.5v2.25M9.25 5.75l1.1 1.1M14.75 5.75l-1.1 1.1"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
            </span>
            <div>
              <strong>You interview first</strong>
              <span>Nobody joins your team before you meet them</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
