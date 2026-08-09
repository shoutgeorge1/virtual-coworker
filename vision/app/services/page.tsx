import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import HubMapHero from "../components/HubMapHero";
import JsonLd from "../components/JsonLd";
import ServicesRoleGrid from "../components/ServicesRoleGrid";
import PainGain from "../components/PainGain";
import { resolvePhone, type MarketId } from "../../config/markets";
import { primaryHireCta } from "../../config/employer-cro";
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
  const isAu = market === "au";
  const cta = primaryHireCta(market);
  const phone = resolvePhone(market);
  const showPhone = phone.configured && Boolean(phone.href);

  return (
    <main className={`micro${isAu ? " micro-light" : ""}`}>
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Home", path: home },
          { name: "Roles", path: `/services?market=${market}` },
        ])}
      />
      <MarketGtm surface={surface} />
      <SiteNav
        tone={isAu ? "light" : "dark"}
        market={surface}
        active="services"
      />

      <HubMapHero market={market}>
        <p className="micro-kicker">
          Roles · {isAu ? "Australia" : "United States"} · Businesses
        </p>
        <h1>
          {isAu
            ? "Pick the role. We’ll match a dedicated Filipino teammate."
            : "Pick the seat. We’ll match a dedicated Filipino teammate."}
        </h1>
        <p className="micro-lead">
          {isAu
            ? "Admin, books, support, marketing, HR, sales and more. Every page is for Australian businesses hiring dedicated Filipino staff on Australian hours. Job seekers choose the job-seeker option in the form."
            : "Admin, books, support, marketing, HR, sales, and more. Every page is for US businesses hiring dedicated Filipino staff. Job seekers choose the job-seeker option in the form."}
        </p>
        <div className="micro-actions">
          <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
            {cta}
          </Link>
          <Link
            href={`/how-it-works?market=${market}`}
            className="micro-btn micro-btn-ghost"
          >
            How it works
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
        <ServicesRoleGrid market={market} />
      </section>

      <section className="micro-cta">
        <h2>
          {isAu ? "Not sure which role fits?" : "Not sure which seat fits?"}
        </h2>
        <p>
          {isAu
            ? "Take the hiring quiz, or have a chat and we’ll sort it with you."
            : showPhone
              ? "Take the hiring quiz — or call us if you’d rather talk it through."
              : "Take the hiring quiz, or talk to a specialist and we’ll sort it with you."}
        </p>
        <div className="micro-actions">
          <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
            {cta}
          </Link>
        </div>
        <p className="micro-cross">
          Looking for {otherLabel}?{" "}
          <Link href={`/services?market=${other}`}>{otherLabel} services</Link>
        </p>
      </section>

      <SiteFooter
        tone={isAu ? "light" : "dark"}
        market={surface}
      />
    </main>
  );
}
