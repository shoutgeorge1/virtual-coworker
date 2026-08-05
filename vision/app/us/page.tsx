import Link from "next/link";
import type { Metadata } from "next";
import LeadGate, { type GateCopy } from "../components/LeadGate";
import StickyCta from "../components/StickyCta";
import { MARKETS, resolveCareersUrl, resolvePhone } from "../../config/markets";
import "./us.css";

export const metadata: Metadata = {
  title: "Hire Offshore Staff | Virtual Coworker US",
  description:
    "Employer landing page for US businesses hiring dedicated Philippines-based staff through Virtual Coworker.",
  robots: { index: false, follow: false },
};

const market = MARKETS.us;

export default function USHome() {
  const phone = resolvePhone("us");
  const careers = resolveCareersUrl();

  const gate: GateCopy = {
    eyebrow: "Employers only · about 60 seconds",
    title: "Request a hiring consult",
    intentLabel: "First — who are you?",
    intentPrimary: "I’m hiring staff for a business.",
    intentSecondary: "I’m looking for a job.",
    divertTitle: "Looking for work?",
    divertBody:
      "This page is for businesses hiring staff. Job applications go to the careers destination — not our employer sales form.",
    divertCta: "Go to careers →",
    careersHref: careers,
    roleLabel: "What do you need help with?",
    roles: market.servicesProposed,
    detailsLabel: "Your business details",
    nameLabel: "Full name",
    namePlaceholder: "Full name",
    emailLabel: "Work email",
    emailPlaceholder: "Work email",
    phoneLabel: "Business phone",
    phonePlaceholder: "Business phone",
    companyLabel: "Company",
    companyPlaceholder: "Company name",
    submit: "Request consult →",
    reassure:
      "Employers only. We’ll reply using the details you provide. By submitting you agree to our privacy notice.",
    callLabel: phone.configured ? "Call · US business line" : "US business phone · set in config",
    phoneDisplay: phone.display,
    phoneHref: phone.href,
    doneTitle: "Request received.",
    doneBody: "Thanks — a teammate will follow up using the details you provided.",
  };

  return (
    <main className="us">
      <nav className="us-nav">
        <Link href="/us" className="us-brand">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/brand/logo-vc.png"
            alt="Virtual Coworker"
            className="logo-img logo-img-on-dark"
          />
        </Link>
        <div className="us-nav-right">
          {phone.href ? (
            <a
              href={phone.href}
              className="us-navcall"
              data-track="phone_click"
            >
              <span aria-hidden>☎</span> {phone.display}
            </a>
          ) : (
            <span className="us-navcall" aria-label="US business phone placeholder">
              <span aria-hidden>☎</span> {phone.display}
            </span>
          )}
        </div>
      </nav>

      <section className="us-hero">
        <div className="us-hero-bg" aria-hidden />

        <div className="us-hero-inner">
          <div className="us-hero-copy">
            <p className="us-kicker anim-rise">United States · Employers</p>
            <h1 className="anim-rise">{market.headline}</h1>
            <p className="us-lead anim-rise-d1">{market.prop}</p>

            <ul className="us-ticks anim-rise-d1">
              <li>Staffing partner — not a freelance marketplace</li>
              <li>You interview and choose who to hire</li>
              <li>Clear employer path from inquiry to placement ops</li>
            </ul>

            <p className="us-lead anim-rise-d2" style={{ marginTop: "0.75rem" }}>
              {market.staffingExplain}
            </p>

            <div className="trust-row anim-rise-d2">
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="/brand/clutch-us.webp"
                  alt="Clutch recognition badge"
                />
                <span>
                  <b>Clutch</b>
                  <span>Recognition badge</span>
                </span>
              </span>
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src="/brand/badge-google-5star.webp" alt="Google reviews badge" />
                <span>
                  <b>Google</b>
                  <span>Reviews badge</span>
                </span>
              </span>
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="/brand/badge-forbes-white.webp"
                  alt="Forbes Business Council badge"
                />
                <span>
                  <b>Forbes</b>
                  <span>Business Council badge</span>
                </span>
              </span>
            </div>
          </div>

          <figure className="va-card us-va anim-rise-d1">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/brand/va-us.jpg"
              alt="Virtual Coworker team member at a desk"
            />
            <span className="va-card-tag">
              <i />
              Dedicated hire
            </span>
            <figcaption>
              <b>Matched to your role</b>
              <span>Employer consult · US business hours</span>
            </figcaption>
          </figure>

          <LeadGate copy={gate} market="us" />
        </div>
      </section>

      <section className="us-sell">
        <div className="us-sell-inner">
          <div className="us-sell-head">
            <p className="us-proof-label">How staffing works here</p>
            <h2>One primary path: tell us the role, interview shortlisted talent, hire with support.</h2>
          </div>
          <div className="sell-grid">
            {[
              {
                k: "Recruit",
                t: "We source and screen",
                d: "Role brief in → shortlist of candidates aligned to your workflow.",
              },
              {
                k: "Choose",
                t: "You interview",
                d: "You decide who joins your business. No mystery matching.",
              },
              {
                k: "Operate",
                t: "We support the hire",
                d: "Account management and employment ops so you stay focused on the work.",
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

      <section className="us-cta-bar">
        <p>Prefer to talk?</p>
        <div className="us-cta-bar-actions">
          {phone.href ? (
            <a href={phone.href} className="us-btn us-btn-primary">
              ☎ {phone.display}
            </a>
          ) : (
            <span className="us-btn us-btn-primary" aria-disabled="true">
              ☎ {phone.display}
            </span>
          )}
          <a href="#gate" className="us-btn us-btn-ghost">
            Back to the form
          </a>
        </div>
      </section>

      <footer className="us-footer">
        <span>US employer paid LP · Virtual Coworker</span>
        <Link href="/privacy">Privacy</Link>
      </footer>

      <StickyCta
        href="#gate"
        label="Request consult"
        market="us"
        phoneDisplay={phone.display}
        phoneHref={phone.href}
      />
    </main>
  );
}
