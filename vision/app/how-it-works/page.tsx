import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import HubMapHero from "../components/HubMapHero";
import JsonLd from "../components/JsonLd";
import PainGain from "../components/PainGain";
import { HOW_STEP_ICONS } from "../components/MicroIcons";
import type { MarketId } from "../../config/markets";
import { hiringProcessSteps } from "../../config/hiring-process";
import { PRIMARY_HIRE_CTA } from "../../config/employer-cro";
import type { SiteSurface } from "../../config/site";
import { breadcrumbJsonLd, buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "How Hiring Works | Virtual Coworker",
  description:
    "How Virtual Coworker helps US and Australian businesses hire dedicated Filipino staff — conversation, brief, interview, onboard.",
  path: "/how-it-works",
  indexable: true,
});

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
  const steps = hiringProcessSteps(market);

  return (
    <main className={`micro${isAu ? " micro-light" : ""}`}>
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Home", path: home },
          { name: "How it works", path: `/how-it-works?market=${market}` },
        ])}
      />
      <MarketGtm surface={surface} />
      <SiteNav
        tone={isAu ? "light" : "dark"}
        market={surface}
        active="how"
      />

      <HubMapHero market={market}>
        <p className="micro-kicker">
          {isAu ? "Australia" : "United States"} · Businesses · Filipino talent
        </p>
        <h1>
          {isAu
            ? "How hiring works for Australian businesses."
            : "How hiring works with Virtual Coworker."}
        </h1>
        <p className="micro-lead">
          {isAu
            ? "Four clear steps. Tell us what you need, we identify suitable Filipino candidates, you interview and choose, and we support onboarding and employment admin afterward — including Australian business hours."
            : "Four clear steps. Tell us what you need, we identify suitable Filipino candidates, you interview and choose, and we support onboarding, payroll, and the ongoing relationship."}
        </p>
        <div className="micro-actions">
          <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
            {PRIMARY_HIRE_CTA}
          </Link>
          <Link
            href={`/services?market=${market}`}
            className="micro-btn micro-btn-ghost"
          >
            Browse roles
          </Link>
        </div>
      </HubMapHero>

      <PainGain market={market} light={isAu} ctaHref={`${home}#gate`} />

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
              </article>
            );
          })}
        </div>
      </section>

      <section className="micro-cta">
        <h2>Ready to free your team from work that keeps slipping?</h2>
        <p>
          {isAu
            ? "Start a hiring request for your Australian business. Looking for work? Choose the job-seeker option in the form."
            : "Start a hiring request for your US business. Looking for work? Choose the job-seeker option in the form."}
        </p>
        <div className="micro-actions">
          <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
            {PRIMARY_HIRE_CTA}
          </Link>
        </div>
      </section>

      <SiteFooter tone={isAu ? "light" : "dark"} market={surface} />
    </main>
  );
}
