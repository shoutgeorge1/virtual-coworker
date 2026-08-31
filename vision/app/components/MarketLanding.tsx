import Link from "next/link";
import LeadGate, { type GateCopy } from "./LeadGate";
import StickyCta from "./StickyCta";
import EngageChat from "./EngageChat";
import ExitIntent from "./ExitIntent";
import QuizConversionSlot from "./QuizConversionSlot";
import LpDensity from "./LpDensity";
import SiteNav from "./SiteNav";
import SiteFooter from "./SiteFooter";
import TrustBand from "./TrustBand";
import PressBand from "./PressBand";
import RoleOutcomes from "./RoleOutcomes";
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
  yearsTrading,
} from "../../config/site";
import GoogleReviewBadge, { RatingStars } from "./GoogleReviewBadge";
import SocialReachBadges from "./SocialReachBadges";
import {
  breadcrumbJsonLd,
  faqPageJsonLd,
  organizationJsonLd,
  professionalServiceJsonLd,
  websiteJsonLd,
} from "../../lib/seo";
import { highlightH1Role } from "../../lib/h1-role-highlight";
import { isUngatedEmployerLp } from "../../lib/ungated-us-home";

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
  const ungated = isUngatedEmployerLp({
    market,
    category,
    conversionSurface,
  });
  const years = yearsTrading();
  const gbp = googleBusinessForMarket(market);

  const quizHero = isAu
    ? {
        h1: "Find the right virtual assistant for your business",
        sub: "Take the employer hiring quiz. We’ll name the role that takes the load - then you can book a free strategy call.",
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
  // Simplified paid form LPs: AU light chrome for both markets (park dark US shell).
  // Quiz routes keep market shell so richer quiz UX stays intact.
  const shell = isQuiz ? (market === "us" ? "us" : "au") : "au";
  const light = isQuiz ? market === "au" : true;

  const formCue = isQuiz
    ? isAu
      ? { label: "Take the quiz", body: "A few taps - then book a free strategy call." }
      : { label: "Take the quiz", body: "A few taps - then book a free strategy call." }
    : FORM_CUE[market];

  const gate: GateCopy = {
    eyebrow: isAu ? "About a minute · obligation free" : "About a minute · free strategy call",
    title: cat
      ? isAu
        ? `Book a free chat about ${cat.label}`
        : `Book a free strategy call for ${cat.label}`
      : isAu
        ? "Book a free strategy call"
        : "Book a free strategy call",
    intentLabel: "Are you hiring?",
    intentPrimary: "Yes - hiring for my business",
    intentSecondary: "No - looking for work",
    divertTitle: "Looking for work?",
    divertBody:
      "Happy to help - job applications live on our Philippines careers site.",
    divertCta: "Philippines careers →",
    careersHref: careers,
    roleLabel: "What do you need help with?",
    roles: cfg.servicesProposed,
    detailsLabel: "How can we reach you?",
    nameLabel: "Full name",
    namePlaceholder: "Full name",
    emailLabel: "Business Email Address",
    emailPlaceholder: "Business Email Address",
    phoneLabel: "Phone",
    phonePlaceholder: isAu ? "0400 000 000" : "(201) 555-0123",
    submit: primaryCta,
    reassure: ungated
      ? isAu
        ? "Obligation free, at no cost. About a minute. A teammate will follow up for a short chat - not an instant hire. We don’t sell your information."
        : "Obligation free, at no cost. About a minute. A teammate follows up within one business day. We don’t sell your information."
      : isAu
        ? "Obligation free, at no cost. A teammate will follow up for a short chat - not an instant hire. We don’t sell your information."
        : "Obligation free, at no cost. A teammate follows up within one business day. We don’t sell your information.",
    callLabel: showPhone ? "Prefer to talk?" : "",
    phoneDisplay: phone.display,
    phoneHref: phone.href,
    showPhone,
    doneTitle: "Thanks - you’re in.",
    doneBody: isAu
      ? "A teammate will follow up shortly about the role and next steps."
      : "A teammate will call you to talk through the role and next steps.",
    websiteLabel: ungated ? "Company website (optional)" : undefined,
    websitePlaceholder: ungated ? "https://" : undefined,
    careersUnderForm: ungated
      ? "Looking for work? Visit our Philippines careers site."
      : undefined,
    audienceLine: ungated
      ? "For businesses hiring staff - not a job board."
      : undefined,
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
      className={`${shell}${isQuiz ? " quiz-lp" : ""}${ungated ? " ungated-us-home" : ""}`}
      data-variant={variant}
      data-category={category || "generic"}
      data-cta-mode={isQuiz ? "quiz_lp" : "form_primary"}
      data-lp-surface={conversionSurface}
      data-ungated-us-home={ungated ? "true" : undefined}
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
      <LpDensity market={market} forceLean={!isQuiz} />
      <SiteNav tone={light ? "light" : "dark"} market={market} />

      <section className={`${shell}-hero`}>
        <div className={shell === "us" ? "us-hero-bg" : "au-hero-veil"} aria-hidden />

        <div className={`${shell}-hero-inner`}>
          <div className={`${shell}-hero-copy`}>
            <p className={`${shell}-kicker anim-rise`}>
              {cfg.label} · {isAu ? "Businesses" : "Employers"}
              {cat ? ` · ${cat.label}` : ""}
              {isQuiz ? " · Employer hiring quiz" : ""}
              {" · "}Philippines staffing
            </p>
            <h1 className="anim-rise">{highlightH1Role(h1)}</h1>
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
              className={`trust-row trust-row-hero anim-rise-d2${light ? " trust-row-light" : ""}`}
            >
              <SocialReachBadges />
              <GoogleReviewBadge proof={gbp} />
              <span
                className="trust-chip trust-chip-review"
                aria-label={`Clutch ${TRUST_PROOF.clutch.rating} out of 5`}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={market === "us" ? "/brand/clutch-us.webp" : "/brand/badge-clutch-au.webp"}
                  alt=""
                />
                <span>
                  <b className="trust-chip-rating-line">
                    <RatingStars size={15} />
                    {TRUST_PROOF.clutch.rating}
                  </b>
                  <span className="trust-chip-meta">Clutch</span>
                </span>
              </span>
              <span className="trust-chip trust-chip-stat trust-chip-cred">
                <em>{years}+</em>
                <span>
                  <b>Years</b>
                  <span>placing Filipino staff</span>
                </span>
              </span>
            </div>
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
                ungated={ungated}
              />
            )}
            <ul className="gate-nudges">
              <li>Obligation free</li>
              <li>{isQuiz ? "A few taps" : "About a minute"}</li>
              <li>Specialist follows up</li>
              <li>We don’t sell your info</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Form money LPs: keep TrustBand (testimonials + client marks + legitimacy).
          Park press / how-hiring sell brochure bands — quiz LPs keep the richer stack.
          Category form keeps RoleOutcomes. */}
      {isQuiz ? <PressBand light={light} market={market} /> : null}

      {category ? (
        <RoleOutcomes category={category} market={market} light={light} />
      ) : null}

      {isQuiz ? (
        <section className={`${shell}-sell`}>
          <div className={`${shell}-sell-inner`}>
            <div className={`${shell}-sell-head`}>
              <p className={shell === "us" ? "us-proof-label" : "au-proof-label"}>
                How hiring works
              </p>
              <h2>White-glove hiring. Not a freelancer marketplace.</h2>
              <p className={`${shell}-sell-sub`} data-lp="secondary">
                {isAu
                  ? "Free strategy call. Job description. We recruit and vet. You get profiles with hourly rates, then you interview. We handle employment admin and stay on after they start. "
                  : "Free strategy call. Job description. We recruit and vet. You get profiles with hourly rates, then you interview. We handle payroll, HR, and time tracking. "}
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
      ) : null}

      <TrustBand light={light} market={market} />

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
        observeSubmit={ungated}
      />

      <EngageChat
        market={market}
        category={category || undefined}
        variant={variant}
        phoneHref={showPhone ? phone.href : null}
        phoneDisplay={showPhone ? phone.display : undefined}
        careersHref={careers}
        skipIntentGate={ungated}
      />

      {ungated ? null : (
        <ExitIntent
          market={market}
          category={category || undefined}
          variant={variant}
          phoneHref={showPhone ? phone.href : null}
          phoneDisplay={showPhone ? phone.display : undefined}
          careersHref={careers}
        />
      )}
    </main>
  );
}
