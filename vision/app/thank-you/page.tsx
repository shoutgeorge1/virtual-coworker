import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import { type SiteSurface } from "../../config/site";
import { resolvePhone, type MarketId } from "../../config/markets";
import { hiringProcessStrip } from "../../config/hiring-process";
import {
  calendlyEmbedDomain,
  calendlyPopupUrl,
  calendlyUrlForMarket,
  shouldCalendlyAutoOpen,
  THANK_YOU_BOOKING_COPY,
} from "../../lib/calendly";
import CalendlyPopup from "./CalendlyPopup";
import ThankYouClient from "./ThankYouClient";

import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Thank you · Virtual Coworker",
  description: "Thanks - we got your hiring request.",
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
  const calendlyWidgetUrl = calendlyUrl
    ? calendlyPopupUrl(calendlyUrl, { embedDomain: calendlyEmbedDomain() })
    : null;
  const phone =
    market === "us" || market === "au"
      ? resolvePhone(market as MarketId)
      : { display: "", href: null, configured: false };
  const showPhone = phone.configured && Boolean(phone.href);
  const showBook = Boolean(calendlyUrl && calendlyWidgetUrl);
  const bookingCopy = isAu ? THANK_YOU_BOOKING_COPY.au : THANK_YOU_BOOKING_COPY.us;

  const process = hiringProcessStrip(market === "au" || market === "us" ? market : "us");
  const steps = [
    {
      k: "01",
      t: "Free consultation",
      d: calendlyUrl
        ? isAu
          ? "A member of our team will follow up about the role and Australian hours. You can also pick a time, or call."
          : "A member of our team will call you about the role and hours. You can also pick a time, or call."
        : isAu
          ? "A member of our team follows up about the role and Australian hours. Obligation free, at no cost."
          : "A member of our team will call you about the role and hours. Obligation free, at no cost.",
    },
    ...process.slice(1),
  ];

  return (
    <main
      className={`micro thank-you thank-you-${market}${isAu ? " micro-light" : ""}`}
      {...(sid ? { "data-submission-id": sid } : {})}
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
              ? "Thanks - we’ve got your request."
              : "Thanks - you’re in."
            : "Thanks - this was a test submission."}
        </h1>
        {conversionEligible ? (
          <p className="micro-lead thank-you-lead">
            {isAu
              ? "A member of our team will follow up for a short chat about the role and Australian hours. Obligation free, at no cost."
              : "A member of our team will call you to talk through the role and next steps. Obligation free, at no cost."}
          </p>
        ) : (
          <p className="micro-lead thank-you-lead">
            Our hiring team was not notified. If you meant to send a real
            request, please try again from the hiring page - or contact us if
            something looks wrong.
          </p>
        )}
      </header>

      {conversionEligible && (showPhone || showBook) ? (
        <section className="thank-you-book" aria-labelledby="ty-book">
          <div className="thank-you-book-inner">
            <p className="thank-you-book-eyebrow">
              {showBook
                ? bookingCopy.eyebrow
                : showPhone
                  ? "Talk now"
                  : "Hiring chat"}
            </p>
            <h2 id="ty-book">
              {showBook
                ? bookingCopy.headline
                : isAu
                  ? "Prefer to talk now?"
                  : "Want to talk now?"}
            </h2>
            <p>
              {showBook
                ? bookingCopy.sub
                : "Call the business line. Obligation free, at no cost."}
            </p>
            {showPhone && showBook ? (
              <p className="thank-you-book-note">{bookingCopy.micro}</p>
            ) : null}
            {showPhone || showBook ? (
              <div className="thank-you-book-actions">
                {showBook && calendlyUrl && calendlyWidgetUrl ? (
                  <CalendlyPopup
                    widgetUrl={calendlyWidgetUrl}
                    bookUrl={calendlyUrl}
                    market={market}
                    label="Schedule a call"
                    autoOpen={shouldCalendlyAutoOpen(conversionEligible)}
                    phoneDisplay={phone.display}
                    phoneHref={phone.href}
                  />
                ) : null}
                {showPhone ? (
                  <a
                    href={phone.href!}
                    className={`micro-btn ${showBook ? "micro-btn-ghost thank-you-book-secondary" : "micro-btn-primary thank-you-book-primary"}`}
                    data-track="phone_cta_clicked"
                  >
                    Call {phone.display}
                  </a>
                ) : null}
              </div>
            ) : null}
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
              <h2 id="ty-help">More about hiring</h2>
              <p>
                {calendlyUrl
                  ? showPhone
                    ? "Browse how hiring works or explore role categories. Prefer a call? Use the business line."
                    : "Browse how hiring works or explore role categories - useful context before your conversation."
                  : showPhone
                    ? "Calendar booking link coming from Virtual Coworker - we’ll reach out directly. Prefer a call first? Use the business line below."
                    : isAu
                      ? "Calendar booking link coming from Virtual Coworker - a member of our team will follow up directly to talk through the role."
                      : "Calendar booking link coming from Virtual Coworker - we’ll reach out directly."}
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
              {showPhone ? (
                <a
                  href={phone.href!}
                  className="micro-btn micro-btn-primary"
                  data-track="phone_cta_clicked"
                >
                  Call {phone.display}
                </a>
              ) : (
                <span
                  className="micro-btn micro-btn-primary"
                  aria-disabled="true"
                  title="Booking link pending from Virtual Coworker"
                >
                  Book a hiring chat - link coming from Virtual Coworker
                </span>
              )}
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
