"use client";

import Link from "next/link";
import { useState } from "react";
import "./ph.css";

const copy = {
  en: {
    brandTag: "Careers",
    navApply: "Apply",
    navHub: "All markets",
    kicker: "PH · Build a VA career",
    h1: "Your next chapter starts here.",
    lead: "Real VA roles with real clients. Training, support, and a path — not another gig post that disappears.",
    cta: "Apply now",
    cta2: "See open tracks",
    gate: "Hiring a VA for your business? Use the US or AU buyer sites — this door is for talent only.",
    proofLabel: "Why people apply",
    proofH2: "Opportunity energy. Same brand. Career, not chaos.",
    proofP:
      "Warmer evolution of Virtual Coworker — navy, cyan, gold, with orange CTAs — built for talent, never mixed with hire funnels.",
    tracks: [
      {
        t: "Admin & ops",
        d: "Inbox, calendars, follow-ups that keep owners sane.",
        img: "/brand/ea.jpg",
      },
      {
        t: "Support",
        d: "Customers who feel heard — across time zones.",
        img: "/brand/support.jpg",
      },
      {
        t: "Growth support",
        d: "CRM hygiene, outreach assists, campaign help.",
        img: "/brand/marketing.webp",
      },
    ],
    foot: "PH talent vision · Virtual Coworker",
  },
  tl: {
    brandTag: "Careers",
    navApply: "Mag-apply",
    navHub: "Lahat ng market",
    kicker: "PH · Magtayo ng VA career",
    h1: "Dito nagsisimula ang susunod mong chapter.",
    lead: "Totoong VA roles, totoong clients. May training at support — hindi gig na biglang nawawala.",
    cta: "Mag-apply ngayon",
    cta2: "Tingnan ang tracks",
    gate: "Naghahanap ng VA para sa business? Pumunta sa US o AU buyer site — ang pintong ito ay para sa talent lang.",
    proofLabel: "Bakit nag-a-apply ang mga tao",
    proofH2: "Opportunity energy. Parehong brand. Career, hindi chaos.",
    proofP:
      "Mas mainit na evolution ng Virtual Coworker — navy, cyan, gold, orange CTAs — para sa talent, hindi nahahalo sa hire funnel.",
    tracks: [
      {
        t: "Admin & ops",
        d: "Inbox, calendars, follow-ups para sa owners.",
        img: "/brand/ea.jpg",
      },
      {
        t: "Support",
        d: "Customers na nararamdaman — kahit iba ang timezone.",
        img: "/brand/support.jpg",
      },
      {
        t: "Growth support",
        d: "CRM, outreach assists, campaign help.",
        img: "/brand/marketing.webp",
      },
    ],
    foot: "PH talent vision · Virtual Coworker",
  },
};

export default function PHHome() {
  const [lang, setLang] = useState<"en" | "tl">("en");
  const t = copy[lang];

  return (
    <main className="ph">
      <p className="vision-banner ph-banner">
        Vision demo · <Link href="/">back to hub</Link> · not live product
      </p>

      <nav className="ph-nav">
        <Link href="/ph" className="ph-brand">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/brand/logo-vc.png"
            alt="Virtual Coworker"
            className="logo-img logo-img-on-dark"
          />
          <span className="ph-brand-tag">{t.brandTag}</span>
        </Link>
        <div className="ph-nav-right">
          <div className="ph-nav-links">
            <Link href="/ph/apply">{t.navApply}</Link>
            <Link href="/">{t.navHub}</Link>
          </div>
          <div className="ph-lang" role="group" aria-label="Language">
            <button
              type="button"
              className={lang === "en" ? "active" : ""}
              onClick={() => setLang("en")}
            >
              EN
            </button>
            <button
              type="button"
              className={lang === "tl" ? "active" : ""}
              onClick={() => setLang("tl")}
            >
              TL
            </button>
          </div>
        </div>
      </nav>

      <section className="ph-hero">
        <div className="ph-hero-media" aria-hidden>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/jumping.webp" alt="" />
        </div>
        <div className="ph-hero-bg" aria-hidden />

        <p className="ph-hero-kicker anim-rise">{t.kicker}</p>
        <h1 className="anim-rise-d1">{t.h1}</h1>
        <p className="ph-hero-lead anim-rise-d2">{t.lead}</p>

        <div className="ph-cta-row anim-rise-d2">
          <Link href="/ph/apply" className="ph-btn ph-btn-primary">
            {t.cta}
          </Link>
          <Link href="/ph#tracks" className="ph-btn ph-btn-ghost">
            {t.cta2}
          </Link>
        </div>

        <p className="ph-gate-note anim-fade">
          {t.gate}{" "}
          <Link href="/us">US</Link> · <Link href="/au">AU</Link>
        </p>
      </section>

      <section className="ph-proof" id="tracks">
        <p className="ph-proof-label">{t.proofLabel}</p>
        <h2>{t.proofH2}</h2>
        <p>{t.proofP}</p>
        <div className="ph-tracks">
          {t.tracks.map((track) => (
            <div className="ph-track" key={track.t}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={track.img} alt="" />
              <div className="ph-track-body">
                <strong>{track.t}</strong>
                <span>{track.d}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="ph-faces">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/talent-arvin.jpg" alt="VA team member" />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/talent-john.jpeg" alt="VA team member" />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/hire-talent.webp" alt="Specialized talent" />
        </div>
      </section>

      <footer className="ph-footer">
        <span>{t.foot}</span>
        <Link href="/us">See US buyer look →</Link>
      </footer>
    </main>
  );
}
