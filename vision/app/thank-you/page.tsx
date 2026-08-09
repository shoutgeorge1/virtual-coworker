import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import { type SiteSurface } from "../../config/site";
import { resolvePhone, type MarketId } from "../../config/markets";
import { calendlyUrlForMarket } from "../../lib/calendly";
import ThankYouClient from "./ThankYouClient";

import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Thank you · Virtual Coworker",
  description: "Thanks — we got your hiring request.",
  path: "/thank-you",
  indexable: false,
});

export default async function ThankYouPage({
  searchParams,
}: {
  searchParams: Promise<{ market?: string; sid?: string; eligible?: string }>;
}) {
  const sp = await searchParams;
  const market: SiteSurface =
    sp?.market === "au" ? "au" : sp?.market === "us" ? "us" : "us";
  const sid = sp?.sid || "";
  const conversionEligible = sp?.eligible !== "0";
  const isAu = market === "au";
  const home = isAu ? "/au" : "/us";
  const marketLabel = isAu ? "Australia" : "United States";
  const calendlyUrl =
    market === "us" || market === "au" ? calendlyUrlForMarket(market) : null;
  const phone =
    market === "us" || market === "au"
      ? resolvePhone(market as MarketId)
      : { display: "", href: null, configured: false };
  const showPhone = phone.configured && Boolean(phone.href);

  const steps = [
    {
      k: "01",
      t: "Free hiring consult",
      d: calendlyUrl
        ? isAu
          ? "Book a time below, or wait — a teammate will follow up for a short chat about the role and Australian hours."
          : "Book a time below, or wait — a teammate will follow up about the role and hours."
        : isAu
          ? "A teammate follows up about the role and Australian hours — free, no pressure."
          : "A teammate follows up about the role and hours — free, no pressure.",
    },
    {
      k: "02",
      t: "We recruit. You get the shortlist.",
      d: "Our Philippines team finds and screens people. You get strong candidates handed over — not a pile of random resumes.",
    },
    {
      k: "03",
      t: "You pick who you want",
      d: "Meet them on video. Screen who you like. These candidates are that good — you’re going to find someone fast.",
    },
    {
      k: "04",
      t: "Forget the paperwork",
      d: isAu
        ? "Onboarding, employment admin, emails — we handle it. Teammate ready to work Australian hours. You’re sorted."
        : "Onboarding, payroll, emails — we handle it. Gift-wrapped teammate, on your desk, ready to go.",
    },
  ];

  return (
    <main
      className={`micro thank-you thank-you-${market}${isAu ? " micro-light" : ""}`}
    >
      <MarketGtm surface={market} />
      <SiteNav tone={isAu ? "light" : "dark"} market={market} />

      <div className="thank-you-atmosphere" aria-hidden>
        <span className="thank-you-orb thank-you-orb-a" />
        <span className="thank-you-orb thank-you-orb-b" />
        <span className="thank-you-grid" />
      </div>

      <header className="thank-you-hero">
        <div className="thank-you-hero-glow" aria-hidden />
        <p className="micro-kicker">Virtual Coworker · {marketLabel}</p>
        <h1>
          {conversionEligible
            ? isAu
              ? "Thanks — we’ve got your request."
              : "Thanks — you’re in."
            : "Thanks — this was a test submission."}
        </h1>
        {conversionEligible ? (
          <p className="micro-lead thank-you-lead">
            {isAu
              ? "A teammate will follow up for a short chat about the role and Australian hours. Free, no pressure."
              : "A teammate will follow up to talk through the role and next steps. Free consult, no pressure."}
          </p>
        ) : (
          <p className="micro-lead thank-you-lead">
            Our hiring team was not notified. If you meant to send a real
            request, please try again from the hiring page — or contact us if
            something looks wrong.
          </p>
        )}
        {sid ? (
          <p className="thank-you-ref">
            Reference <code>{sid}</code>
          </p>
        ) : null}
      </header>

      {conversionEligible && calendlyUrl ? (
        <section
          className="thank-you-book"
          aria-labelledby="ty-book"
        >
          <div className="thank-you-book-inner">
            <p className="thank-you-book-eyebrow">Optional next step</p>
            <h2 id="ty-book">
              {isAu
                ? "Want to talk sooner? Book a time"
                : "Want to move faster? Book a hiring conversation"}
            </h2>
            <p>
              {isAu
                ? "Optional — pick a time that suits Australian business hours. Or skip booking and wait for email follow-up. Still free, no lock-in."
                : "Optional — pick a time that works for you. Or skip booking and wait for email follow-up. Still free, no obligation."}
            </p>
            <div className="thank-you-book-actions">
              <a
                href={calendlyUrl}
                className="micro-btn micro-btn-primary thank-you-book-primary"
                target="_blank"
                rel="noopener noreferrer"
                data-track="calendly_cta_clicked"
              >
                Schedule a call
              </a>
              {showPhone ? (
                <a
                  href={phone.href!}
                  className="micro-btn micro-btn-ghost"
                  data-track="phone_cta_clicked"
                >
                  Or call {phone.display}
                </a>
              ) : null}
            </div>
            <p className="thank-you-book-note">
              Prefer email follow-up? No need to book — we’ll reach out from your
              request.
            </p>
          </div>
        </section>
      ) : null}

      {conversionEligible ? (
        <section className="micro-section thank-you-next" aria-labelledby="ty-next">
          <h2 id="ty-next" className="thank-you-section-title">
            What happens next
          </h2>
          <ol className="thank-you-steps">
            {steps.map((s) => (
              <li key={s.k} className="thank-you-step">
                <em>{s.k}</em>
                <h3>{s.t}</h3>
                <p>{s.d}</p>
              </li>
            ))}
          </ol>
        </section>
      ) : null}

      <section className="thank-you-aside" aria-labelledby="ty-help">
        <div className="thank-you-aside-inner">
          {conversionEligible ? (
            <>
              <h2 id="ty-help">While you wait</h2>
              <p>
                {calendlyUrl
                  ? showPhone
                    ? "Browse how hiring works, explore role categories, or call the business line if you’d rather talk sooner."
                    : "Browse how hiring works or explore role categories — useful context before your conversation."
                  : showPhone
                    ? "Calendar booking link coming from Virtual Coworker — we’ll reach out directly. Prefer a call first? Use the business line below."
                    : isAu
                      ? "Calendar booking link coming from Virtual Coworker — a teammate will follow up directly to talk through the role."
                      : "Calendar booking link coming from Virtual Coworker — we’ll reach out directly."}
              </p>
            </>
          ) : (
            <>
              <h2 id="ty-help">Need help?</h2>
              <p>Return to the hiring page and send a real request, or call us.</p>
            </>
          )}

          <nav className="thank-you-links" aria-label="Helpful links">
            <Link href={`/how-it-works?market=${market}`}>How it works</Link>
            <Link href={`/services?market=${market}`}>Role categories</Link>
            <Link href={home}>{isAu ? "Australia home" : "United States home"}</Link>
            {showPhone ? (
              <a href={phone.href!} data-track="phone_cta_clicked">
                Call {phone.display}
              </a>
            ) : null}
            <Link href="/privacy">Privacy</Link>
          </nav>

          {!calendlyUrl && conversionEligible ? (
            <div className="micro-actions thank-you-placeholder-cta">
              <span
                className="micro-btn micro-btn-primary"
                aria-disabled="true"
                title="Booking link pending from Virtual Coworker"
              >
                Book a hiring conversation — link coming from Virtual Coworker
              </span>
              {showPhone ? (
                <a
                  href={phone.href!}
                  className="micro-btn micro-btn-ghost"
                  data-track="phone_cta_clicked"
                >
                  Call {phone.display}
                </a>
              ) : null}
            </div>
          ) : null}

          {!conversionEligible ? (
            <div className="micro-actions">
              {showPhone ? (
                <a
                  href={phone.href!}
                  className="micro-btn micro-btn-primary"
                  data-track="phone_cta_clicked"
                >
                  Call {phone.display}
                </a>
              ) : null}
              <Link href={home} className="micro-btn micro-btn-ghost">
                {isAu ? "Back to Australia" : "Back to United States"}
              </Link>
            </div>
          ) : null}

          <p className="thank-you-legal">
            <Link href="/privacy">Privacy</Link>
            {" · "}
            <Link href="/terms">Terms</Link>
          </p>
        </div>
      </section>

      <ThankYouClient
        market={market}
        submissionId={sid}
        conversionEligible={conversionEligible}
      />

      <SiteFooter tone={isAu ? "light" : "dark"} market={market} />
    </main>
  );
}
