"use client";

import type { MarketId } from "../../config/markets";
import {
  CHALLENGER_VARIANT,
  type ChallengerConcept,
  capacityQuotes,
  challengerCopy,
} from "../../config/lp-challenger-capacity";
import { GUIDED_MATCH_ROLES, JOB_SEEKER_LINE } from "../../config/guided-match";
import { clientMarksForMarket } from "../../config/site";
import { DEFAULT_CAREERS_URL } from "../../config/markets";
import { trackPhoneClick, trackEvent } from "../../lib/tracking";
import GuidedMatchGate from "./GuidedMatchGate";
import "../guided-match.css";
import "../capacity-challenger.css";

type Props = {
  market: MarketId;
  careersHref?: string;
  concept?: ChallengerConcept;
};

export default function CapacityChallengerLanding({
  market,
  careersHref = DEFAULT_CAREERS_URL,
  concept = "capacity",
}: Props) {
  const copy = challengerCopy(concept, market);
  const logos = clientMarksForMarket(market);
  const quotes = capacityQuotes();
  const featured = quotes[copy.featuredQuoteIndex] || quotes[0];
  const rest = quotes.filter((_, i) => i !== copy.featuredQuoteIndex);
  const variant = CHALLENGER_VARIANT[concept];

  function onPhone() {
    trackPhoneClick({
      market,
      category: "",
      variant,
    });
  }

  function onCareers(e: React.MouseEvent<HTMLAnchorElement>) {
    e.preventDefault();
    trackEvent("job_seeker_redirected", {
      market,
      category: "",
      variant,
      intent: "job_seeker",
      destination: careersHref,
      primary_eligible: false,
      bidding_primary: false,
      source: "paid_lp_footer",
    });
    window.location.replace(careersHref);
  }

  function selectBandRole(chip: string) {
    const match = Array.from(
      document.querySelectorAll<HTMLButtonElement>(".gm-gate .gm-chip"),
    ).find((el) => el.textContent?.includes(chip));
    if (match) match.click();
    window.setTimeout(() => {
      document.getElementById("gate")?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }, 80);
  }

  return (
    <div className="gm cc" data-challenger={variant} data-market={market}>
      {copy.previewNote ? (
        <p className="cc-preview-note">{copy.previewNote}</p>
      ) : null}
      <div className="gm-wrap">
        <nav className="gm-nav" aria-label="Employer hiring">
          <img src="/brand/logo-vc.png" alt="Virtual Coworker" width={148} height={30} />
          <div className="gm-nav-links">
            <a href="#situation">If this is you</a>
            <a href="#why">Why us</a>
            <a href="#how">How it works</a>
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
            <p className="cc-eyebrow">{copy.eyebrow}</p>
            <h1>{copy.h1}</h1>
            <p className="gm-lead">{copy.lead}</p>
            <ul className="cc-proof-strip">
              {copy.proofStrip.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
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
            <p className="cc-form-intro">{copy.formIntro}</p>
            <GuidedMatchGate
              market={market}
              variant={variant}
              careersHref={careersHref}
            />
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
            Serving employers since {copy.sinceYear} · 450K+ LinkedIn
          </p>
        </div>
      </section>

      <section className="gm-band mist" id="situation">
        <div className="gm-wrap">
          <p className="cc-eyebrow">{copy.situationsEyebrow}</p>
          <h2>{copy.situationsTitle}</h2>
          <div className="cc-card-grid">
            {copy.situations.map((item) => (
              <article className="cc-card" key={item.title}>
                <h3>{item.title}</h3>
                <p>{item.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band white" id="outcomes">
        <div className="gm-wrap">
          <p className="cc-eyebrow">{copy.outcomesEyebrow}</p>
          <h2>{copy.outcomesTitle}</h2>
          <div className="cc-card-grid">
            {copy.outcomes.map((item) => (
              <article className="cc-card" key={item.title}>
                <h3>{item.title}</h3>
                <p>{item.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band sand" id="why">
        <div className="gm-wrap">
          <p className="cc-eyebrow">{copy.compareEyebrow}</p>
          <h2>{copy.compareTitle}</h2>
          <p className="gm-lead">{copy.compareLead}</p>
          <div className="cc-compare">
            {copy.compareRows.map((row) => (
              <article
                key={row.option}
                className={`cc-compare-card${row.highlight ? " on" : ""}`}
              >
                <h3>{row.option}</h3>
                <dl>
                  <div>
                    <dt>Screening and matching</dt>
                    <dd>{row.screening}</dd>
                  </div>
                  <div>
                    <dt>You choose</dt>
                    <dd>{row.chooses}</dd>
                  </div>
                  <div>
                    <dt>Employment</dt>
                    <dd>{row.employment}</dd>
                  </div>
                  <div>
                    <dt>Ongoing support</dt>
                    <dd>{row.support}</dd>
                  </div>
                  <div>
                    <dt>Dedicated teammate</dt>
                    <dd>{row.dedicated}</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band white" id="proof">
        <div className="gm-wrap gm-split">
          <div>
            <p className="cc-eyebrow">{copy.proofEyebrow}</p>
            <h2>{copy.proofTitle}</h2>
            <div className="gm-why-grid">
              {copy.proofs.map((item) => (
                <div key={item.title}>
                  <h3>{item.title}</h3>
                  <p>{item.body}</p>
                </div>
              ))}
            </div>
          </div>
          <img
            className="gm-scene"
            src={copy.sceneSrc}
            alt={copy.sceneAlt}
            width={1200}
            height={800}
            loading="lazy"
          />
        </div>
      </section>

      <section className="gm-band mist" id="stories">
        <div className="gm-wrap">
          <h2>What employers say</h2>
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

      <section className="gm-band white" id="how">
        <div className="gm-wrap">
          <p className="cc-eyebrow">{copy.processEyebrow}</p>
          <h2>{copy.processTitle}</h2>
          <p className="gm-lead">{copy.processLead}</p>
          <div className="gm-grid-steps cc-steps">
            {copy.steps.map((step) => (
              <div className="gm-step" key={step.k}>
                <b>
                  {step.k}. {step.t}
                </b>
                <p>{step.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band sand" id="roles">
        <div className="gm-wrap">
          <h2>Roles we hire for</h2>
          <p className="gm-lead">Dedicated staff, not a rotating freelance pool.</p>
          <div className="gm-role-grid">
            {GUIDED_MATCH_ROLES.map((r) => (
              <button
                key={r.id}
                type="button"
                className="gm-role-card"
                onClick={() => selectBandRole(r.chip)}
              >
                <b>{r.chip}</b>
                <span>{r.blurb}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band white" id="people">
        <div className="gm-wrap">
          <h2>The team that recruits your hire</h2>
          <p className="gm-lead">
            Philippines recruitment floor. US and Australian offices behind the
            account.
          </p>
          <img
            className="gm-wide"
            src={copy.teamSrc}
            alt={copy.teamAlt}
            width={1600}
            height={900}
            loading="lazy"
          />
        </div>
      </section>

      <section className="gm-band mist" id="faq">
        <div className="gm-wrap" style={{ maxWidth: "44rem" }}>
          <h2>Questions employers ask</h2>
          {copy.faqs.map((item) => (
            <details key={item.q}>
              <summary>{item.q}</summary>
              <p>{item.a}</p>
            </details>
          ))}
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
                {copy.secondaryCta} {copy.phoneDisplay}
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
