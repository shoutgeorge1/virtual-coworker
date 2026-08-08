import Link from "next/link";
import LeadGate, { type GateCopy } from "./LeadGate";
import StickyCta from "./StickyCta";
import EngageChat from "./EngageChat";
import RoleQuiz from "./RoleQuiz";
import QuizTeaser from "./QuizTeaser";
import LpDensity from "./LpDensity";
import SiteNav from "./SiteNav";
import SiteFooter from "./SiteFooter";
import TrustBand from "./TrustBand";
import PressBand from "./PressBand";
import PainGain from "./PainGain";
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
  PRIMARY_HIRE_CTA,
  employerFaq,
  roleHeroBenefits,
} from "../../config/employer-cro";
import { SITE, yearsTrading } from "../../config/site";
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
}: {
  market: MarketId;
  category?: CategorySlug | null;
  variant: AbVariant;
}) {
  const cfg = MARKETS[market];
  const phone = resolvePhone(market);
  const careers = resolveCareersUrl();
  const cat = category ? CATEGORIES[category] : null;
  const v = cat ? cat.variants[variant] : null;
  const isAu = market === "au";
  const years = yearsTrading();

  const h1 = v ? v.h1[market] : cfg.headline;
  const sub = v ? v.subhead[market] : cfg.prop;
  const primaryCta = v?.primaryCta || PRIMARY_HIRE_CTA;
  const heroSrc = v
    ? v.heroImage[market]
    : market === "us"
      ? "/brand/va-us.jpg"
      : "/brand/va-au.jpg";
  const heroAlt = v?.heroAlt || "Virtual Coworker team member at a desk";

  const benefits = category
    ? roleHeroBenefits(category)
    : isAu
      ? [
          "Filipino talent matched to Australian business hours",
          "You interview before anyone joins your team",
          "We handle employment admin and ongoing support after you hire",
          "A staffing partner — not a freelance marketplace",
        ]
      : [
          "Dedicated Filipino coworkers for US business ops",
          "We recruit and vet — you interview and decide",
          "We handle payroll and account support after you hire",
          "A staffing partner — not a freelance marketplace",
        ];

  const faq = employerFaq(market, cat?.label || null, category);
  const processSteps = hiringProcessStrip(market);

  const showPhone = phone.configured && Boolean(phone.href);
  const shell = market === "us" ? "us" : "au";
  const light = market === "au";

  const gate: GateCopy = {
    eyebrow: isAu ? "Businesses only · 2 minutes" : "Employers only · 2 minutes",
    title: cat ? `Hire ${cat.label}` : "Start Hiring — 2 minutes.",
    intentLabel: "First — who are you?",
    intentPrimary: "I’m hiring for a business.",
    intentSecondary: "I’m looking for a job.",
    divertTitle: "Looking for work?",
    divertBody:
      "This page is for businesses hiring staff. Job applications open on our Philippines careers site — not this form.",
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
    phonePlaceholder: "Business phone",
    companyLabel: "Company",
    companyPlaceholder: "Company name",
    submit: primaryCta,
    reassure: isAu
      ? "Businesses only. This starts a conversation — not an instant hire. By submitting you agree to our privacy notice."
      : "Employers only. This starts a conversation — not an instant hire. By submitting you agree to our privacy notice.",
    callLabel: showPhone ? "Prefer to call?" : "",
    phoneDisplay: phone.display,
    phoneHref: phone.href,
    showPhone,
    doneTitle: "Got it — thanks.",
    doneBody: "A teammate will follow up to talk through the role and next steps.",
  };

  const breadcrumbs = cat
    ? [
        { name: "Home", path: cfg.landingPath },
        { name: "Roles", path: `/services?market=${market}` },
        { name: cat.label, path: `${cfg.landingPath}/${cat.slug}` },
      ]
    : [
        { name: "Home", path: cfg.landingPath },
        { name: "How it works", path: `/how-it-works?market=${market}` },
      ];

  return (
    <main
      className={shell}
      data-variant={variant}
      data-category={category || "generic"}
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
              {" · "}Filipino talent
            </p>
            <h1 className="anim-rise">{h1}</h1>
            <p className={`${shell}-lead anim-rise-d1`}>{sub}</p>

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

            <QuizTeaser light={light} />

            <div
              className={`trust-row anim-rise-d2${light ? " trust-row-light" : ""}`}
            >
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={market === "us" ? "/brand/clutch-us.webp" : "/brand/badge-clutch-au.webp"}
                  alt="Clutch"
                />
                <span>
                  <b>Clutch</b>
                  <span>{isAu ? "Recognised" : "Recognized"}</span>
                </span>
              </span>
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src="/brand/badge-google-5star.webp" alt="Google Reviews" />
                <span>
                  <b>Google</b>
                  <span>Reviews</span>
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
              Rates discussed once we understand the role — not buried in fine print.
            </p>
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

          <LeadGate
            copy={gate}
            market={market}
            category={category}
            variant={variant}
            preselectedRole={cat ? cat.formLabel : null}
          />
        </div>
      </section>

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
            <h2>
              {isAu
                ? "From first chat to a teammate on your hours."
                : "From first call to a teammate on your hours."}
            </h2>
            <p className={`${shell}-sell-sub`} data-lp="secondary">
              {isAu
                ? "For Australian businesses that want to own the hire — not rent freelancers. "
                : "For US employers that want to own the hire — not rent freelancers. "}
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

      <RoleQuiz
        market={market}
        category={category || undefined}
        variant={variant}
        light={light}
        phoneDisplay={showPhone ? phone.display : undefined}
        phoneHref={showPhone ? phone.href : null}
      />

      {/* Featured In sits below quiz — keeps Happy customers (logos + reviews) uncluttered. */}
      <PressBand light={light} />

      <section className={`${shell}-sell faq-section`}>
        <div className={`${shell}-sell-inner`}>
          <div className={`${shell}-sell-head`}>
            <p className={market === "us" ? "us-proof-label" : "au-proof-label"}>
              Questions
            </p>
            <h2>Straight answers before you start.</h2>
          </div>
          {/* FAQ stays visible on both lp_density arms — never mark secondary. */}
          <div
            className={`sell-grid faq-grid${light ? " sell-grid-light" : ""}`}
          >
            {faq.map((item) => (
              <div className="sell-card sell-card-faq" key={item.q}>
                <strong>{item.q}</strong>
                <p>{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className={`${shell}-cta-bar`}>
        <p>
          {showPhone
            ? "Ready to hire — or prefer to talk?"
            : "Ready to hire Filipino staff for your business?"}
        </p>
        <div className={`${shell}-cta-bar-actions`}>
          <a href="#gate" className={`${shell}-btn ${shell}-btn-primary`}>
            {PRIMARY_HIRE_CTA}
          </a>
          {showPhone ? (
            <a href={phone.href!} className={`${shell}-btn ${shell}-btn-ghost`}>
              Call Our Team · {phone.display}
            </a>
          ) : null}
        </div>
      </section>

      <SiteFooter
        tone={light ? "light" : "dark"}
        market={market}
        categoryLabel={cat?.label}
      />

      <p className="sr-only">
        {SITE.copyright}. Offices: {SITE.addressUs}; {SITE.addressAu}.
      </p>

      <StickyCta
        href="#gate"
        label={PRIMARY_HIRE_CTA}
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
