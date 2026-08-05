import Link from "next/link";
import type { Metadata } from "next";
import LeadGate, { type GateCopy } from "../components/LeadGate";
import StickyCta from "../components/StickyCta";
import { MARKETS, resolveCareersUrl, resolvePhone } from "../../config/markets";
import "./au.css";

export const metadata: Metadata = {
  title: "Hire Offshore Staff | Virtual Coworker Australia",
  description:
    "Employer landing page for Australian businesses hiring dedicated Philippines-based staff through Virtual Coworker.",
  robots: { index: false, follow: false },
};

const market = MARKETS.au;

export default function AUHome() {
  const phone = resolvePhone("au");
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
    callLabel: phone.configured ? "Call · AU business line" : "AU business phone · set in config",
    phoneDisplay: phone.display,
    phoneHref: phone.href,
    doneTitle: "Request received.",
    doneBody: "Thanks — a teammate will follow up using the details you provided.",
  };

  return (
    <main className="au">
      <nav className="au-nav">
        <Link href="/au" className="au-brand">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/brand/logo-vc.png"
            alt="Virtual Coworker"
            className="logo-img"
          />
        </Link>
        <div className="au-nav-right">
          {phone.href ? (
            <a href={phone.href} className="au-navcall" data-track="phone_click">
              <span aria-hidden>☎</span> {phone.display}
            </a>
          ) : (
            <span className="au-navcall" aria-label="AU business phone placeholder">
              <span aria-hidden>☎</span> {phone.display}
            </span>
          )}
        </div>
      </nav>

      <section className="au-hero">
        <div className="au-hero-veil" aria-hidden />

        <div className="au-hero-inner">
          <div className="au-hero-copy">
            <p className="au-kicker anim-rise">Australia · Employers</p>
            <h1 className="anim-rise">{market.headline}</h1>
            <p className="au-lead anim-rise-d1">{market.prop}</p>

            <ul className="au-ticks anim-rise-d1">
              <li>Built for Australian employers hiring offshore staff</li>
              <li>You interview — we recruit and support the ops</li>
              <li>Separate from the careers / job-seeker path</li>
            </ul>

            <p className="au-lead anim-rise-d2" style={{ marginTop: "0.75rem" }}>
              {market.staffingExplain}
            </p>

            <div className="trust-row trust-row-light anim-rise-d2">
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="/brand/badge-clutch-au.webp"
                  alt="Clutch Australia recognition badge"
                />
                <span>
                  <b>Clutch</b>
                  <span>Australia badge</span>
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
                  src="/brand/badge-forbes-navy.webp"
                  alt="Forbes Business Council badge"
                />
                <span>
                  <b>Forbes</b>
                  <span>Business Council badge</span>
                </span>
              </span>
            </div>
          </div>

          <figure className="va-card au-va anim-rise-d1">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/brand/va-au.jpg"
              alt="Virtual Coworker team member at a desk"
            />
            <span className="va-card-tag">
              <i />
              Dedicated hire
            </span>
            <figcaption>
              <b>Matched to your role</b>
              <span>Employer consult · Australian business day</span>
            </figcaption>
          </figure>

          <LeadGate copy={gate} market="au" />
        </div>
      </section>

      <section className="au-sell">
        <div className="au-sell-inner">
          <div className="au-sell-head">
            <p className="au-sell-label">How staffing works here</p>
            <h2>One primary path: brief the role, interview shortlisted talent, hire with support.</h2>
          </div>
          <div className="sell-grid sell-grid-light">
            {[
              {
                k: "Recruit",
                t: "We source and screen",
                d: "Role brief in → shortlist aligned to how your business actually works.",
              },
              {
                k: "Choose",
                t: "You interview",
                d: "You decide who joins. Clear ownership stays with your business.",
              },
              {
                k: "Operate",
                t: "We support the hire",
                d: "Account management and employment ops after you hire.",
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

      <section className="au-cta-bar">
        <p>Prefer a quick chat?</p>
        <div className="au-cta-bar-actions">
          {phone.href ? (
            <a href={phone.href} className="au-btn au-btn-primary">
              ☎ {phone.display}
            </a>
          ) : (
            <span className="au-btn au-btn-primary" aria-disabled="true">
              ☎ {phone.display}
            </span>
          )}
          <a href="#gate" className="au-btn au-btn-ghost">
            Back to the form
          </a>
        </div>
      </section>

      <footer className="au-footer">
        <span>AU employer paid LP · Virtual Coworker</span>
        <Link href="/privacy">Privacy</Link>
      </footer>

      <StickyCta
        href="#gate"
        label="Request consult"
        market="au"
        phoneDisplay={phone.display}
        phoneHref={phone.href}
      />
    </main>
  );
}
