"use client";

/**
 * Paid Landing Page Baseline v1 — August 2026
 * Shared production template for /us, /au, and role pages.
 * Hybrid: approved price-led hero + quiz; live image bands + section rhythm.
 * Job-seeker exit stays visible (footer + gate) — no hard employer gate.
 */

import { useEffect, useRef } from "react";
import type { CategorySlug } from "../../config/categories";
import type { MarketId } from "../../config/markets";
import { DEFAULT_CAREERS_URL } from "../../config/markets";
import {
  BASELINE_LP_VARIANT,
  BASELINE_LP_VERSION,
  baselineQuotes,
  baselineSharedCopy,
  baselineTrackingExtras,
  buildBaselineRoute,
} from "../../config/lp-baseline";
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
  market: MarketId;
  category?: CategorySlug | null;
  careersHref?: string;
};

export default function StaffingBaselineLanding({
  market,
  category = null,
  careersHref = DEFAULT_CAREERS_URL,
}: Props) {
  const cfg = buildBaselineRoute({ market, role: category });
  const copy = baselineSharedCopy(market);
  const logos = clientMarksForMarket(market);
  const { featured, rest } = baselineQuotes(category);
  const extras = baselineTrackingExtras(cfg);
  const variant = BASELINE_LP_VARIANT;

  const gateHeadingRef = useRef<HTMLHeadingElement>(null);
  const quizCardRef = useRef<HTMLDivElement>(null);
  const pulseTimer = useRef<number | undefined>(undefined);

  useEffect(() => {
    captureAttribution(market, {
      category: category || "",
      variant,
      lp_variant: variant,
      lp_version: BASELINE_LP_VERSION,
    });
    return () => {
      if (pulseTimer.current !== undefined) {
        window.clearTimeout(pulseTimer.current);
      }
    };
  }, [market, category, variant]);

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
      market,
      category: category || "",
      variant,
      ...extras,
    });
  }

  function onPrimaryCta() {
    trackEvent("primary_cta_clicked", {
      market,
      category: category || "",
      variant,
      destination: "#gate",
      ...extras,
    });
  }

  function onCareers(e: React.MouseEvent<HTMLAnchorElement>) {
    e.preventDefault();
    trackEvent("job_seeker_redirected", {
      market,
      category: category || "",
      variant,
      intent: "job_seeker",
      destination: careersHref,
      primary_eligible: false,
      bidding_primary: false,
      source: "paid_lp_footer",
      ...extras,
    });
    window.location.replace(careersHref);
  }

  return (
    <div
      className="gm sp"
      data-lp-version={BASELINE_LP_VERSION}
      data-lp-variant={variant}
      data-market={market}
      data-baseline="v1-2026-08"
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
            <a href="#stories">Stories</a>
            <a href="#gate" onClick={(e) => goToQuiz(e)}>
              Hire
            </a>
          </div>
          <a className="gm-call" href={cfg.phone_href} onClick={onPhone}>
            <span className="sp-phone-long">{cfg.phone_display}</span>
            <span className="sp-phone-short">{cfg.phone_short}</span>
          </a>
        </nav>
      </div>

      <section className="gm-hero">
        <div className="gm-wrap gm-hero-grid">
          <div>
            <p className="sp-eyebrow">{cfg.eyebrow}</p>
            <h1>{cfg.h1}</h1>
            <p className="gm-lead">{cfg.supporting_copy}</p>
            <a
              className="sp-hero-cta"
              href="#gate"
              onClick={(e) => goToQuiz(e, true)}
            >
              {copy.primaryCta}
            </a>
            <p className="gm-starline sp-hero-stars">
              <span className="gm-stars" aria-hidden="true">
                ★★★★★
              </span>{" "}
              {copy.googleLine} ·{" "}
              <span className="gm-stars" aria-hidden="true">
                ★★★★★
              </span>{" "}
              {copy.clutchLine}
            </p>
            <p className="sp-proof">{cfg.proof_items.join(" • ")}</p>
          </div>
          <img
            className="gm-hero-photo"
            src={cfg.hero_image}
            alt={cfg.hero_alt}
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
              <img key={m.id} src={m.src} alt={m.alt || m.name} height={44} />
            ))}
          </div>
          <p className="gm-proof-meta">
            Serving employers since {copy.sinceYear} · {copy.linkedin} LinkedIn
          </p>
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
          <h2>
            {category
              ? `What this ${cfg.form_role.toLowerCase() || "role"} seat covers`
              : copy.rolesTitle}
          </h2>
          <p className="gm-lead">{copy.rolesLead}</p>
          <div className="sp-roles">
            {cfg.role_tasks.map((role) => (
              <article className="sp-role" key={role.title}>
                <h3>{role.title}</h3>
                <p>{role.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band sand" id="why">
        <div className="gm-wrap gm-split">
          <div>
            <p className="sp-eyebrow">{copy.whyEyebrow}</p>
            <h2>{copy.whyTitle}</h2>
            <div className="gm-why-grid">
              {copy.whyItems.map((item) => (
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

      <section className="gm-band white" id="people">
        <div className="gm-wrap">
          <h2>{copy.teamTitle}</h2>
          <p className="gm-lead">{copy.teamLead}</p>
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

      <section className="gm-band mist" id="stories">
        <div className="gm-wrap">
          <h2>{copy.storiesTitle}</h2>
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

      <section className="gm-qualify" id="gate">
        <div className="gm-wrap">
          <div className="sp-quiz-card" ref={quizCardRef}>
            <h2 id="sp-quiz-heading" tabIndex={-1} ref={gateHeadingRef}>
              {copy.gateTitle}
            </h2>
            <p className="gm-lead">{copy.gateLead}</p>
            <GuidedMatchGate
              market={market}
              category={category}
              variant={variant}
              lpVariant={variant}
              lpVersion={BASELINE_LP_VERSION}
              careersHref={careersHref}
              includeGateId={false}
              explicitContinue
              sequentialNeeds
              hoursQuestionSplit
              progressLabel="step"
              submitLabel="Send My Staffing Request"
              spQuiz
              allowRoleChange={Boolean(category)}
            />
          </div>
        </div>
      </section>

      <section className="gm-band ocean" id="again">
        <div className="gm-wrap gm-closer">
          <div>
            <h2>{copy.finalTitle}</h2>
            <p className="gm-lead">{copy.finalLead}</p>
            <a
              className="sp-hero-cta"
              href={cfg.phone_href}
              onClick={onPhone}
            >
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
