"use client";

import Link from "next/link";
import { useState } from "react";
import SiteFooter from "../components/SiteFooter";
import "./ph.css";

/* Careers destination for job-seeker gate redirects. Not a paid employer LP. */
const faces = [
  { src: "/brand/talent-arvin.jpg", pos: "50% 10%", cap: "Arvin · Client support" },
  { src: "/brand/ea.jpg", pos: "50% 12%", cap: "Marie · Executive assistant" },
  { src: "/brand/support.jpg", pos: "50% 14%", cap: "Support desk" },
];

const copy = {
  en: {
    brandTag: "Careers",
    kicker: "PH · Build a VA career",
    h1: "Your next chapter starts here.",
    lead: "Real VA roles with real clients — training, support and a path. Not another gig post that disappears in a week.",
    ticks: [
      "Work from home with long-term clients",
      "Paid training and a real support team",
      "No placement fees, ever",
    ],
    facesLabel: "People already doing it",
    vaTag: "Now hiring",
    vaRole: "Admin & operations VA",
    vaMeta: "Work from home · long-term client · full-time hours",
    ctaTitle: "Start your application",
    ctaBody:
      "This door is for talent only. Businesses hiring staff should use the US or Australia hiring pages — linked in the footer.",
    ctaApply: "Go to application →",
  },
  tl: {
    brandTag: "Careers",
    kicker: "PH · Magtayo ng VA career",
    h1: "Dito nagsisimula ang susunod mong chapter.",
    lead: "Totoong VA roles, totoong clients — may training, support at malinaw na daan.",
    ticks: [
      "Work from home kasama ang long-term clients",
      "May bayad na training at totoong support team",
      "Walang placement fee, kailanman",
    ],
    facesLabel: "Mga kasama na ngayon",
    vaTag: "Kumukuha ngayon",
    vaRole: "Admin & operations VA",
    vaMeta: "Work from home · long-term client · full-time hours",
    ctaTitle: "Simulan ang application mo",
    ctaBody:
      "Para sa talent lang ang pintong ito. Kung business ang hanap mo, gamitin ang US o Australia hiring pages sa footer.",
    ctaApply: "Pumunta sa application →",
  },
};

export default function PHHome() {
  const [lang, setLang] = useState<"en" | "tl">("en");
  const t = copy[lang];

  return (
    <main className="ph">
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
          <Link href="/ph/apply" className="ph-nav-link ph-nav-link-primary">
            Apply
          </Link>
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
        <div className="ph-hero-bg" aria-hidden />
        <div className="ph-hero-inner">
          <div className="ph-hero-copy">
            <p className="ph-kicker anim-rise">{t.kicker}</p>
            <h1 className="anim-rise">{t.h1}</h1>
            <p className="ph-lead anim-rise-d1">{t.lead}</p>
            <ul className="ph-ticks anim-rise-d1">
              {t.ticks.map((tick) => (
                <li key={tick}>{tick}</li>
              ))}
            </ul>
            <p className="ph-faces-label">{t.facesLabel}</p>
            <div className="va-row anim-rise-d2">
              {faces.map((f) => (
                <figure key={f.src}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={f.src} alt="" style={{ objectPosition: f.pos }} />
                  <figcaption>{f.cap}</figcaption>
                </figure>
              ))}
            </div>
          </div>

          <figure className="va-card ph-va anim-rise-d1">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/brand/va-ph.jpg"
              alt="A Virtual Coworker VA working from home"
            />
            <span className="va-card-tag">
              <i />
              {t.vaTag}
            </span>
            <figcaption>
              <b>{t.vaRole}</b>
              <span>{t.vaMeta}</span>
            </figcaption>
          </figure>

          <aside className="gate-card anim-rise-d1" id="gate">
            <div className="gate-card-head">
              <p className="gate-card-eyebrow">Careers</p>
              <h2>{t.ctaTitle}</h2>
            </div>
            <div className="gate-card-body">
              <p
                className="gate-reassure"
                style={{ textAlign: "left", marginTop: 0 }}
              >
                {t.ctaBody}
              </p>
              <Link href="/ph/apply" className="gate-submit">
                {t.ctaApply}
              </Link>
            </div>
          </aside>
        </div>
      </section>

      <SiteFooter tone="dark" market="ph" />
    </main>
  );
}
