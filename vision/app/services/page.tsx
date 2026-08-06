import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import { ServiceIcon } from "../components/MicroIcons";
import { CATEGORY_SLUGS, CATEGORIES } from "../../config/categories";
import type { MarketId } from "../../config/markets";
import type { SiteSurface } from "../../config/site";

export const metadata: Metadata = {
  title: "Roles · Virtual Coworker",
  description:
    "Hire dedicated Philippines staff across marketing, admin, books, support, and more.",
  robots: { index: false, follow: false },
};

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
    <main className="micro">
      <MarketGtm surface={surface} />
      <SiteNav tone="dark" market={surface} active="services" />

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
            Roles · {market === "au" ? "Australia" : "United States"} · Businesses
          </p>
          <h1>
            {market === "au"
              ? "Roles Australian businesses hire through us."
              : "Roles US businesses hire through us."}
          </h1>
          <p className="micro-lead">
            Pick the seat you need filled. Every page is for{" "}
            {market === "au" ? "Australian" : "US"} businesses hiring dedicated
            Philippines staff — job seekers are pointed to careers instead.
          </p>
          <div className="micro-actions">
            <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
              Start hiring
            </Link>
            <Link
              href={`/how-it-works?market=${market}`}
              className="micro-btn micro-btn-ghost"
            >
              How it works
            </Link>
          </div>
        </div>
      </header>

      <section className="micro-section">
        <div className="services-grid">
          {CATEGORY_SLUGS.map((slug) => {
            const c = CATEGORIES[slug];
            return (
              <article className="services-card" key={slug}>
                <span className="micro-icon" aria-hidden>
                  <ServiceIcon slug={slug} />
                </span>
                <em>{c.shortLabel}</em>
                <h2>{c.label}</h2>
                <p>{c.description[market]}</p>
                <div className="services-card-links">
                  <Link href={`/${market}/${slug}`}>Open →</Link>
                </div>
              </article>
            );
          })}
        </div>
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
            Start hiring
          </Link>
        </div>
        <p className="micro-cross">
          Looking for {otherLabel}?{" "}
          <Link href={`/services?market=${other}`}>{otherLabel} services</Link>
        </p>
      </section>

      <SiteFooter tone="dark" market={surface} />
    </main>
  );
}
