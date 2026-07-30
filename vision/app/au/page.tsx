import Link from "next/link";
import type { Metadata } from "next";
import "./au.css";

export const metadata: Metadata = {
  title: "Virtual Coworker · AU — Hire a VA",
  description:
    "Vision demo: Australian businesses hiring dedicated virtual assistants.",
};

export default function AUHome() {
  return (
    <main className="au">
      <p className="vision-banner au-banner">
        Vision demo ·{" "}
        <Link href="/">back to hub</Link> · not live product
      </p>

      <nav className="au-nav">
        <Link href="/au" className="au-brand">
          Virtual Coworker
        </Link>
        <div className="au-nav-links">
          <Link href="/au#proof">Stories</Link>
          <Link href="/au/consult">Book a chat</Link>
          <Link href="/">All markets</Link>
        </div>
      </nav>

      <section className="au-hero">
        <div className="au-hero-sky" aria-hidden />
        <div className="au-hero-wave" aria-hidden />

        <p className="au-hero-brand anim-rise">Virtual Coworker</p>
        <h1 className="anim-rise-d1">
          A proper VA for your Australian business.
        </h1>
        <p className="au-hero-lead anim-rise-d2">
          Clear pricing. Local support hours that make sense. An assistant who
          feels like part of the team — without the twin look of the US site.
        </p>

        <div className="au-cta-row anim-rise-d2">
          <Link href="/au/consult" className="au-btn au-btn-primary">
            Book a free chat
          </Link>
          <Link href="/au#proof" className="au-btn au-btn-ghost">
            Hear from Aussie owners
          </Link>
        </div>

        <div className="au-gate-wrap anim-fade">
          <p className="au-gate-label">Quick check — which path?</p>
          <div className="gate">
            <Link href="/au/consult" className="gate-btn gate-hire">
              <strong>I want to hire a VA</strong>
              <span>Australian business · book a chat</span>
            </Link>
            <Link href="/ph" className="gate-btn gate-job">
              <strong>I&apos;m after a job</strong>
              <span>Talent applications live on the PH site →</span>
            </Link>
          </div>
        </div>
      </section>

      <section className="au-proof" id="proof">
        <div className="au-proof-inner">
          <div>
            <p className="au-proof-label">Built for Aussie operators</p>
            <h2>Same company. Different door. Different feel.</h2>
            <p>
              Vision direction: coastal light, warm type, and hire-first gating —
              so AU buyers never land in a US clone or a job board by mistake.
            </p>
          </div>
          <div className="au-quote">
            <blockquote>
              “We needed someone who just got on with it — not another platform
              to manage.”
            </blockquote>
            <cite>— Sample AU owner voice (vision copy)</cite>
          </div>
        </div>
      </section>

      <footer className="au-footer">
        <span>AU buyers vision · Virtual Coworker</span>
        <Link href="/ph">See PH talent look →</Link>
      </footer>
    </main>
  );
}
