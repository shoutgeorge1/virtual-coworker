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
import { primaryHireCta } from "../../config/employer-cro";
import type { SiteSurface } from "../../config/site";
import { breadcrumbJsonLd, buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "How Hiring Works | Virtual Coworker",
  description:
    "Free consultation. We recruit and vet in the Philippines. You interview. We handle payroll or employment admin, time tracking, and ongoing support.",
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
  const cta = primaryHireCta(market);

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
        <h1>White-glove hiring. Not a freelancer marketplace.</h1>
        <p className="micro-lead">
          {isAu
            ? "Free consultation. We write the job description with you, recruit and vet in the Philippines, and send profiles with hourly rates. You interview on video. We handle employment admin, time tracking, and stay on after they start."
            : "Free consultation. We write the job description with you, recruit and vet in the Philippines, and send profiles with hourly rates. You interview on video. We handle payroll, HR, time tracking, and stay on after they start."}
        </p>
        <div className="micro-actions">
          <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
            {cta}
          </Link>
          <Link
            href={`/services?market=${market}`}
            className="micro-btn micro-btn-ghost"
          >
            Browse roles
          </Link>
        </div>
        <p className="micro-lead" style={{ marginTop: "1rem" }}>
          <a href={`${home}#role-quiz`}>
            {isAu
              ? "Not sure which role? Take the hiring quiz →"
              : "Not sure which seat? Take the hiring quiz →"}
          </a>
        </p>
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

      <SiteFooter tone={isAu ? "light" : "dark"} market={surface} />
    </main>
  );
}
