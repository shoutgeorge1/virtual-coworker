import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import { SITE, type SiteSurface } from "../../config/site";
import ThankYouClient from "./ThankYouClient";

export const metadata: Metadata = {
  title: "Thank you · Virtual Coworker",
  description: "Thanks — we got your hiring request.",
  robots: { index: false, follow: false },
};

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

  const steps = [
    {
      k: "01",
      t: "Hiring conversation",
      d: isAu
        ? "A teammate follows up to talk through the role, Australian business hours, and whether we’re a fit."
        : "A teammate follows up to talk through the role, hours, tools, and whether we’re a fit.",
    },
    {
      k: "02",
      t: "Brief → we recruit",
      d: "Share the brief. We source and screen dedicated Philippines talent against your must-haves.",
    },
    {
      k: "03",
      t: "You interview",
      d: "Meet the shortlist on video. You decide who joins — no pressure hire.",
    },
    {
      k: "04",
      t: "Onboard with support",
      d: "Once you hire, we help with onboarding and ongoing support so your new teammate settles in.",
    },
  ];

  return (
    <main className={`micro thank-you thank-you-${market}`}>
      <MarketGtm surface={market} />
      <SiteNav tone="dark" market={market} />

      <header className="thank-you-hero">
        <div className="thank-you-hero-glow" aria-hidden />
        <p className="micro-kicker">
          Virtual Coworker · {marketLabel}
        </p>
        <h1>
          {conversionEligible
            ? isAu
              ? "Thanks — we got your request."
              : "Thanks — we got your request."
            : "Thanks — this was a test submission."}
        </h1>
        {conversionEligible ? (
          <p className="micro-lead thank-you-lead">
            {isAu
              ? "A teammate will follow up to talk through the role and next steps for your Australian business. This is a hiring conversation — not a software demo."
              : "A teammate will follow up to talk through the role and next steps for your US business. This is a hiring conversation — not a software demo."}
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

      <section className="thank-you-aside">
        <div className="thank-you-aside-inner">
          {conversionEligible ? (
            <>
              <h2>While you wait</h2>
              <p>
                {isAu
                  ? "No calendar booking on this page yet — a teammate will follow up directly to talk through the role."
                  : "No calendar booking on this page yet — we’ll reach out directly. Prefer a call first? Use the US business line below."}
              </p>
            </>
          ) : (
            <>
              <h2>Need help?</h2>
              <p>Return to the hiring page and send a real request, or call us.</p>
            </>
          )}
          <div className="micro-actions">
            {!isAu ? (
              <a
                href={SITE.usPhoneHref}
                className="micro-btn micro-btn-primary"
                data-track="phone_cta_clicked"
              >
                Call {SITE.usPhoneDisplay}
              </a>
            ) : null}
            <Link href={home} className="micro-btn micro-btn-ghost">
              {isAu ? "Back to Australia" : "Back to United States"}
            </Link>
            <Link
              href={`/how-it-works?market=${market}`}
              className="micro-btn micro-btn-ghost"
            >
              How hiring works
            </Link>
          </div>
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

      <SiteFooter tone="dark" market={market} />
    </main>
  );
}
