import Link from "next/link";
import LeadGate, { type GateCopy } from "./LeadGate";
import StickyCta from "./StickyCta";
import ExitIntent from "./ExitIntent";
import EngageChat from "./EngageChat";
import RoleQuiz from "./RoleQuiz";
import SiteNav from "./SiteNav";
import SiteFooter from "./SiteFooter";
import TrustQuotes from "./TrustQuotes";
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
import { SITE } from "../../config/site";
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
          "Dedicated Filipino VAs and remote staff for US business ops",
          "We recruit and vet — you interview and decide",
          "We handle payroll and account support after you hire",
          "A staffing partner — not a freelance marketplace",
        ]);

  const faq = cat?.faq ||
    (isAu
      ? [
          {
            q: "Is this for businesses or job seekers?",
            a: "Businesses only. If you’re looking for work, use Looking for a job? in the footer — it opens our Philippines careers site.",
          },
          {
            q: "What happens after I send my role?",
            a: "Our team follows up for a short hiring conversation. From there we take your brief, shortlist screened candidates, and you interview before anyone starts.",
          },
          {
            q: "Why hire Filipino talent?",
            a: "English-proficient professionals who can work Australian business hours. Our Filipino recruitment team sources and screens; you choose who to hire.",
          },
          {
            q: "Do I have to hire someone from the shortlist?",
            a: "No. You meet candidates on video and decide. There’s no pressure to hire if it isn’t the right fit.",
          },
        ]
      : [
          {
            q: "Is this for businesses or job seekers?",
            a: "Businesses only. If you’re looking for work, use Looking for a job? in the footer — it opens our Philippines careers site.",
          },
          {
            q: "What happens after I send my role?",
            a: "Our team follows up for a short hiring conversation. From there we take your brief, shortlist screened candidates, and you interview before anyone starts.",
          },
          {
            q: "Why hire Filipino talent?",
            a: "English-proficient Filipino professionals who can support US business ops. Our Filipino recruitment team sources and screens; you interview and decide who to hire.",
          },
          {
            q: "Do I have to hire someone from the shortlist?",
            a: "No. You meet candidates on video and decide. There’s no pressure to hire if it isn’t the right fit.",
          },
        ]);

  const processSteps = hiringProcessStrip(market);

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
                  <b>Filipino</b>
                  <span>Dedicated hires</span>
                </span>
              </span>
            </div>
          </div>

          <figure className={`va-card ${shell}-va anim-rise-d1`}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={heroSrc} alt={heroAlt} />
            <span className="va-card-tag">
              <i />
              {cat ? cat.shortLabel : "Dedicated hire"}
            </span>
            <figcaption>
              <b>{cat ? `${cat.label}` : "Matched to your role"}</b>
              <span>
                {isAu
                  ? "Australian business hours · Filipino talent"
                  : "US business hours · Filipino talent"}
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

      <TrustQuotes light={light} market={market} />

      <RoleQuiz
        market={market}
        category={category || undefined}
        variant={variant}
        light={light}
      />

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
            : "Ready to hire Filipino staff for your business?"}
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
        phoneHref={showPhone ? phone.href : null}
        phoneDisplay={showPhone ? phone.display : undefined}
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
