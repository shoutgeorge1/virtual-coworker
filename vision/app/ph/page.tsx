"use client";

import Link from "next/link";
import { useState } from "react";
import LeadGate, { type GateCopy } from "../components/LeadGate";
import "./ph.css";

/* Modern portraits lead; the headset/desk shots stay as supporting texture.
   Every position is tuned so no head is ever clipped. */
const faces = [
  { src: "/brand/talent-john.jpeg", pos: "50% 14%", cap: "John · Ops & admin" },
  { src: "/brand/talent-arvin.jpg", pos: "50% 12%", cap: "Arvin · Client support" },
  { src: "/brand/support.jpg", pos: "50% 15%", cap: "Support desk" },
  { src: "/brand/marketing.webp", pos: "68% 24%", cap: "Marketing support" },
];

const copy = {
  en: {
    brandTag: "Careers",
    navHub: "All markets",
    kicker: "PH · Build a VA career",
    h1: "Your next chapter starts here.",
    lead: "Real VA roles with real clients — training, support and a path. Not another gig post that disappears in a week.",
    ticks: [
      "Work from home with long-term clients",
      "Paid training and a real support team",
      "No placement fees, ever",
    ],
    facesLabel: "People already doing it",
    tracksLabel: "Where you could land",
    tracksH2: "Pick the track you're strongest at.",
    tracks: [
      { t: "Admin & ops", d: "Inbox, calendars and follow-ups that keep an owner sane." },
      { t: "Customer support", d: "Customers who feel heard — across time zones." },
      { t: "Growth support", d: "CRM hygiene, outreach assists, campaign help." },
    ],
    foot: "PH talent vision · Virtual Coworker",
    footLink: "See the US buyer door →",
    gate: {
      eyebrow: "Apply · takes 60 seconds",
      title: "Start your application",
      intentLabel: "First — who are you?",
      intentPrimary: "I want VA work",
      intentSecondary: "I'm hiring a VA",
      divertHref: "/us",
      divertTitle: "You're hiring, not applying.",
      divertBody:
        "This door is talent-only on purpose. Business owners go to the US or AU site so the two funnels never mix.",
      divertCta: "Go to the buyer site →",
      q1Label: "What are you strongest at?",
      q1: ["Admin & ops", "Customer support", "Sales / CRM", "Marketing", "Bookkeeping"],
      q2Label: "How much experience?",
      q2: ["New to VA work", "1–2 years", "3+ years"],
      detailsLabel: "How do we reach you?",
      namePlaceholder: "Full name",
      emailLabel: "Email",
      emailPlaceholder: "Email",
      phoneLabel: "Mobile",
      phonePlaceholder: "Mobile number",
      submit: "Send my application →",
      reassure:
        "No placement fees. We reply within one business day. Demo only — nothing is submitted.",
      callLabel: "Call tracking · per campaign",
      phoneDisplay: "Recruitment hotline",
      phoneHref: "",
      doneTitle: "Application in.",
      doneBody:
        "In the real build this fires the conversion event, routes to PH recruitment, and the ad that earned the click is credited with the applicant.",
    } as GateCopy,
  },
  tl: {
    brandTag: "Careers",
    navHub: "Lahat ng market",
    kicker: "PH · Magtayo ng VA career",
    h1: "Dito nagsisimula ang susunod mong chapter.",
    lead: "Totoong VA roles, totoong clients — may training, support at malinaw na daan. Hindi gig na biglang nawawala.",
    ticks: [
      "Work from home kasama ang long-term clients",
      "May bayad na training at totoong support team",
      "Walang placement fee, kailanman",
    ],
    facesLabel: "Mga kasama na ngayon",
    tracksLabel: "Saan ka pwedeng mapunta",
    tracksH2: "Piliin ang track na pinakamalakas mo.",
    tracks: [
      { t: "Admin & ops", d: "Inbox, calendars at follow-ups para sa mga owner." },
      { t: "Customer support", d: "Customers na nararamdamang pinapakinggan — kahit iba ang timezone." },
      { t: "Growth support", d: "CRM, outreach assists, tulong sa campaign." },
    ],
    foot: "PH talent vision · Virtual Coworker",
    footLink: "Tingnan ang US buyer door →",
    gate: {
      eyebrow: "Mag-apply · 60 segundo lang",
      title: "Simulan ang application mo",
      intentLabel: "Una — sino ka?",
      intentPrimary: "Gusto ko ng VA work",
      intentSecondary: "Naghahanap ako ng VA",
      divertHref: "/us",
      divertTitle: "Nag-hi-hire ka, hindi nag-a-apply.",
      divertBody:
        "Ang pintong ito ay para sa talent lang. Ang mga business owner ay sa US o AU site para hindi maghalo ang dalawang funnel.",
      divertCta: "Pumunta sa buyer site →",
      q1Label: "Ano ang pinakamalakas mo?",
      q1: ["Admin & ops", "Customer support", "Sales / CRM", "Marketing", "Bookkeeping"],
      q2Label: "Gaano karaming karanasan?",
      q2: ["Baguhan sa VA work", "1–2 taon", "3+ taon"],
      detailsLabel: "Paano ka namin makokontak?",
      namePlaceholder: "Buong pangalan",
      emailLabel: "Email",
      emailPlaceholder: "Email",
      phoneLabel: "Mobile",
      phonePlaceholder: "Mobile number",
      submit: "Ipadala ang application →",
      reassure:
        "Walang placement fee. Sasagot kami sa loob ng isang business day. Demo lang — walang naisusumite.",
      callLabel: "Call tracking · bawat campaign",
      phoneDisplay: "Recruitment hotline",
      phoneHref: "",
      doneTitle: "Nakapasok na.",
      doneBody:
        "Sa totoong build, dito nagpa-fire ang conversion event, dumidiretso sa PH recruitment, at nakukuha ng ad ang credit para sa applicant.",
    } as GateCopy,
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
          <Link href="/" className="ph-nav-link">
            {t.navHub}
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
            <div className="ph-faces anim-rise-d2">
              {faces.map((f) => (
                <figure key={f.src}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={f.src}
                    alt=""
                    className="face-img"
                    style={{ objectPosition: f.pos }}
                  />
                  <figcaption>{f.cap}</figcaption>
                </figure>
              ))}
            </div>
          </div>

          <LeadGate copy={t.gate} />
        </div>
      </section>

      <section className="ph-tracks-sec" id="tracks">
        <div className="ph-tracks-inner">
          <div className="ph-tracks-head">
            <p className="ph-proof-label">{t.tracksLabel}</p>
            <h2>{t.tracksH2}</h2>
          </div>
          <div className="ph-tracks">
            {t.tracks.map((track, i) => (
              <div className="ph-track" key={track.t}>
                <span>{String(i + 1).padStart(2, "0")}</span>
                <strong>{track.t}</strong>
                <p>{track.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="ph-footer">
        <span>{t.foot}</span>
        <Link href="/us">{t.footLink}</Link>
      </footer>
    </main>
  );
}
