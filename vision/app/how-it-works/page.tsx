import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import { HOW_STEP_ICONS } from "../components/MicroIcons";
import type { MarketId } from "../../config/markets";
import type { SiteSurface } from "../../config/site";

export const metadata: Metadata = {
  title: "How it works · Virtual Coworker",
  description:
    "How Virtual Coworker helps you hire dedicated Philippines staff — conversation, brief, interview, onboard.",
  robots: { index: false, follow: false },
};

function resolveMarket(raw: string | string[] | undefined): MarketId {
  const v = Array.isArray(raw) ? raw[0] : raw;
  return v === "au" ? "au" : "us";
}

export default async function HowItWorksPage({
  searchParams,
}: {
  searchParams: Promise<{ market?: string | string[] }>;
}) {
  const params = await searchParams;
  const market = resolveMarket(params.market);
  const surface: SiteSurface = market;
  const home = market === "au" ? "/au" : "/us";
  const isAu = market === "au";

  const steps = isAu
    ? [
        {
          k: "01 · Talk",
          t: "Hiring conversation",
          d: "Tell us the role. We follow up to talk through what you need, Australian business hours, and the skills that matter — so we know it’s a fit before recruiting starts.",
          points: [
            "Short conversation about the seat you need",
            "Clear next steps if we’re a good match",
            "No software demo — this is staffing",
          ],
        },
        {
          k: "02 · Brief",
          t: "We recruit and screen",
          d: "Share your job brief. Our specialised Philippines recruitment team sources and screens candidates against your must-haves.",
          points: [
            "Role brief, not a blank inbox of resumes",
            "Screened against your tools and workflow",
            "Shortlist prepared for your interviews",
          ],
        },
        {
          k: "03 · Choose",
          t: "You interview and decide",
          d: "Review the shortlist, meet people on video, and run any testing you need. Hire only when you’re ready.",
          points: [
            "Video interviews on your schedule",
            "You own the hire decision",
            "Transparent rates discussed with the shortlist",
          ],
        },
        {
          k: "04 · Start",
          t: "Onboard with support",
          d: "Once you hire, we help with onboarding, employment ops, and ongoing check-ins so your new teammate settles in smoothly.",
          points: [
            "Onboarding support from day one",
            "Employment ops handled for you",
            "Ongoing account support while they work",
          ],
        },
      ]
    : [
        {
          k: "01 · Talk",
          t: "Hiring conversation",
          d: "Tell us the role. We follow up to talk through what you need, hours, and tools — so we know it’s a fit before recruiting starts.",
          points: [
            "Short conversation about the seat you need",
            "Clear next steps if we’re a good match",
            "No software demo — this is staffing",
          ],
        },
        {
          k: "02 · Brief",
          t: "We recruit and screen",
          d: "Share your job brief. Our Philippines recruitment team sources and screens candidates against your must-haves.",
          points: [
            "Role brief, not a blank inbox of resumes",
            "Screened against your tools and workflow",
            "Shortlist prepared for your interviews",
          ],
        },
        {
          k: "03 · Choose",
          t: "You interview and decide",
          d: "Review the shortlist, meet people on video, and run any testing you need. Hire only when you’re ready.",
          points: [
            "Video interviews on your schedule",
            "You own the hire decision",
            "Transparent rates discussed with the shortlist",
          ],
        },
        {
          k: "04 · Start",
          t: "Onboard with support",
          d: "Once you hire, we help with onboarding, payroll, and ongoing account support so your new teammate settles in smoothly.",
          points: [
            "Onboarding support from day one",
            "Payroll and employment ops handled",
            "Ongoing account support while they work",
          ],
        },
      ];

  return (
    <main className="micro">
      <MarketGtm surface={surface} />
      <SiteNav tone="dark" market={surface} active="how" />

      <header className={`micro-hero micro-hero--map micro-hero--${market}`}>
        <div className="micro-hero-map" aria-hidden>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/brand/hero-hub-map-b.jpg"
            alt=""
            width={3072}
            height={2048}
            decoding="async"
            fetchPriority="high"
          />
        </div>
        <div className="micro-hero-veil" aria-hidden />
        <div className="micro-hero-copy">
          <p className="micro-kicker">
            {isAu ? "Australia" : "United States"} · Businesses · Philippines talent
          </p>
          <h1>
            {isAu
              ? "How hiring works for Australian businesses."
              : "How hiring works with Virtual Coworker."}
          </h1>
          <p className="micro-lead">
            {isAu
              ? "Four steps. You keep ownership of who joins your team. We recruit, screen, and support dedicated Philippines staff who can work Australian business hours."
              : "Four steps. You keep ownership of who joins your team. We recruit, screen, and support dedicated Philippines staff for US businesses."}
          </p>
          <div className="micro-actions">
            <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
              Start hiring
            </Link>
            <Link
              href={`/services?market=${market}`}
              className="micro-btn micro-btn-ghost"
            >
              Browse roles
            </Link>
          </div>
        </div>
      </header>

      <section className="micro-section">
        <div className="how-steps">
          {steps.map((s, i) => {
            const Icon = HOW_STEP_ICONS[i];
            return (
              <article className="how-step" key={s.k}>
                <span className="micro-icon" aria-hidden>
                  <Icon />
                </span>
                <em>{s.k}</em>
                <h2>{s.t}</h2>
                <p>{s.d}</p>
                <ul>
                  {s.points.map((p) => (
                    <li key={p}>{p}</li>
                  ))}
                </ul>
              </article>
            );
          })}
        </div>
      </section>

      <section className="micro-cta">
        <h2>{isAu ? "Ready to send your role?" : "Ready to tell us who you need?"}</h2>
        <p>
          {isAu
            ? "Start a hiring request for your Australian business. Looking for work? Use the careers link in the footer."
            : "Start a hiring request for your US business. Looking for work? Use the careers link in the footer."}
        </p>
        <div className="micro-actions">
          <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
            Tell us who you need
          </Link>
        </div>
      </section>

      <SiteFooter tone="dark" market={surface} />
    </main>
  );
}
