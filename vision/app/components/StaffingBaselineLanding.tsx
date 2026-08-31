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
import {
  LANDING_PAGE_TYPES,
  STAFFING_AGENCY_CANDIDATE_LP_VERSION,
  US_BASELINE_LABEL,
} from "../../config/lp-version";
import { staffingAgencyCopy } from "../../config/lp-staffing-agency";
import {
  REAL_ESTATE_SLUG,
  buildRealEstateRoute,
  isRealEstateSlug,
} from "../../config/lp-real-estate";
import { clientMarksForMarket } from "../../config/site";
import {
  captureAttribution,
  trackEvent,
  trackPhoneClick,
} from "../../lib/tracking";
import { trackExperimentConvert } from "../../lib/experiments";
import { trackLpView } from "../../lib/lp-events";
import { exitToCareers } from "../../lib/job-seeker-exit";
import { bookPathForMarket, withCurrentSearch } from "../../lib/preserve-query";
import GuidedMatchGate from "./GuidedMatchGate";
import UsBaselineHero from "./UsBaselineHero";
import "../guided-match.css";
import "../staffing-partner.css";

type Props = {
  market: MarketId;
  category?: CategorySlug | typeof REAL_ESTATE_SLUG | null;
  careersHref?: string;
  /** Unused candidate only. Live /us stays "baseline". */
  profile?: "baseline" | "staffing_agency";
};

export default function StaffingBaselineLanding({
  market,
  category = null,
  careersHref = DEFAULT_CAREERS_URL,
  profile = "baseline",
}: Props) {
  const isRealEstate = isRealEstateSlug(category);
  const isStaffingAgency = profile === "staffing_agency" && market === "us";
  const baseCfg = isRealEstate
    ? buildRealEstateRoute(market)
    : buildBaselineRoute({ market, role: category });
  const agency = isStaffingAgency ? staffingAgencyCopy() : null;
  const lpVersion = isStaffingAgency
    ? STAFFING_AGENCY_CANDIDATE_LP_VERSION
    : BASELINE_LP_VERSION;
  const landingPageType = isStaffingAgency
    ? LANDING_PAGE_TYPES.staffing_agency_candidate
    : LANDING_PAGE_TYPES.employer_paid_lp;
  const cfg = agency
    ? {
        ...baseCfg,
        eyebrow: agency.eyebrow,
        h1: agency.h1,
        supporting_copy: agency.supporting_copy,
      }
    : baseCfg;
  const copy = {
    ...baselineSharedCopy(market),
    ...(agency
      ? {
          howTitle: agency.howTitle,
          howLead: agency.howLead,
          howEyebrow: agency.howEyebrow,
          whyItems: agency.whyItems,
          gateLead: agency.gateLead,
        }
      : {}),
  };
  const logos = clientMarksForMarket(market);
  const { featured, rest } = baselineQuotes(isRealEstate ? null : category);
  const extras = {
    ...baselineTrackingExtras(cfg),
    lp_version: lpVersion,
    ...(isRealEstate
      ? {
          lp_role: REAL_ESTATE_SLUG,
          lp_intent_cluster: REAL_ESTATE_SLUG,
          lp_route: cfg.route,
        }
      : {}),
  };
  const variant = BASELINE_LP_VARIANT;

  const gateHeadingRef = useRef<HTMLHeadingElement>(null);
  const quizCardRef = useRef<HTMLDivElement>(null);
  const pulseTimer = useRef<number | undefined>(undefined);

  useEffect(() => {
    captureAttribution(market, {
      category: category || "",
      variant,
      lp_variant: variant,
      lp_version: lpVersion,
      baseline_label: US_BASELINE_LABEL,
    });
    trackLpView({
      market,
      lp_version: lpVersion,
      baseline_label: US_BASELINE_LABEL,
      landing_page_type: landingPageType,
    });
    return () => {
      if (pulseTimer.current !== undefined) {
        window.clearTimeout(pulseTimer.current);
      }
    };
  }, [market, category, variant, lpVersion, landingPageType]);

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

  function onPhone(location: "header" | "hero" | "closer") {
    trackPhoneClick({
      market,
      category: category || "",
      variant,
      cta_location: location,
      ...extras,
    });
    trackExperimentConvert("phone_click", {
      market,
      surface: "staffing_baseline",
      cta_location: location,
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
    exitToCareers(careersHref, {
      market,
      lp_version: lpVersion,
      landing_page_type: landingPageType,
      redirect_location: "footer_careers_link",
      redirect_reason: "careers_escape",
    });
  }

  return (
    <div
      className="gm sp"
      data-lp-version={lpVersion}
      data-lp-variant={variant}
      data-market={market}
      data-baseline="v1-2026-08"
      data-baseline-label={US_BASELINE_LABEL}
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
          <a className="gm-call" href={cfg.phone_href} onClick={() => onPhone("header")}>
            {cfg.phone_display}
          </a>
        </nav>
      </div>

      <section className="gm-hero">
        <div className="gm-wrap gm-hero-grid">
          <div>
            <p className="sp-eyebrow">{cfg.eyebrow}</p>
            <h1>{cfg.h1}</h1>
            <p className="gm-lead">{cfg.supporting_copy}</p>
            <div className="sp-hero-cta-row">
              <a
                className="sp-hero-cta"
                href="#gate"
                onClick={(e) => goToQuiz(e, true)}
              >
                {copy.primaryCta}
              </a>
              <a
                className="sp-hero-cta-secondary"
                href={bookPathForMarket(market)}
                data-track="calendly_cta_clicked"
                data-market={market}
                onClick={(e) => {
                  const next = withCurrentSearch(bookPathForMarket(market));
                  trackEvent("calendly_cta_clicked", {
                    market,
                    href: next,
                    source: "hero_skip_form",
                    bidding_primary: false,
                  });
                  if (next === bookPathForMarket(market)) return;
                  e.preventDefault();
                  window.location.assign(next);
                }}
              >
                Book a call - skip the form
              </a>
            </div>
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
          {market === "us" && !category && !isRealEstate && !isStaffingAgency ? (
            <UsBaselineHero className="gm-hero-photo" />
          ) : (
            <img
              className="gm-hero-photo"
              src={cfg.hero_image}
              alt={cfg.hero_alt}
              width={960}
              height={1280}
              fetchPriority="high"
              decoding="async"
            />
          )}
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
            {isRealEstate
              ? "What this real-estate seat covers"
              : category
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
            <p className="gm-lead" style={{ marginTop: "-0.35rem" }}>
              Prefer not to fill a form?{" "}
              <a
                href={bookPathForMarket(market)}
                data-track="calendly_cta_clicked"
                data-market={market}
                onClick={(e) => {
                  const next = withCurrentSearch(bookPathForMarket(market));
                  trackEvent("calendly_cta_clicked", {
                    market,
                    href: next,
                    source: "gate_skip_form",
                    bidding_primary: false,
                  });
                  if (next === bookPathForMarket(market)) return;
                  e.preventDefault();
                  window.location.assign(next);
                }}
              >
                Book a consultation instead
              </a>
              .
            </p>
            <GuidedMatchGate
              market={market}
              category={category}
              variant={variant}
              lpVariant={variant}
              lpVersion={lpVersion}
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
              onClick={() => onPhone("closer")}
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
