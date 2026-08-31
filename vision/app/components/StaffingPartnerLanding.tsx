"use client";

import { useEffect, useRef } from "react";
import { DEFAULT_CAREERS_URL } from "../../config/markets";
import {
  STAFFING_PARTNER_VARIANT,
  staffingPartnerCopy,
  staffingPartnerQuotes,
} from "../../config/lp-staffing-partner";
import { clientMarksForMarket } from "../../config/site";
import {
  captureAttribution,
  trackEvent,
  trackPhoneClick,
} from "../../lib/tracking";
import GuidedMatchGate from "./GuidedMatchGate";
import "../guided-match.css";
import "../staffing-partner.css";

type Props = {
  careersHref?: string;
};

export default function StaffingPartnerLanding({
  careersHref = DEFAULT_CAREERS_URL,
}: Props) {
  const copy = staffingPartnerCopy();
  const logos = clientMarksForMarket("us");
  const quotes = staffingPartnerQuotes();
  const featured = quotes[0];
  const rest = quotes.slice(1);
  const variant = STAFFING_PARTNER_VARIANT;

  const gateHeadingRef = useRef<HTMLHeadingElement>(null);
  const quizCardRef = useRef<HTMLDivElement>(null);
  const pulseTimer = useRef<number | undefined>(undefined);

  useEffect(() => {
    captureAttribution("us", {
      variant,
      lp_variant: variant,
    });
    return () => {
      if (pulseTimer.current !== undefined) {
        window.clearTimeout(pulseTimer.current);
      }
    };
  }, [variant]);

  function goToQuiz(
    e: React.MouseEvent<HTMLAnchorElement>,
    trackPrimary = false,
  ) {
    e.preventDefault();
    if (trackPrimary) onPrimaryCta();
    const card = quizCardRef.current;
    const heading = gateHeadingRef.current;
    if (!card) return;

    const reduceMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    const top = window.scrollY + card.getBoundingClientRect().top - 16;
    window.scrollTo({
      top: Math.max(0, top),
      behavior: reduceMotion ? "auto" : "smooth",
    });

    const emphasize = () => {
      heading?.focus({ preventScroll: true });
      card.classList.remove("sp-quiz-arrive");
      void card.offsetWidth;
      card.classList.add("sp-quiz-arrive");
      if (pulseTimer.current !== undefined) {
        window.clearTimeout(pulseTimer.current);
      }
      pulseTimer.current = window.setTimeout(() => {
        card.classList.remove("sp-quiz-arrive");
      }, 1000);
    };

    if (reduceMotion) {
      emphasize();
      return;
    }

    let finished = false;
    const done = () => {
      if (finished) return;
      finished = true;
      window.removeEventListener("scrollend", done);
      emphasize();
    };
    window.addEventListener("scrollend", done, { once: true });
    window.setTimeout(done, 900);
  }

  function onPhone() {
    trackPhoneClick({
      market: "us",
      category: "",
      variant,
      lp_variant: variant,
    });
  }

  function onPrimaryCta() {
    trackEvent("primary_cta_clicked", {
      market: "us",
      category: "",
      variant,
      lp_variant: variant,
      destination: "#gate",
    });
  }

  function onCareers(e: React.MouseEvent<HTMLAnchorElement>) {
    e.preventDefault();
    trackEvent("job_seeker_redirected", {
      market: "us",
      category: "",
      variant,
      lp_variant: variant,
      intent: "job_seeker",
      destination: careersHref,
      primary_eligible: false,
      bidding_primary: false,
      source: "paid_lp_footer",
    });
    window.location.replace(careersHref);
  }

  return (
    <div
      className="gm sp"
      data-challenger={variant}
      data-lp-variant={variant}
      data-market="us"
    >
      <div className="gm-wrap">
        <nav className="gm-nav" aria-label="Employer hiring">
          <img
            src="/brand/logo-vc.png"
            alt="Virtual Coworker"
            width={148}
            height={30}
          />
          <div className="gm-nav-links">
            <a href="#how">How it works</a>
            <a href="#roles">Roles</a>
            <a href="#gate" onClick={(e) => goToQuiz(e)}>
              Hire
            </a>
          </div>
          <a className="gm-call" href={copy.phoneHref} onClick={onPhone}>
            {copy.phoneDisplay}
          </a>
        </nav>
      </div>

      <section className="gm-hero">
        <div className="gm-wrap gm-hero-grid">
          <div>
            <p className="sp-eyebrow">{copy.eyebrow}</p>
            <h1>{copy.h1}</h1>
            <p className="gm-lead">{copy.lead}</p>
            <a
              className="sp-hero-cta"
              href="#gate"
              onClick={(e) => goToQuiz(e, true)}
            >
              {copy.primaryCta}
            </a>
            <p className="sp-proof">{copy.proofStrip.join(" • ")}</p>
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

      <section className="gm-band white" id="how">
        <div className="gm-wrap">
          <p className="sp-eyebrow">{copy.howEyebrow}</p>
          <h2>{copy.howTitle}</h2>
          <p className="gm-lead">{copy.howLead}</p>
          <div className="sp-steps">
            {copy.steps.map((step) => (
              <article className="sp-step" key={step.k}>
                <b>
                  <span className="sp-k">{step.k}</span>
                  {step.t}
                </b>
                <p>{step.d}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band mist" id="roles">
        <div className="gm-wrap">
          <p className="sp-eyebrow">{copy.rolesEyebrow}</p>
          <h2>{copy.rolesTitle}</h2>
          <p className="gm-lead">{copy.rolesLead}</p>
          <div className="sp-roles">
            {copy.roles.map((role) => (
              <article className="sp-role" key={role.title}>
                <h3>{role.title}</h3>
                <p>{role.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band sand" id="why">
        <div className="gm-wrap">
          <p className="sp-eyebrow">{copy.contrastEyebrow}</p>
          <h2>{copy.contrastTitle}</h2>
          <p className="gm-lead">{copy.contrastLead}</p>
          <div className="sp-contrast">
            {copy.contrasts.map((row) => (
              <article
                className={`sp-card${row.highlight ? " on" : ""}`}
                key={row.option}
              >
                <h3>{row.option}</h3>
                <p>{row.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band white" id="proof">
        <div className="gm-wrap">
          <p className="sp-eyebrow">{copy.proofEyebrow}</p>
          <h2>{copy.proofTitle}</h2>
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
          <div className="sp-proofs">
            {copy.proofs.map((item) => (
              <article className="sp-card" key={item.title}>
                <h3>{item.title}</h3>
                <p>{item.body}</p>
              </article>
            ))}
          </div>
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

      <section className="gm-logos" aria-label="Companies we have staffed">
        <div className="gm-wrap">
          <div className="gm-logo-row">
            {logos.map((m) => (
              <img key={m.id} src={m.src} alt={m.alt || m.name} height={44} />
            ))}
          </div>
          <p className="gm-proof-meta">
            Serving employers since {copy.sinceYear}
          </p>
        </div>
      </section>

      <section className="gm-qualify" id="gate">
        <div className="gm-wrap">
          <div className="sp-quiz-card" ref={quizCardRef}>
            <h2 id="sp-quiz-heading" tabIndex={-1} ref={gateHeadingRef}>
              {copy.gateTitle}
            </h2>
            <p className="gm-lead">{copy.gateLead}</p>
            <GuidedMatchGate
              market="us"
              variant={variant}
              lpVariant={variant}
              careersHref={careersHref}
              includeGateId={false}
              explicitContinue
              sequentialNeeds
              hoursQuestionSplit
              progressLabel="step"
              submitLabel="Send My Staffing Request"
              spQuiz
            />
          </div>
        </div>
      </section>

      <section className="gm-band ocean" id="again">
        <div className="gm-wrap gm-closer">
          <div>
            <h2>{copy.finalTitle}</h2>
            <p className="gm-lead">{copy.finalLead}</p>
            <a className="sp-hero-cta" href={copy.phoneHref} onClick={onPhone}>
              {copy.finalPhoneCta}
            </a>
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
          Philippines recruitment hub · Serving employers since {copy.sinceYear}{" "}
          · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a>
          <br />
          <a href={careersHref} onClick={onCareers}>
            {copy.seekerLine}
          </a>
        </div>
      </footer>
    </div>
  );
}
