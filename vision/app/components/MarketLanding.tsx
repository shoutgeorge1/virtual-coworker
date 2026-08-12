import Link from "next/link";
import LeadGate, { type GateCopy } from "./LeadGate";
import StickyCta from "./StickyCta";
import EngageChat from "./EngageChat";
import RoleQuiz from "./RoleQuiz";
import QuizConversionSlot from "./QuizConversionSlot";
import LpDensity from "./LpDensity";
import SiteNav from "./SiteNav";
import SiteFooter from "./SiteFooter";
import TrustBand from "./TrustBand";
import PressBand from "./PressBand";
import PainGain from "./PainGain";
import RoleOutcomes from "./RoleOutcomes";
import FaqAccordion from "./FaqAccordion";
import StopCloser from "./StopCloser";
import { RoleHeroCard } from "./RoleImagery";
import JsonLd from "./JsonLd";
import {
  MARKETS,
  resolveCareersUrl,
  resolvePhone,
  type MarketId,
} from "../../config/markets";
import { hiringProcessStrip } from "../../config/hiring-process";
import {
  CATEGORIES,
  type AbVariant,
  type CategorySlug,
} from "../../config/categories";
import {
  primaryHireCta,
  employerFaq,
  roleHeroBenefits,
} from "../../config/employer-cro";
import {
  FORM_CUE,
  SITE,
  TRUST_PROOF,
  googleBusinessForMarket,
  industryStatsForMarket,
  yearsTrading,
} from "../../config/site";
import GoogleReviewBadge, { RatingStars } from "./GoogleReviewBadge";
import { StatsGrid } from "./TrustAnimated";
import {
  breadcrumbJsonLd,
  faqPageJsonLd,
  organizationJsonLd,
  professionalServiceJsonLd,
  websiteJsonLd,
} from "../../lib/seo";

export default function MarketLanding({
  market,
  category,
  variant,
  conversionSurface = "form",
}: {
  market: MarketId;
  category?: CategorySlug | null;
  variant: AbVariant;
  /** form = LeadGate in hero (default LP). quiz = RoleQuiz in hero (quiz LP). */
  conversionSurface?: "form" | "quiz";
}) {
  const cfg = MARKETS[market];
  const phone = resolvePhone(market);
  const careers = resolveCareersUrl();
  const cat = category ? CATEGORIES[category] : null;
  const v = cat ? cat.variants[variant] : null;
  const isAu = market === "au";
  const isQuiz = conversionSurface === "quiz";
  const years = yearsTrading();
  const gbp = googleBusinessForMarket(market);

  const quizHero = isAu
    ? {
        h1: "Find the right virtual assistant for your business",
        sub: "Take the employer hiring quiz. We’ll name the role that takes the load - then you can book a free consultation.",
      }
    : {
        h1: "Find the right virtual assistant for your business",
        sub: "Take the employer hiring quiz. A few taps - we’ll name the seat that buys back your week.",
      };

  const h1 = isQuiz && !cat ? quizHero.h1 : v ? v.h1[market] : cfg.headline;
  const sub = isQuiz && !cat ? quizHero.sub : v ? v.subhead[market] : cfg.prop;
  const primaryCta = primaryHireCta(market);
  const heroSrc = v
    ? v.heroImage[market]
    : market === "us"
      ? "/brand/va-us.jpg"
      : "/brand/va-au.jpg";
  const heroAlt = v?.heroAlt || "Virtual Coworker team member at a desk";

  const benefits = category
    ? roleHeroBenefits(category, market)
    : isAu
      ? [
          "Dedicated full-time or part-time professionals from the Philippines",
          "They work Australian hours - your time zone, not theirs",
          "Recruiting, vetting, employment admin, and ongoing support handled for you",
          "Serving businesses since 2011 - not a gig marketplace",
        ]
      : [
          "Dedicated full-time or part-time professionals from the Philippines",
          "They work your time zone - not a night shift",
          "Recruiting, vetting, payroll, and ongoing support handled for you",
          "Serving businesses since 2011 - not a gig marketplace",
        ];

  const faq = employerFaq(market, cat?.label || null, category);
  const processSteps = hiringProcessStrip(market);

  const showPhone = phone.configured && Boolean(phone.href);
  const shell = market === "us" ? "us" : "au";
  const light = market === "au";

  const formCue = isQuiz
    ? isAu
      ? { label: "Take the quiz", body: "A few taps - then book a free consultation." }
      : { label: "Take the quiz", body: "A few taps - then book a free consultation." }
    : FORM_CUE[market];
  const industryStats = industryStatsForMarket(market);

  const gate: GateCopy = {
    eyebrow: isAu ? "Businesses only · 2 minutes" : "Employers only · 2 minutes",
    title: cat
      ? isAu
        ? `Chat about ${cat.label}`
        : `Hire ${cat.label}`
      : isAu
        ? "Book a free consultation - obligation free, at no cost."
        : "Book your free consultation.",
    intentLabel: "First - who are you?",
    intentPrimary: "I’m hiring for a business.",
    intentSecondary: "I’m looking for a job.",
    divertTitle: "Looking for work?",
    divertBody:
      "This page is for businesses hiring staff. Job applications open on our Philippines careers site - not this form.",
    divertCta: "Go to Philippines careers →",
    careersHref: careers,
    roleLabel: "What do you need help with?",
    roles: cfg.servicesProposed,
    detailsLabel: "Your business details",
    nameLabel: "Full name",
    namePlaceholder: "Full name",
    emailLabel: "Work email",
    emailPlaceholder: "Work email",
    phoneLabel: "Business phone",
    phonePlaceholder: isAu ? "0400 000 000" : "(201) 555-0123",
    companyLabel: "Company",
    companyPlaceholder: "Company name",
    submit: primaryCta,
    reassure: isAu
      ? "Obligation free, at no cost. No lock-in. Businesses only. A member of our team will follow up for a short chat - this is not an instant hire. We don’t sell your information. Privacy notice applies."
      : "Obligation free, at no cost. Employers only. A member of our team follows up - usually within one business day. We don’t sell your information. Privacy notice applies.",
    callLabel: showPhone
      ? isAu
        ? "Prefer to give us a call?"
        : "Prefer to call?"
      : "",
    phoneDisplay: phone.display,
    phoneHref: phone.href,
    showPhone,
    doneTitle: "Got it - thanks.",
    doneBody: isAu
      ? "A member of our team will follow up for a short chat about the role and next steps."
      : "A member of our team will call you to talk through the role and next steps.",
  };

  const breadcrumbs = cat
    ? [
        { name: "Home", path: cfg.landingPath },
        { name: "Roles", path: `/services?market=${market}` },
        { name: cat.label, path: `${cfg.landingPath}/${cat.slug}` },
      ]
    : isQuiz
      ? [
          { name: "Home", path: cfg.landingPath },
          { name: "Quiz", path: `${cfg.landingPath}/quiz` },
        ]
      : [
          { name: "Home", path: cfg.landingPath },
          { name: "How it works", path: `/how-it-works?market=${market}` },
        ];

  return (
    <main
      className={`${shell}${isQuiz ? " quiz-lp" : ""}`}
      data-variant={variant}
      data-category={category || "generic"}
      data-cta-mode={isQuiz ? "quiz_lp" : "form_primary"}
      data-lp-surface={conversionSurface}
    >
      <JsonLd
        data={[
          organizationJsonLd(),
          websiteJsonLd(),
          professionalServiceJsonLd(market),
          breadcrumbJsonLd(breadcrumbs),
          faqPageJsonLd(faq),
        ]}
      />
      <LpDensity market={market} />
      <SiteNav tone={light ? "light" : "dark"} market={market} />

      <section className={`${shell}-hero`}>
        <div className={market === "us" ? "us-hero-bg" : "au-hero-veil"} aria-hidden />

        <div className={`${shell}-hero-inner`}>
          <div className={`${shell}-hero-copy`}>
            <p className={`${shell}-kicker anim-rise`}>
              {cfg.label} · {isAu ? "Businesses" : "Employers"}
              {cat ? ` · ${cat.label}` : ""}
              {isQuiz ? " · Employer hiring quiz" : ""}
              {" · "}Philippines staffing
            </p>
            <h1 className="anim-rise">{h1}</h1>
            <p className={`${shell}-lead anim-rise-d1`}>{sub}</p>
          </div>

          <RoleHeroCard
            category={category}
            market={market}
            fallbackSrc={heroSrc}
            fallbackAlt={heroAlt}
            shell={shell}
            shortLabel={cat ? cat.shortLabel : "Dedicated hire"}
            captionTitle={cat ? cat.label : "Matched to your role"}
            captionSub={
              isAu
                ? "Australian business hours · Filipino talent"
                : "US business hours · Filipino talent"
            }
          />

          <div className={`${shell}-hero-more`}>
            <ul className={`${shell}-ticks anim-rise-d1`}>
              {benefits.map((b) => (
                <li key={b}>{b}</li>
              ))}
            </ul>

            <p
              className={`${shell}-lead anim-rise-d2`}
              style={{ marginTop: "0.75rem" }}
              data-lp="secondary"
            >
              {cfg.staffingExplain}
            </p>

            <div
              className={`trust-row anim-rise-d2${light ? " trust-row-light" : ""}`}
            >
              <GoogleReviewBadge proof={gbp} />
              <span
                className="trust-chip"
                aria-label={`Clutch ${TRUST_PROOF.clutch.rating} out of 5 from ${TRUST_PROOF.clutch.reviewCount} reviews`}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={market === "us" ? "/brand/clutch-us.webp" : "/brand/badge-clutch-au.webp"}
                  alt=""
                />
                <span>
                  <b className="trust-chip-rating-line">
                    <RatingStars size={13} />
                    {TRUST_PROOF.clutch.rating}
                  </b>
                  <span>
                    Clutch · {TRUST_PROOF.clutch.reviewCount} reviews
                  </span>
                </span>
              </span>
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={
                    light
                      ? "/brand/badge-forbes-navy.webp"
                      : "/brand/badge-forbes-white.webp"
                  }
                  alt="Forbes Business Council"
                />
                <span>
                  <b>Forbes</b>
                  <span>Business Council</span>
                </span>
              </span>
              <span className="trust-chip trust-chip-stat">
                <em>{years}+</em>
                <span>
                  <b>Years</b>
                  <span>placing Filipino staff</span>
                </span>
              </span>
              <span className="trust-chip trust-chip-stat">
                <em>PH</em>
                <span>
                  <b>Filipino</b>
                  <span>Dedicated hires</span>
                </span>
              </span>
            </div>

            <p className={`${shell}-rate-note anim-rise-d2`}>
              Rates discussed once we understand the role - not buried in fine print.
            </p>
          </div>

          <div className="gate-wrap">
            <p className="form-cue" aria-hidden="true">
              <span className="form-cue-arrow">↓</span>
              <span className="form-cue-copy">
                <b>{formCue.label}</b>
                <span>{formCue.body}</span>
              </span>
            </p>
            {isQuiz ? (
              <QuizConversionSlot
                market={market}
                category={category || undefined}
                variant={variant}
                light={light}
                phoneDisplay={showPhone ? phone.display : undefined}
                phoneHref={showPhone ? phone.href : null}
                careersHref={careers}
                gate={gate}
              />
            ) : (
              <LeadGate
                copy={gate}
                market={market}
                category={category}
                variant={variant}
                preselectedRole={cat ? cat.formLabel : null}
                lpSurface="form"
                ctaMode="form_primary"
              />
            )}
            <ul className="gate-nudges">
              <li>Obligation free</li>
              <li>{isQuiz ? "A few taps" : "2-minute brief"}</li>
              <li>Specialist follows up</li>
              <li>We don’t sell your info</li>
            </ul>
          </div>
        </div>
      </section>

      <PressBand light={light} market={market} />

      {industryStats.length > 0 ? (
        <section
          className={`industry-band${light ? " industry-band-light" : ""}`}
          aria-labelledby="industry-stats-title"
        >
          <div className="industry-band-inner">
            <p className={market === "us" ? "us-proof-label" : "au-proof-label"}>
              Why businesses hire offshore
            </p>
            <h2 id="industry-stats-title">
              The #1 reason isn’t cheaper. It’s better people.
            </h2>
            <p className="industry-band-lead">
              Published research - not our marketing.
            </p>
            <StatsGrid stats={industryStats} />
          </div>
        </section>
      ) : null}

      <PainGain market={market} light={light} />

      {category ? (
        <RoleOutcomes category={category} market={market} light={light} />
      ) : null}

      <section className={`${shell}-sell`}>
        <div className={`${shell}-sell-inner`}>
          <div className={`${shell}-sell-head`}>
            <p className={market === "us" ? "us-proof-label" : "au-proof-label"}>
              How hiring works
            </p>
            <h2>White-glove hiring. Not a freelancer marketplace.</h2>
            <p className={`${shell}-sell-sub`} data-lp="secondary">
              {isAu
                ? "Free consultation. Job description. We recruit and vet. You get profiles with hourly rates, then you interview. We handle employment admin and stay on after they start. "
                : "Free consultation. Job description. We recruit and vet. You get profiles with hourly rates, then you interview. We handle payroll, HR, and time tracking. "}
              <Link href={`/how-it-works?market=${market}`}>
                See the full process →
              </Link>
              {" · "}
              <Link href={`/services?market=${market}`}>Browse roles →</Link>
            </p>
          </div>
          <div className={`sell-grid sell-grid-4${light ? " sell-grid-light" : ""}`}>
            {processSteps.map((b) => (
              <div className="sell-card" key={b.k}>
                <em>{b.k}</em>
                <strong>{b.t}</strong>
                <p>{b.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <TrustBand light={light} market={market} />

      {!isQuiz ? (
        <RoleQuiz
          market={market}
          category={category || undefined}
          variant={variant}
          light={light}
          phoneDisplay={showPhone ? phone.display : undefined}
          phoneHref={showPhone ? phone.href : null}
        />
      ) : null}

      {faq.length > 0 ? (
        <section className={`${shell}-sell faq-section`}>
          <div className={`${shell}-sell-inner`}>
            <div className={`${shell}-sell-head`}>
              <p
                className={
                  market === "us" ? "us-proof-label" : "au-proof-label"
                }
              >
                Quick answers
              </p>
              <h2>Tap a question.</h2>
            </div>
            <FaqAccordion items={faq} light={light} />
          </div>
        </section>
      ) : null}

      <StopCloser
        market={market}
        light={light}
        showPhone={showPhone}
        phoneDisplay={phone.display}
        phoneHref={phone.href}
        surface={category || "home"}
        ctaHref={isQuiz ? "#role-quiz" : "#gate"}
      />

      <SiteFooter
        tone={light ? "light" : "dark"}
        market={market}
        categoryLabel={cat?.label}
      />

      <p className="sr-only">
        {SITE.copyright} Offices: {SITE.addressUs}; {SITE.addressAu}.
      </p>

      <StickyCta
        href={isQuiz ? "#role-quiz" : "#gate"}
        label={isQuiz ? "Take the quiz" : primaryCta}
        market={market}
        phoneDisplay={showPhone ? phone.display : undefined}
        phoneHref={showPhone ? phone.href : null}
        category={category || undefined}
        variant={variant}
      />

      <EngageChat
        market={market}
        category={category || undefined}
        variant={variant}
        phoneHref={showPhone ? phone.href : null}
        phoneDisplay={showPhone ? phone.display : undefined}
        careersHref={careers}
      />
    </main>
  );
}
