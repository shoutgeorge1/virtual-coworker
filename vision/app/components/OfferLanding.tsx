"use client";

import type { MarketId } from "../../config/markets";
import { JOB_SEEKER_LINE } from "../../config/guided-match";
import { offerFunnelCopy } from "../../config/lp-funnel-challengers";
import { DEFAULT_CAREERS_URL } from "../../config/markets";
import { trackPhoneClick, trackEvent } from "../../lib/tracking";
import GuidedMatchGate from "./GuidedMatchGate";
import "../guided-match.css";
import "../funnel-challengers.css";

type Props = {
  market: MarketId;
  careersHref?: string;
};

export default function OfferLanding({
  market,
  careersHref = DEFAULT_CAREERS_URL,
}: Props) {
  const copy = offerFunnelCopy(market);

  function onPhone() {
    trackPhoneClick({
      market,
      category: "",
      variant: copy.variant,
    });
  }

  function onCareers(e: React.MouseEvent<HTMLAnchorElement>) {
    e.preventDefault();
    trackEvent("job_seeker_redirected", {
      market,
      category: "",
      variant: copy.variant,
      intent: "job_seeker",
      destination: careersHref,
      primary_eligible: false,
      bidding_primary: false,
      source: "paid_lp_footer",
    });
    window.location.replace(careersHref);
  }

  return (
    <div className="gm of" data-funnel={copy.variant} data-market={market}>
      <div className="gm-wrap">
        <nav className="of-nav" aria-label="Employer hiring">
          <span className="lp-logo-chip">
            <img src="/brand/logo-vc.png" alt="Virtual Coworker" width={148} height={28} />
          </span>
          <a className="gm-call" href={copy.phoneHref} onClick={onPhone} style={{ marginLeft: "auto" }}>
            {copy.phoneDisplay}
          </a>
        </nav>
      </div>

      <section className="of-speed">
        <div className="gm-wrap of-speed-grid">
          <div className="of-copy">
            <img
              className="of-portrait"
              src={copy.heroSrc}
              alt={copy.heroAlt}
              width={240}
              height={240}
              fetchPriority="high"
              decoding="async"
            />
            <p className="of-kicker">{copy.eyebrow}</p>
            <h1>{copy.h1}</h1>
            <p className="gm-lead">{copy.lead}</p>
            <ul className="of-chips">
              {copy.chips.map((chip) => (
                <li key={chip}>{chip}</li>
              ))}
            </ul>
            <p className="gm-starline">
              <span className="gm-stars" aria-hidden="true">
                ★★★★★
              </span>{" "}
              {copy.googleLine} · {copy.clutchLine}
            </p>
            <p className="of-audience">{copy.audienceLine}</p>
          </div>
          <div className="of-form-card">
            <GuidedMatchGate
              market={market}
              variant={copy.variant}
              careersHref={careersHref}
              contactFirst
              contactHeading={copy.contactHeading}
            />
          </div>
        </div>
      </section>

      <section className="gm-band mist">
        <div className="gm-wrap">
          <h2>{copy.howTitle}</h2>
          <div className="of-mini">
            {copy.howBeats.map((beat) => (
              <article key={beat.k}>
                <b>
                  {beat.k}. {beat.t}
                </b>
                <p>{beat.d}</p>
              </article>
            ))}
          </div>
          <aside className="of-quote">
            <p>“{copy.quote.text}”</p>
            <cite>{copy.quote.by}</cite>
            <p style={{ marginTop: "0.85rem" }}>{copy.hoursLine}</p>
          </aside>
        </div>
      </section>

      <footer className="of-footer">
        <div className="gm-wrap">
          <strong>{copy.entity}</strong>
          <br />
          {copy.nap}
          <br />
          Philippines recruitment hub · Serving employers since {copy.sinceYear} ·{" "}
          <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a>
          <br />
          <a href={careersHref} onClick={onCareers}>
            {JOB_SEEKER_LINE}
          </a>
        </div>
      </footer>
    </div>
  );
}
