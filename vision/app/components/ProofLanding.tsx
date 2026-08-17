"use client";

import type { MarketId } from "../../config/markets";
import { JOB_SEEKER_LINE } from "../../config/guided-match";
import { proofFunnelCopy } from "../../config/lp-funnel-challengers";
import { DEFAULT_CAREERS_URL } from "../../config/markets";
import { trackPhoneClick, trackEvent } from "../../lib/tracking";
import GuidedMatchGate from "./GuidedMatchGate";
import "../guided-match.css";
import "../funnel-challengers.css";

type Props = {
  market: MarketId;
  careersHref?: string;
};

export default function ProofLanding({
  market,
  careersHref = DEFAULT_CAREERS_URL,
}: Props) {
  const copy = proofFunnelCopy(market);

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
    <div className="gm st" data-funnel={copy.variant} data-market={market}>
      <section className="st-hero">
        <img
          className="st-hero-photo"
          src={copy.heroSrc}
          alt={copy.heroAlt}
          width={1600}
          height={1060}
          fetchPriority="high"
          decoding="async"
        />
        <div className="gm-wrap st-nav-wrap">
          <nav className="st-nav" aria-label="Employer hiring">
            <span className="lp-logo-chip">
              <img src="/brand/logo-vc.png" alt="Virtual Coworker" width={148} height={28} />
            </span>
            <a
              className="gm-call"
              href={copy.phoneHref}
              onClick={onPhone}
              style={{ marginLeft: "auto" }}
            >
              {copy.phoneDisplay}
            </a>
          </nav>
        </div>
        <div className="gm-wrap">
          <div className="st-hero-inner">
            <div className="st-hero-plate">
              <p className="of-kicker" style={{ color: "var(--gm-gold)" }}>
                {copy.eyebrow}
              </p>
              <h1>{copy.situation}</h1>
              <p className="st-books">{copy.booksLine}</p>
              <p>
                {copy.quote.by}
                {copy.quote.company ? ` · ${copy.quote.company}` : ""} · {copy.googleLine}
              </p>
              <a className="st-hero-jump" href="#hire">
                See how hiring works
              </a>
            </div>
          </div>
        </div>
      </section>

      <section className="st-story">
        <div className="gm-wrap st-story-grid">
          <div>
            <p className="of-kicker">{copy.situationKicker}</p>
            <p className="st-pull">“{copy.quote.text}”</p>
            <cite>
              {copy.quote.by}
              {copy.quote.company ? ` · ${copy.quote.company}` : ""}
            </cite>
          </div>
          <aside className="st-meta">
            <p className="st-support">“{copy.supportQuote.text}”</p>
            <cite>{copy.supportQuote.by}</cite>
            <p style={{ marginTop: "0.9rem" }}>
              {copy.clutchLine} · Serving employers since {copy.sinceYear}
            </p>
          </aside>
        </div>
      </section>

      <section className="st-beats" id="hire">
        <div className="gm-wrap">
          <h2>{copy.beatsTitle}</h2>
          <div className="st-beat-list">
            {copy.beats.map((beat) => (
              <article className="st-beat" key={beat.k}>
                <b>{beat.k}</b>
                <div>
                  <h3>{beat.t}</h3>
                  <p>{beat.d}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="st-form-band" id="gate-band">
        <div className="gm-wrap st-form-grid">
          <div>
            <p className="of-kicker" style={{ color: "var(--gm-gold)" }}>
              {copy.formEyebrow}
            </p>
            <h2>{copy.formTitle}</h2>
            <p className="gm-lead">{copy.formLead}</p>
            <img
              className="st-team"
              src={copy.teamSrc}
              alt={copy.teamAlt}
              width={1200}
              height={800}
              loading="lazy"
            />
          </div>
          <div className="st-form-card">
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

      <footer className="st-footer">
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
