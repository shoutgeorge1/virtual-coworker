import Link from "next/link";
import type { Metadata } from "next";
import "./us.css";

export const metadata: Metadata = {
  title: "Virtual Coworker · US — Hire a VA",
  description:
    "Vision demo: US businesses hiring dedicated virtual assistants.",
};

export default function USHome() {
  return (
    <main className="us">
      <p className="vision-banner us-banner">
        Vision demo ·{" "}
        <Link href="/">back to hub</Link> · not live product
      </p>

      <nav className="us-nav">
        <Link href="/us" className="us-brand">
          Virtual Coworker
        </Link>
        <div className="us-nav-links">
          <Link href="/us#proof">Proof</Link>
          <Link href="/us/consult">Free consultation</Link>
          <Link href="/">All markets</Link>
        </div>
      </nav>

      <section className="us-hero">
        <div className="us-hero-bg" aria-hidden />
        <div className="us-hero-grid" aria-hidden />

        <p className="us-hero-brand anim-rise">Virtual Coworker</p>
        <h1 className="anim-rise-d1">Your next hire already works remotely.</h1>
        <p className="us-hero-lead anim-rise-d2">
          Dedicated virtual assistants for US businesses that need execution —
          not another freelancer roulette. Matched. Managed. Accountable.
        </p>

        <div className="us-cta-row anim-rise-d2">
          <Link href="/us/consult" className="us-btn us-btn-primary">
            Book a free consultation
          </Link>
          <Link href="/us#proof" className="us-btn us-btn-ghost">
            See how it works
          </Link>
        </div>

        <div className="us-gate-wrap anim-fade">
          <p className="us-gate-label">Before you continue — who are you?</p>
          <div className="gate">
            <Link href="/us/consult" className="gate-btn gate-hire">
              <strong>I&apos;m hiring a VA</strong>
              <span>US business · get matched &amp; consult</span>
            </Link>
            <Link href="/ph" className="gate-btn gate-job">
              <strong>I&apos;m looking for a job</strong>
              <span>Talent opportunities live on the PH site →</span>
            </Link>
          </div>
        </div>
      </section>

      <section className="us-proof" id="proof">
        <p className="us-proof-label">Why US teams stay</p>
        <h2>One dedicated assistant. Clear ownership. No roulette.</h2>
        <p>
          Vision direction: a buyer site that sounds like American business —
          direct, confident, and gated so job seekers never poison the hire
          funnel.
        </p>
        <div className="us-stats">
          <div>
            <strong>1:1</strong>
            <span>Dedicated match</span>
          </div>
          <div>
            <strong>US</strong>
            <span>Business hours overlap</span>
          </div>
          <div>
            <strong>0</strong>
            <span>Upfront hiring fees*</span>
          </div>
        </div>
      </section>

      <footer className="us-footer">
        <span>US buyers vision · Virtual Coworker</span>
        <Link href="/au">See AU look →</Link>
      </footer>
    </main>
  );
}
