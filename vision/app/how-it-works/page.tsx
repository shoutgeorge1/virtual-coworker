import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import HubMapHero from "../components/HubMapHero";
import JsonLd from "../components/JsonLd";
import { HOW_STEP_ICONS } from "../components/MicroIcons";
import type { MarketId } from "../../config/markets";
import { hiringProcessSteps } from "../../config/hiring-process";
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
    <main className="micro">
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Home", path: home },
          { name: "How it works", path: `/how-it-works?market=${market}` },
        ])}
      />
      <MarketGtm surface={surface} />
      <SiteNav tone="dark" market={surface} active="how" />

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
            ? "Four steps. You keep ownership of who joins your team. We recruit, screen, and support dedicated Filipino staff who can work Australian business hours."
            : "Four steps. You keep ownership of who joins your team. We recruit, screen, and support dedicated Filipino staff for US businesses."}
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
      </HubMapHero>

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
        <h2>{isAu ? "Ready to send your role?" : "Ready to tell us who you need?"}</h2>
        <p>
          {isAu
            ? "Start a hiring request for your Australian business. Looking for work? Use Looking for a job? in the footer."
            : "Start a hiring request for your US business. Looking for work? Use Looking for a job? in the footer."}
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
