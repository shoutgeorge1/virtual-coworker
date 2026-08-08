import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import HubMapHero from "../components/HubMapHero";
import JsonLd from "../components/JsonLd";
import ServicesRoleGrid from "../components/ServicesRoleGrid";
import PainGain from "../components/PainGain";
import type { MarketId } from "../../config/markets";
import { PRIMARY_HIRE_CTA } from "../../config/employer-cro";
import type { SiteSurface } from "../../config/site";
import { breadcrumbJsonLd, buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Roles to Hire · Filipino Staff | Virtual Coworker",
  description:
    "Browse dedicated Filipino staffing roles — marketing, admin, bookkeeping, support, HR, sales, and more for US and Australian businesses.",
  path: "/services",
  indexable: true,
});

function resolveMarket(
  raw: string | string[] | undefined
): MarketId {
  const v = Array.isArray(raw) ? raw[0] : raw;
  return v === "au" ? "au" : "us";
}

export default async function ServicesPage({
  searchParams,
}: {
  searchParams: Promise<{ market?: string | string[] }>;
}) {
  const params = await searchParams;
  const market = resolveMarket(params.market);
  const surface: SiteSurface = market;
  const home = market === "au" ? "/au" : "/us";
  const other: MarketId = market === "au" ? "us" : "au";
  const otherLabel = other === "au" ? "Australia" : "United States";

  return (
    <main className={`micro${market === "au" ? " micro-light" : ""}`}>
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Home", path: home },
          { name: "Roles", path: `/services?market=${market}` },
        ])}
      />
      <MarketGtm surface={surface} />
      <SiteNav
        tone={market === "au" ? "light" : "dark"}
        market={surface}
        active="services"
      />

      <HubMapHero market={market}>
        <p className="micro-kicker">
          Roles · {market === "au" ? "Australia" : "United States"} · Businesses
        </p>
        <h1>
          {market === "au"
            ? "Hand off the work slowing your Australian business down."
            : "Hand off the work slowing your US business down."}
        </h1>
        <p className="micro-lead">
          Pick the seat you need filled — admin, books, support, marketing, HR,
          sales, and more. Every page is for{" "}
          {market === "au" ? "Australian" : "US"} businesses hiring dedicated
          Filipino staff. Job seekers choose the job-seeker option in the form.
        </p>
        <div className="micro-actions">
          <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
            {PRIMARY_HIRE_CTA}
          </Link>
          <Link
            href={`/how-it-works?market=${market}`}
            className="micro-btn micro-btn-ghost"
          >
            How it works
          </Link>
        </div>
      </HubMapHero>

      <PainGain market={market} light={market === "au"} ctaHref={`${home}#gate`} />

      <section className="micro-section">
        <ServicesRoleGrid market={market} />
      </section>

      <section className="micro-cta">
        <h2>Not sure which role fits?</h2>
        <p>
          Start on the hiring page and pick the closest option
          {market === "us"
            ? " — or call us if you’d rather talk it through."
            : " — we’ll sort the details with you."}
        </p>
        <div className="micro-actions">
          <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
            {PRIMARY_HIRE_CTA}
          </Link>
        </div>
        <p className="micro-cross">
          Looking for {otherLabel}?{" "}
          <Link href={`/services?market=${other}`}>{otherLabel} services</Link>
        </p>
      </section>

      <SiteFooter
        tone={market === "au" ? "light" : "dark"}
        market={surface}
      />
    </main>
  );
}
