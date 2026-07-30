import Link from "next/link";
import type { Metadata } from "next";
import LeadGate, { type GateCopy } from "../components/LeadGate";
import StickyCta from "../components/StickyCta";
import "./au.css";

export const metadata: Metadata = {
  title: "Virtual Coworker · AU — Hire a VA",
  description:
    "Vision demo: Australian businesses hiring dedicated virtual assistants.",
};

const gate: GateCopy = {
  eyebrow: "Free chat · takes 60 seconds",
  title: "Find your VA match",
  intentLabel: "First up — who are you?",
  intentPrimary: "I want to hire a VA",
  intentSecondary: "I'm after a job",
  divertHref: "/ph",
  divertTitle: "Looking for work, not hiring.",
  divertBody:
    "All our VA roles run through the Philippines careers site. We'll take you straight there rather than making you fill this in.",
  divertCta: "Go to VA careers →",
  q1Label: "What needs doing?",
  q1: ["Admin & inbox", "Customer service", "Sales / CRM", "Marketing", "Bookkeeping"],
  q2Label: "How many hours a week?",
  q2: ["10–20", "20–40", "Full time", "Not sure yet"],
  detailsLabel: "Where do we send it?",
  namePlaceholder: "Full name",
  emailLabel: "Email",
  emailPlaceholder: "Email",
  phoneLabel: "Phone",
  phonePlaceholder: "Phone — for a quicker call back",
  submit: "Find my VA →",
  reassure:
    "No lock-in contracts. We'll come back to you within one business day. Demo only — nothing is submitted.",
  callLabel: "Call tracking · AU line",
  phoneDisplay: "1300 886 740",
  phoneHref: "tel:+611300886740",
  doneTitle: "Beauty — that's all we need.",
  doneBody:
    "In the real build this fires the conversion event, routes to the AU team, and the keyword that drove the click follows the lead into the CRM.",
};

const benefits = [
  {
    k: "Talent",
    t: "The top 1% of applicants",
    d: "Screened for skills, reliability and English before a single CV reaches you.",
  },
  {
    k: "Price",
    t: "From $8/hr AUD, all in",
    d: "Our fee sits inside the hourly rate. No recruitment fee, no lock-in contract.",
  },
  {
    k: "Hours",
    t: "On your clock, not overnight",
    d: "Your VA works the Australian business day, so nothing sits until tomorrow.",
  },
  {
    k: "Control",
    t: "Pay for verified hours only",
    d: "Daily activity reports and desktop screenshots every 10 minutes, in your dashboard.",
  },
];

const lineup = [
  { src: "/brand/va-face-1.jpg", cap: "Executive assistant" },
  { src: "/brand/va-face-2.jpg", cap: "Customer service" },
  { src: "/brand/va-face-3.jpg", cap: "Bookkeeping & marketing" },
];

export default function AUHome() {
  return (
    <main className="au">
      <p className="vision-banner au-banner">
        Vision demo · <Link href="/">back to hub</Link> · not live product
      </p>

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
          <Link href="/" className="au-nav-link">
            All markets
          </Link>
          <a href="tel:+611300886740" className="au-navcall">
            <span aria-hidden>☎</span> 1300 886 740
          </a>
        </div>
      </nav>

      <section className="au-hero">
        <div className="au-hero-veil" aria-hidden />

        <div className="au-hero-inner">
          <div className="au-hero-copy">
            <p className="au-kicker anim-rise">AU · Dedicated virtual assistants</p>
            <h1 className="anim-rise">
              A <em>top 1%</em> Filipino VA for your Australian business.
            </h1>
            <p className="au-lead anim-rise-d1">
              Clear hourly pricing, hours that line up with yours, and someone
              who actually sticks around — not another platform to manage.
            </p>

            <ul className="au-ticks anim-rise-d1">
              <li>Works inside your time zone, not overnight</li>
              <li>Flat hourly rate, no lock-in contracts</li>
              <li>One dedicated assistant, matched to your business</li>
            </ul>

            <div className="trust-row trust-row-light anim-rise-d2">
              <span className="trust-chip">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="/brand/badge-clutch-au.webp"
                  alt="Top Clutch Virtual Assistant Company, Australia"
                />
                <span>
                  <b>Top VA company</b>
                  <span>Clutch · Australia</span>
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
                  src="/brand/badge-forbes-navy.webp"
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

          <figure className="va-card au-va anim-rise-d1">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/brand/va-au.jpg"
              alt="A Virtual Coworker assistant at his desk"
            />
            <span className="va-card-tag">
              <i />
              Your dedicated VA
            </span>
            <figcaption>
              <b>Admin &amp; operations</b>
              <span>Inbox, quotes and scheduling · on your AEST day</span>
            </figcaption>
          </figure>

          <LeadGate copy={gate} />
        </div>
      </section>

      <section className="au-sell">
        <div className="au-sell-inner">
          <div className="au-sell-head">
            <p className="au-sell-label">What you actually get</p>
            <h2>A vetted assistant, a flat hourly rate, and proof of the hours.</h2>
          </div>
          <div className="sell-grid sell-grid-light">
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

      <section className="au-proof" id="proof">
        <div className="au-proof-inner">
          <div>
            <p className="au-proof-label">Built for Aussie operators</p>
            <h2>Same company as the US site. Different door, on purpose.</h2>
            <div className="au-stats">
              <div>
                <strong>AEST</strong>
                <span>Hours that match yours</span>
              </div>
              <div>
                <strong>$8</strong>
                <span>Starting hourly rate</span>
              </div>
              <div>
                <strong>$0</strong>
                <span>Upfront hiring fee</span>
              </div>
            </div>
          </div>
          <div className="au-lineup">
            <p className="au-lineup-label">Who you&apos;d be working with</p>
            <div className="va-row">
              {lineup.map((p) => (
                <figure key={p.src}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={p.src} alt="" />
                  <figcaption>{p.cap}</figcaption>
                </figure>
              ))}
            </div>
            <figure className="au-quote">
              <blockquote>
                “We needed someone who&apos;d just get on with it — not another
                platform to manage.”
              </blockquote>
              <figcaption>Sample AU owner voice · vision copy</figcaption>
            </figure>
          </div>
        </div>
      </section>

      <section className="au-cta-bar">
        <p>Rather have a quick chat?</p>
        <div className="au-cta-bar-actions">
          <a href="tel:+611300886740" className="au-btn au-btn-primary">
            ☎ 1300 886 740
          </a>
          <Link href="/au#gate" className="au-btn au-btn-ghost">
            Back to the form
          </Link>
        </div>
      </section>

      <footer className="au-footer">
        <span>AU buyers vision · Virtual Coworker</span>
        <Link href="/ph">See the PH talent door →</Link>
      </footer>

      <StickyCta
        href="#gate"
        label="Find my VA"
        phoneDisplay="1300 886 740"
        phoneHref="tel:+611300886740"
      />
    </main>
  );
}
