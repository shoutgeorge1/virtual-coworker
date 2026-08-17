"use client";

import type { MarketId } from "../../config/markets";
import { JOB_SEEKER_LINE } from "../../config/guided-match";
import { consultCopy, consultQuotes } from "../../config/lp-consult";
import { clientMarksForMarket } from "../../config/site";
import { DEFAULT_CAREERS_URL } from "../../config/markets";
import { trackPhoneClick, trackEvent } from "../../lib/tracking";
import GuidedMatchGate from "./GuidedMatchGate";
import "../guided-match.css";
import "../consult-landing.css";

type Props = {
  market: MarketId;
  careersHref?: string;
};

function SectionHead({
  kicker,
  title,
  lead,
}: {
  kicker: string;
  title: string;
  lead?: string;
}) {
  return (
    <header className="gm-sec-head">
      <p className="gm-kicker">{kicker}</p>
      <h2>{title}</h2>
      {lead ? <p className="gm-lead">{lead}</p> : null}
    </header>
  );
}

function Panels({ items }: { items: { t: string; d: string }[] }) {
  const cols = items.length === 4 ? "four" : "three";
  return (
    <div className={`gm-panel-grid ${cols}`}>
      {items.map((item) => (
        <article className="gm-panel" key={item.t}>
          <h3>{item.t}</h3>
          <p>{item.d}</p>
        </article>
      ))}
    </div>
  );
}

export default function ConsultLanding({
  market,
  careersHref = DEFAULT_CAREERS_URL,
}: Props) {
  const copy = consultCopy(market);
  const logos = clientMarksForMarket(market);
  const quotes = consultQuotes();
  const featured = quotes[0];
  const rest = quotes.slice(1);

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
    <div className="gm gm-consult" data-funnel={copy.variant} data-market={market}>
      <div className="gm-wrap">
        <nav className="gm-nav" aria-label="Employer hiring">
          <img src="/brand/logo-vc.png" alt="Virtual Coworker" width={148} height={30} />
          <div className="gm-nav-links">
            <a href="#pain">The call</a>
            <a href="#how">How it works</a>
            <a href="#mixups">Mix-ups</a>
            <a href="#gate">Hire</a>
          </div>
          <a className="gm-call" href={copy.phoneHref} onClick={onPhone}>
            {copy.phoneDisplay}
          </a>
        </nav>
      </div>

      <section className="gm-hero">
        <div className="gm-wrap gm-hero-grid">
          <div>
            <h1>{copy.h1}</h1>
            <p className="gm-lead">{copy.lead}</p>
            <p className="gm-starline">
              <span className="gm-stars" aria-hidden="true">
                ★★★★★
              </span>{" "}
              {copy.googleLine} ·{" "}
              <span className="gm-stars" aria-hidden="true">
                ★★★★★
              </span>{" "}
              {copy.clutchLine}
            </p>
            <div className="gm-gate-card">
              <GuidedMatchGate
                market={market}
                variant={copy.variant}
                careersHref={careersHref}
              />
            </div>
          </div>
          <img
            className="gm-hero-photo"
            src={copy.heroSrc}
            alt={copy.heroAlt}
            width={960}
            height={1280}
            fetchPriority="high"
            decoding="async"
          />
        </div>
      </section>

      <section className="gm-logos" aria-label="Companies we have staffed">
        <div className="gm-wrap">
          <div className="gm-logo-row">
            {logos.map((m) => (
              <img key={m.id} src={m.src} alt={m.alt || m.name} height={32} />
            ))}
          </div>
          <p className="gm-proof-meta">
            Serving employers since {copy.sinceYear} · {copy.linkedin} LinkedIn
          </p>
        </div>
      </section>

      <section className="gm-band mist" id="pain">
        <div className="gm-wrap">
          <SectionHead kicker="01 · The call" title={copy.painsTitle} />
          <Panels items={copy.pains} />
          <img
            className="gm-wide"
            src={copy.sceneSrc}
            alt={copy.sceneAlt}
            width={1600}
            height={900}
            loading="lazy"
            style={{ marginTop: "1.8rem" }}
          />
        </div>
      </section>

      <section className="gm-band white" id="enquire">
        <div className="gm-wrap">
          <SectionHead
            kicker="02 · Why they call"
            title={copy.enquireTitle}
            lead={copy.enquireLead}
          />
          <Panels items={copy.enquire} />
        </div>
      </section>

      <section className="gm-band sand" id="how">
        <div className="gm-wrap">
          <SectionHead
            kicker="03 · How it works"
            title={copy.howTitle}
            lead={copy.howLead}
          />
          <div className="gm-grid-steps">
            {copy.steps.map((step) => (
              <div className="gm-step" key={step.k}>
                <span className="gm-step-k">{step.k}</span>
                <b>{step.t}</b>
                <p>{step.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band white" id="value">
        <div className="gm-wrap">
          <SectionHead kicker="04 · What settles it" title={copy.valueTitle} />
          <Panels items={copy.values} />
        </div>
      </section>

      <section className="gm-band sand" id="mixups">
        <div className="gm-wrap">
          <SectionHead
            kicker="05 · Mix-ups"
            title={copy.mixTitle}
            lead={copy.mixLead}
          />
          <Panels items={copy.mixups} />
        </div>
      </section>

      <section className="gm-band mist" id="stories">
        <div className="gm-wrap">
          <SectionHead kicker="06 · Employers" title={copy.storiesTitle} />
          <div className="gm-quote-grid">
            <aside className="gm-quote feat">
              <p>“{featured.text}”</p>
              <cite>{featured.by}</cite>
            </aside>
            {rest.map((q) => (
              <aside className="gm-quote" key={q.by}>
                <p>“{q.text}”</p>
                <cite>{q.by}</cite>
              </aside>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band white" id="hire">
        <div className="gm-wrap gm-hire-split">
          <div>
            <SectionHead
              kicker="07 · Hire"
              title={copy.gateTitle}
              lead={copy.gateLead}
            />
            <div className="gm-cta-row">
              <a className="gm-submit inline" href="#gate">
                {copy.primaryCta}
              </a>
              <a className="gm-call" href={copy.phoneHref} onClick={onPhone}>
                {copy.phoneDisplay}
              </a>
            </div>
          </div>
          <img
            className="gm-scene"
            src={copy.closerSrc}
            alt={copy.closerAlt}
            width={1200}
            height={800}
            loading="lazy"
          />
        </div>
      </section>

      <section className="gm-band ocean" id="again">
        <div className="gm-wrap gm-closer">
          <div>
            <h2>{copy.finalTitle}</h2>
            <p className="gm-lead">{copy.finalLead}</p>
            <div className="gm-cta-row">
              <a className="gm-submit inline" href="#gate">
                {copy.primaryCta}
              </a>
              <a className="gm-call" href={copy.phoneHref} onClick={onPhone}>
                {copy.phoneDisplay}
              </a>
            </div>
          </div>
        </div>
      </section>

      <footer className="gm-footer">
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
