import Link from "next/link";
import LeadGate, { type GateCopy } from "./LeadGate";
import StickyCta from "./StickyCta";
import ExitIntent from "./ExitIntent";
import SiteNav from "./SiteNav";
import SiteFooter from "./SiteFooter";
import TrustQuotes from "./TrustQuotes";
import {
  MARKETS,
  resolveCareersUrl,
  resolvePhone,
  type MarketId,
} from "../../config/markets";
import {
  CATEGORIES,
  type AbVariant,
  type CategorySlug,
} from "../../config/categories";
import { SITE } from "../../config/site";
import type { HeroOverlay } from "../../lib/hero-overlay";
import { resolveHeroSecondaryBadge } from "../../lib/hero-badge-copy";

export default function MarketLanding({
  market,
  category,
  variant,
  heroOverlay = "none",
}: {
  market: MarketId;
  category?: CategorySlug | null;
  variant: AbVariant;
  /** QA-only image overlay treatments (?hero=badge|pill|hot). Default = current chrome. */
  heroOverlay?: HeroOverlay;
}) {
  const cfg = MARKETS[market];
  const phone = resolvePhone(market);
  const careers = resolveCareersUrl();
  const cat = category ? CATEGORIES[category] : null;
  const v = cat ? cat.variants[variant] : null;
  const isAu = market === "au";

  const h1 = v ? v.h1[market] : cfg.headline;
  const sub = v ? v.subhead[market] : cfg.prop;
  const primaryCta = v?.primaryCta || "Tell us who you need →";
  const heroSrc = v
    ? v.heroImage[market]
    : market === "us"
      ? "/brand/va-us.jpg"
      : "/brand/va-au.jpg";
  const heroAlt = v?.heroAlt || "Virtual Coworker team member at a desk";

  const benefits = cat?.benefits ||
    (isAu
      ? [
          "Filipino talent matched to Australian business hours",
          "You interview before anyone joins your team",
          "We handle payroll and ongoing support after you hire",
          "A staffing partner — not a freelance marketplace",
        ]
      : [
          "Philippines talent matched to your US hours and tools",
          "You interview before anyone joins your team",
          "We handle payroll and account support after you hire",
          "A staffing partner — not a freelance marketplace",
        ]);

  const faq = cat?.faq ||
    (isAu
      ? [
          {
            q: "Is this for businesses or job seekers?",
            a: "Businesses only. If you’re looking for work, use the careers link in the footer.",
          },
          {
            q: "What happens after I send my role?",
            a: "Our team follows up for a short hiring conversation. From there we take your brief, shortlist screened candidates, and you interview before anyone starts.",
          },
          {
            q: "Why hire from the Philippines?",
            a: "English-proficient professionals who can work Australian business hours. We recruit and screen; you choose who to hire.",
          },
          {
            q: "Do I have to hire someone from the shortlist?",
            a: "No. You meet candidates on video and decide. There’s no pressure to hire if it isn’t the right fit.",
          },
        ]
      : [
          {
            q: "Is this for businesses or job seekers?",
            a: "Businesses only. If you’re looking for work, use the careers link in the footer.",
          },
          {
            q: "What happens after I send my role?",
            a: "Our team follows up for a short hiring conversation. From there we take your brief, shortlist screened candidates, and you interview before anyone starts.",
          },
          {
            q: "Why hire from the Philippines?",
            a: "English-proficient professionals who can work your hours. We recruit and screen; you choose who to hire.",
          },
          {
            q: "Do I have to hire someone from the shortlist?",
            a: "No. You meet candidates on video and decide. There’s no pressure to hire if it isn’t the right fit.",
          },
        ]);

  const processSteps = isAu
    ? [
        {
          k: "01",
          t: "Hiring conversation",
          d: "Tell us the role. We follow up to talk through what you need, hours, and tools — so we know it’s a fit before recruiting starts.",
        },
        {
          k: "02",
          t: "We recruit and screen",
          d: "Share your brief. Our Philippines recruitment team sources and screens candidates against your must-haves — not a resume dump.",
        },
        {
          k: "03",
          t: "You interview and choose",
          d: "Review a shortlist, meet people on video, and pick who joins. You stay in control of the hire.",
        },
        {
          k: "04",
          t: "Onboard with support",
          d: "Once you hire, we help with onboarding, employment admin, and ongoing account support so you can focus on the work.",
        },
      ]
    : [
        {
          k: "01",
          t: "Hiring conversation",
          d: "Tell us the role. We follow up to talk through what you need, hours, and tools — so we know it’s a fit before recruiting starts.",
        },
        {
          k: "02",
          t: "We recruit and screen",
          d: "Share your brief. Our Philippines recruitment team sources and screens candidates against your must-haves — not a resume dump.",
        },
        {
          k: "03",
          t: "You interview and choose",
          d: "Review a shortlist, meet people on video, and pick who joins. You stay in control of the hire.",
        },
        {
          k: "04",
          t: "Onboard with support",
          d: "Once you hire, we help with onboarding, payroll, and ongoing account support so you can focus on the work.",
        },
      ];

  const showPhone = phone.configured && Boolean(phone.href);
  const shell = market === "us" ? "us" : "au";
  const light = market === "au";

  const gate: GateCopy = {
    eyebrow: isAu ? "Businesses only · about a minute" : "Employers only · about a minute",
    title: cat ? `Hire ${cat.label}` : "Tell us who you need",
    intentLabel: "First — who are you?",
    intentPrimary: isAu
      ? "I’m hiring staff for a business."
      : "I’m hiring staff for a business.",
    intentSecondary: "I’m looking for a job.",
    divertTitle: "Looking for work?",
    divertBody: isAu
      ? "This page is for businesses hiring staff. Job applications go to careers — not this form."
      : "This page is for businesses hiring staff. Job applications go to careers — not this form.",
    divertCta: "Go to careers →",
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
      ? "Businesses only. This starts a conversation with our team — not an instant hire. By submitting you agree to our privacy notice."
      : "Employers only. This starts a conversation with our team — not an instant hire. By submitting you agree to our privacy notice.",
    callLabel: showPhone
      ? market === "us"
        ? "Prefer to call?"
        : "Prefer to call?"
      : "",
    phoneDisplay: phone.display,
    phoneHref: phone.href,
    showPhone,
    doneTitle: "Got it — thanks.",
    doneBody: isAu
      ? "A teammate will follow up to talk through the role and next steps."
      : "A teammate will follow up to talk through the role and next steps.",
  };

  const showOverlay = heroOverlay !== "none";
  // Prefer image overlays over recoloring H1 — hot keeps default typography.
  const h1Class = "anim-rise";
  const secondaryBadge = resolveHeroSecondaryBadge(market, category);

  return (
    <main
      className={shell}
      data-variant={variant}
      data-category={category || "generic"}
      data-hero={heroOverlay}
    >
      <SiteNav tone={light ? "light" : "dark"} market={market} />

      <section className={`${shell}-hero`}>
        <div className={market === "us" ? "us-hero-bg" : "au-hero-veil"} aria-hidden />

        <div className={`${shell}-hero-inner`}>
          <div className={`${shell}-hero-copy`}>
            <p className={`${shell}-kicker anim-rise`}>
              {cfg.label} · {isAu ? "Businesses" : "Employers"}
              {cat ? ` · ${cat.label}` : ""}
              {" · "}Philippines talent
            </p>
            <h1 className={h1Class}>{h1}</h1>
            <p className={`${shell}-lead anim-rise-d1`}>{sub}</p>

            <ul className={`${shell}-ticks anim-rise-d1`}>
              {benefits.map((b) => (
                <li key={b}>{b}</li>
              ))}
            </ul>

            <p className={`${shell}-lead anim-rise-d2`} style={{ marginTop: "0.75rem" }}>
              {cfg.staffingExplain}
            </p>

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
                  <span>Recognized</span>
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
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={
                    market === "us"
                      ? "/brand/badge-forbes-white.webp"
                      : "/brand/badge-forbes-navy.webp"
                  }
                  alt="Forbes Business Council"
                />
                <span>
                  <b>Forbes</b>
                  <span>Business Council</span>
                </span>
              </span>
              <span className="trust-chip trust-chip-stat">
                <em>PH</em>
                <span>
                  <b>Philippines</b>
                  <span>Dedicated hires</span>
                </span>
              </span>
            </div>
          </div>

          <figure
            className={`va-card ${shell}-va anim-rise-d1${
              showOverlay ? ` va-card-hero-${heroOverlay}` : ""
            }`}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={heroSrc} alt={heroAlt} />
            {!showOverlay ? (
              <span className="va-card-tag">
                <i />
                {cat ? cat.shortLabel : "Dedicated hire"}
              </span>
            ) : null}
            {showOverlay ? (
              <div
                className={`va-hero-badge-stack va-hero-badge-stack-${heroOverlay}`}
              >
                {heroOverlay === "pill" ? (
                  <div
                    className="va-hero-badge va-hero-badge-pill"
                    aria-label="Dedicated full-time, monthly"
                  >
                    <strong>Dedicated · Full-time</strong>
                    <span>Monthly placement</span>
                  </div>
                ) : (
                  <div
                    className="va-hero-badge va-hero-badge-circle"
                    aria-label="Dedicated full-time, monthly"
                  >
                    <span className="va-hero-badge-glow" aria-hidden />
                    <span className="va-hero-badge-ring" aria-hidden />
                    <span className="va-hero-badge-core">
                      <em>Dedicated</em>
                      <strong>Full-time</strong>
                      <span>Monthly</span>
                    </span>
                  </div>
                )}
                {secondaryBadge.kind === "rate" ? (
                  <div
                    className="va-hero-badge va-hero-badge-rate"
                    aria-label={secondaryBadge.rate.aria}
                  >
                    <strong>{secondaryBadge.rate.amount}</strong>
                    <span>{secondaryBadge.rate.unit}</span>
                  </div>
                ) : (
                  <div
                    className="va-hero-badge va-hero-badge-ph"
                    aria-label={secondaryBadge.aria}
                  >
                    <strong>{secondaryBadge.label}</strong>
                    <span>{secondaryBadge.sub}</span>
                  </div>
                )}
              </div>
            ) : null}
            <figcaption>
              <b>{cat ? `${cat.label}` : "Matched to your role"}</b>
              <span>
                {isAu
                  ? "Australian business hours · Philippines talent"
                  : "US business hours · Philippines talent"}
              </span>
            </figcaption>
          </figure>

          <LeadGate
            copy={gate}
            market={market}
            category={category}
            variant={variant}
            preselectedRole={cat ? cat.formLabel : null}
          />
        </div>
      </section>

      <section className={`${shell}-sell`}>
        <div className={`${shell}-sell-inner`}>
          <div className={`${shell}-sell-head`}>
            <p className={market === "us" ? "us-proof-label" : "au-proof-label"}>
              How hiring works
            </p>
            <h2>
              {isAu
                ? "From first chat to a teammate on your hours — you stay in control."
                : "From first conversation to a teammate on your hours — you stay in control."}
            </h2>
            <p className={`${shell}-sell-sub`}>
              {isAu
                ? "Built for Australian businesses that want ownership of the hire — not a gig platform. "
                : "Built for US employers that want ownership of the hire — not a gig platform. "}
              <Link href={`/how-it-works?market=${market}`}>
                See the full process →
              </Link>
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

      <TrustQuotes light={light} market={market} />

      <section className={`${shell}-sell`} style={{ paddingTop: 0 }}>
        <div className={`${shell}-sell-inner`}>
          <div className={`${shell}-sell-head`}>
            <p className={market === "us" ? "us-proof-label" : "au-proof-label"}>
              Questions
            </p>
            <h2>
              {isAu
                ? "Straight answers before you start."
                : "Straight answers before you start."}
            </h2>
          </div>
          <div className={`sell-grid${light ? " sell-grid-light" : ""}`}>
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
            : isAu
              ? "Ready to hire Filipino staff for your business?"
              : "Ready to hire Philippines staff for your business?"}
        </p>
        <div className={`${shell}-cta-bar-actions`}>
          {showPhone ? (
            <a href={phone.href!} className={`${shell}-btn ${shell}-btn-primary`}>
              ☎ {phone.display}
            </a>
          ) : null}
          <a href="#gate" className={`${shell}-btn ${shell}-btn-ghost`}>
            {primaryCta.replace(/→$/, "").trim()}
          </a>
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
        label={primaryCta.replace(/→$/, "").trim()}
        market={market}
        phoneDisplay={showPhone ? phone.display : undefined}
        phoneHref={showPhone ? phone.href : null}
        category={category || undefined}
        variant={variant}
      />

      <ExitIntent
        market={market}
        gateHref="#gate"
        category={category || undefined}
        variant={variant}
      />
    </main>
  );
}
