import Link from "next/link";
import type { Metadata } from "next";
import LeadGate, { type GateCopy } from "../components/LeadGate";
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
        <div className="au-hero-media" aria-hidden>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/hero-au-2026.jpg" alt="" className="face-img" />
        </div>
        <div className="au-hero-veil" aria-hidden />

        <div className="au-hero-inner">
          <div className="au-hero-copy">
            <p className="au-kicker anim-rise">AU · Dedicated virtual assistants</p>
            <h1 className="anim-rise">
              A proper VA for your Australian business.
            </h1>
            <p className="au-lead anim-rise-d1">
              Clear pricing, hours that line up with yours, and someone who
              actually sticks around — not another platform for you to manage.
            </p>

            <ul className="au-ticks anim-rise-d1">
              <li>Support inside your time zone, not overnight</li>
              <li>Flat hourly rate, no lock-in contracts</li>
              <li>One dedicated assistant, matched to your business</li>
            </ul>

            <div className="trust trust-light anim-rise-d2">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/brand/clutch-au.webp"
                alt="Top Clutch Virtual Assistant Company, Australia"
              />
              <span className="trust-rule" aria-hidden />
              <span className="trust-copy">
                <strong>
                  Top Virtual Assistant
                  <br />
                  Company · Australia
                </strong>
                <span className="trust-stars" aria-hidden>
                  ★★★★★
                </span>
                <span>Clutch · verified reviews</span>
              </span>
            </div>
          </div>

          <LeadGate copy={gate} />
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
                <strong>1:1</strong>
                <span>Dedicated match</span>
              </div>
              <div>
                <strong>$0</strong>
                <span>Upfront hiring fee</span>
              </div>
            </div>
          </div>
          <figure className="au-quote">
            <blockquote>
              “We needed someone who&apos;d just get on with it — not another
              platform to manage.”
            </blockquote>
            <figcaption>Sample AU owner voice · vision copy</figcaption>
          </figure>
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
    </main>
  );
}
