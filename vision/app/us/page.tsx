import Link from "next/link";
import type { Metadata } from "next";
import LeadGate, { type GateCopy } from "../components/LeadGate";
import StickyCta from "../components/StickyCta";
import "./us.css";

export const metadata: Metadata = {
  title: "Virtual Coworker · US — Hire a VA",
  description:
    "Vision demo: US businesses hiring dedicated virtual assistants.",
};

const gate: GateCopy = {
  eyebrow: "Free consultation · takes 60 seconds",
  title: "Get matched with a dedicated VA",
  intentLabel: "First — who are you?",
  intentPrimary: "I'm hiring a VA",
  intentSecondary: "I'm looking for a job",
  divertHref: "/ph",
  divertTitle: "You're after work, not a hire.",
  divertBody:
    "Every Virtual Coworker VA role is run from the Philippines careers site. We'll send you straight there — no forms in between.",
  divertCta: "Go to VA careers →",
  q1Label: "What do you need off your plate?",
  q1: ["Admin & inbox", "Customer support", "Sales / CRM", "Marketing", "Bookkeeping"],
  q2Label: "How many hours a week?",
  q2: ["10–20", "20–40", "Full time", "Not sure yet"],
  detailsLabel: "Where do we send your match?",
  namePlaceholder: "Full name",
  emailLabel: "Work email",
  emailPlaceholder: "Work email",
  phoneLabel: "Phone",
  phonePlaceholder: "Phone — for a faster callback",
  submit: "Get my VA match →",
  reassure:
    "No fee to start. We reply within one business day. Demo only — nothing is submitted.",
  callLabel: "Call tracking · US line",
  phoneDisplay: "888 964 8644",
  phoneHref: "tel:+18889648644",
  doneTitle: "That's all we needed.",
  doneBody:
    "In the real build this fires the conversion event, routes to the US pod, and carries the source keyword into the CRM with the lead.",
};

const benefits = [
  {
    k: "Talent",
    t: "The top 1% of applicants",
    d: "Screened for skills, reliability and English before a single CV reaches you.",
  },
  {
    k: "Price",
    t: "From $7/hr, all in",
    d: "Our fee sits inside the hourly rate. No recruitment fee, no lock-in contract.",
  },
  {
    k: "Effort",
    t: "You interview. We do the rest.",
    d: "Recruitment, screening and payroll are ours. A success manager runs onboarding.",
  },
  {
    k: "Control",
    t: "Pay for verified hours only",
    d: "Daily activity reports and desktop screenshots every 10 minutes, in your dashboard.",
  },
];

const lineup = [
  { src: "/brand/va-face-1.jpg", cap: "Executive assistant" },
  { src: "/brand/va-face-2.jpg", cap: "Customer support" },
  { src: "/brand/va-face-3.jpg", cap: "Bookkeeping & marketing" },
];

export default function USHome() {
  return (
    <main className="us">
      <p className="vision-banner us-banner">
        Vision demo · <Link href="/">back to hub</Link> · not live product
      </p>

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
          <Link href="/" className="us-nav-link">
            All markets
          </Link>
          <a href="tel:+18889648644" className="us-navcall">
            <span aria-hidden>☎</span> 888 964 8644
          </a>
        </div>
      </nav>

      <section className="us-hero">
        <div className="us-hero-bg" aria-hidden />

        <div className="us-hero-inner">
          <div className="us-hero-copy">
            <p className="us-kicker anim-rise">US · Dedicated virtual assistants</p>
            <h1 className="anim-rise">
              Hire the <em>top 1%</em> of Filipino virtual assistants.
            </h1>
            <p className="us-lead anim-rise-d1">
              One dedicated assistant for your US business — matched to your
              workflow, working your hours, accountable from week one.
            </p>

            <ul className="us-ticks anim-rise-d1">
              <li>One dedicated VA, not a shared pool</li>
              <li>Works your US business hours</li>
              <li>No upfront hiring fee, no lock-in</li>
            </ul>

            <div className="trust-row anim-rise-d2">
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="/brand/clutch-us.webp"
                  alt="Top Clutch Virtual Assistant Company, United States 2026"
                />
                <span>
                  <b>Top VA company</b>
                  <span>Clutch · US 2026</span>
                </span>
              </span>
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src="/brand/badge-google-5star.webp" alt="Google 5-star reviews" />
                <span>
                  <b>5-star reviews</b>
                  <span>Google · verified</span>
                </span>
              </span>
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="/brand/badge-forbes-white.webp"
                  alt="Forbes Business Council 2026 official member"
                />
                <span>
                  <b>Business Council</b>
                  <span>Forbes · member 2026</span>
                </span>
              </span>
              <span className="trust-chip trust-chip-stat">
                <span>
                  <b>
                    <em>2011</em>
                  </b>
                  <span>Placing staff since</span>
                </span>
              </span>
            </div>
          </div>

          <figure className="va-card us-va anim-rise-d1">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/brand/va-us.jpg"
              alt="A Virtual Coworker executive assistant at her desk"
            />
            <span className="va-card-tag">
              <i />
              Your dedicated VA
            </span>
            <figcaption>
              <b>Executive assistant</b>
              <span>Inbox, calendar and CRM · works 9–5 your time</span>
            </figcaption>
          </figure>

          <LeadGate copy={gate} />
        </div>
      </section>

      <section className="us-sell">
        <div className="us-sell-inner">
          <div className="us-sell-head">
            <p className="us-proof-label">What you actually get</p>
            <h2>A vetted assistant, a flat hourly rate, and proof of the hours.</h2>
          </div>
          <div className="sell-grid">
            {benefits.map((b) => (
              <div className="sell-card" key={b.k}>
                <em>{b.k}</em>
                <strong>{b.t}</strong>
                <p>{b.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="us-proof" id="proof">
        <div className="us-proof-inner">
          <div>
            <p className="us-proof-label">Why US teams stay</p>
            <h2>One assistant. Clear ownership. No freelancer roulette.</h2>
            <div className="us-stats">
              <div>
                <strong>1:1</strong>
                <span>Dedicated match</span>
              </div>
              <div>
                <strong>$7</strong>
                <span>Starting hourly rate</span>
              </div>
              <div>
                <strong>$0</strong>
                <span>Upfront hiring fee</span>
              </div>
            </div>
          </div>
          <div className="us-lineup">
            <p className="us-lineup-label">Who you&apos;d be working with</p>
            <div className="va-row">
              {lineup.map((p) => (
                <figure key={p.src}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={p.src} alt="" />
                  <figcaption>{p.cap}</figcaption>
                </figure>
              ))}
            </div>
            <p className="us-lineup-note">
              Career VAs in the Philippines — not gig-site freelancers. You
              interview the shortlist and pick your own.
            </p>
          </div>
        </div>
      </section>

      <section className="us-cta-bar">
        <p>Rather just talk it through?</p>
        <div className="us-cta-bar-actions">
          <a href="tel:+18889648644" className="us-btn us-btn-primary">
            ☎ 888 964 8644
          </a>
          <Link href="/us#gate" className="us-btn us-btn-ghost">
            Back to the form
          </Link>
        </div>
      </section>

      <footer className="us-footer">
        <span>US buyers vision · Virtual Coworker</span>
        <Link href="/au">See the AU door →</Link>
      </footer>

      <StickyCta
        href="#gate"
        label="Get my VA match"
        phoneDisplay="888 964 8644"
        phoneHref="tel:+18889648644"
      />
    </main>
  );
}
