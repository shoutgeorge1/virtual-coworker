import Link from "next/link";
import type { Metadata } from "next";
import LeadGate, { type GateCopy } from "../components/LeadGate";
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
        <div className="us-hero-media" aria-hidden>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/hero-us-2026.jpg" alt="" className="face-img" />
        </div>
        <div className="us-hero-bg" aria-hidden />

        <div className="us-hero-inner">
          <div className="us-hero-copy">
            <p className="us-kicker anim-rise">US · Dedicated virtual assistants</p>
            <h1 className="anim-rise">
              Your next hire already works remotely.
            </h1>
            <p className="us-lead anim-rise-d1">
              Dedicated VAs for US businesses that need execution — matched to
              your workflow, managed, and accountable from week one.
            </p>

            <ul className="us-ticks anim-rise-d1">
              <li>One dedicated assistant, not a shared pool</li>
              <li>Works your US business hours</li>
              <li>No upfront hiring fee</li>
            </ul>

            <div className="trust anim-rise-d2">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/brand/clutch-us.webp"
                alt="Top Clutch Virtual Assistant Company, United States 2026"
              />
              <span className="trust-rule" aria-hidden />
              <span className="trust-copy">
                <strong>
                  Top Virtual Assistant
                  <br />
                  Company · United States
                </strong>
                <span className="trust-stars" aria-hidden>
                  ★★★★★
                </span>
                <span>Clutch · 2026</span>
              </span>
            </div>
          </div>

          <LeadGate copy={gate} />
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
                <strong>24h</strong>
                <span>Reply on consultations</span>
              </div>
              <div>
                <strong>$0</strong>
                <span>Upfront hiring fee</span>
              </div>
            </div>
          </div>
          <div className="us-proof-visual">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/brand/how-it-works.webp"
              alt="Two Virtual Coworker assistants"
              className="cutout-img"
            />
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
    </main>
  );
}
