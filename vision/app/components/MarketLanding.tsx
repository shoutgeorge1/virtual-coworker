import Link from "next/link";
import LeadGate, { type GateCopy } from "./LeadGate";
import StickyCta from "./StickyCta";
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

  const h1 = v ? v.h1[market] : cfg.headline;
  const sub = v ? v.subhead[market] : cfg.prop;
  const primaryCta = v?.primaryCta || "Tell us who you need →";
  const heroSrc = v ? v.heroImage[market] : market === "us" ? "/brand/va-us.jpg" : "/brand/va-au.jpg";
  const heroAlt = v?.heroAlt || "Virtual Coworker team member at a desk";
  const benefits = cat?.benefits || [
    "Staffing partner — not a freelance marketplace",
    "Philippines-based talent matched to your role brief",
    "You interview and choose who to hire",
    "Payroll + account management after you hire",
  ];
  const faq = cat?.faq || [
    {
      q: "Is this for employers?",
      a: "Yes. Job seekers use the careers destination — not this form.",
    },
    {
      q: "Does a form submit equal a job order?",
      a: "No. Submit is an employer inquiry. Job order and placement come later if you proceed.",
    },
    {
      q: "Why Philippines staff?",
      a: "English-proficient professionals who work your hours. We recruit and screen; you interview and decide.",
    },
    {
      q: "Does a phone click equal a qualified call?",
      a: "No. Phone CTA click is tracked separately until CallRail + human qualification exist.",
    },
  ];

  const showPhone = phone.configured && Boolean(phone.href);
  const shell = market === "us" ? "us" : "au";
  const light = market === "au";

  const gate: GateCopy = {
    eyebrow: "Employers only · about 60 seconds",
    title: cat ? `Hire ${cat.label} support` : "Tell us who you need",
    intentLabel: "First — who are you?",
    intentPrimary: "I’m hiring staff for a business.",
    intentSecondary: "I’m looking for a job.",
    divertTitle: "Looking for work?",
    divertBody:
      "This page is for businesses hiring staff. Job applications go to the careers destination — not our employer form.",
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
    reassure:
      "Employers only. A submit is a hiring inquiry — not a job order or placement. By submitting you agree to our privacy notice.",
    callLabel: showPhone
      ? market === "us"
        ? "Call · US business line"
        : "Call · AU business line"
      : "",
    phoneDisplay: phone.display,
    phoneHref: phone.href,
    showPhone,
    doneTitle: "Request received.",
    doneBody:
      "Thanks — a teammate will follow up using the details you provided. This is an inquiry, not a confirmed placement.",
  };

  return (
    <main className={shell} data-variant={variant} data-category={category || "generic"}>
      <SiteNav tone={light ? "light" : "dark"} market={market} />

      <section className={`${shell}-hero`}>
        <div className={market === "us" ? "us-hero-bg" : "au-hero-veil"} aria-hidden />

        <div className={`${shell}-hero-inner`}>
          <div className={`${shell}-hero-copy`}>
            <p className={`${shell}-kicker anim-rise`}>
              {cfg.label} · Employers
              {cat ? ` · ${cat.label}` : ""}
              {" · "}Philippines talent
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
                  alt="Clutch recognition badge"
                />
                <span>
                  <b>Clutch</b>
                  <span>Recognition badge</span>
                </span>
              </span>
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src="/brand/badge-google-5star.webp" alt="Google 5-Star Reviews badge" />
                <span>
                  <b>Google</b>
                  <span>Reviews badge</span>
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
                  alt="Forbes Business Council badge"
                />
                <span>
                  <b>Forbes</b>
                  <span>Business Council badge</span>
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

          <figure className={`va-card ${shell}-va anim-rise-d1`}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={heroSrc} alt={heroAlt} />
            <span className="va-card-tag">
              <i />
              {cat ? cat.shortLabel : "Dedicated hire"}
            </span>
            <figcaption>
              <b>{cat ? `${cat.label} path` : "Matched to your role"}</b>
              <span>
                Employer inquiry · {market === "us" ? "US business hours" : "AU business hours"} · Philippines talent
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
              How staffing works here
            </p>
            <h2>
              One clear path: brief the role, interview shortlisted Philippines talent, hire with support.
            </h2>
            <p className={`${shell}-sell-sub`}>
              Built for employers who want ownership of the hire — not gig-platform churn.{" "}
              <Link href="/how-it-works">See the full process →</Link>
            </p>
          </div>
          <div className={`sell-grid sell-grid-3${light ? " sell-grid-light" : ""}`}>
            {[
              {
                k: "Recruit",
                t: "We source and screen",
                d: "You send a role brief. Our Philippines recruitment team sources and screens candidates aligned to your tools and workflow — not a resume dump.",
              },
              {
                k: "Choose",
                t: "You interview",
                d: "You meet shortlisted talent on video, ask what matters to your business, and decide who joins. No mystery matching.",
              },
              {
                k: "Operate",
                t: "We support the hire",
                d: "Once you hire, we handle employment ops and account management so you stay focused on the work — and remain the client.",
              },
            ].map((b) => (
              <div className="sell-card" key={b.k}>
                <em>{b.k}</em>
                <strong>{b.t}</strong>
                <p>{b.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <TrustQuotes light={light} />

      <section className={`${shell}-sell`} style={{ paddingTop: 0 }}>
        <div className={`${shell}-sell-inner`}>
          <div className={`${shell}-sell-head`}>
            <p className={market === "us" ? "us-proof-label" : "au-proof-label"}>FAQ</p>
            <h2>Straight answers before you inquire.</h2>
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
        <p>{showPhone ? "Prefer to talk?" : "Ready to tell us who you need?"}</p>
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
        Legal: {SITE.copyright}. Addresses published on virtualcoworker.com/contact/.
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
    </main>
  );
}
