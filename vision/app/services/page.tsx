import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import { CATEGORY_SLUGS, CATEGORIES } from "../../config/categories";

export const metadata: Metadata = {
  title: "Services · Virtual Coworker Hiring",
  description:
    "Employer service lines for hiring dedicated Philippines staff — US and Australia.",
  robots: { index: false, follow: false },
};

export default function ServicesPage() {
  return (
    <main className="micro">
      <SiteNav tone="dark" active="services" />

      <header className="micro-hero">
        <p className="micro-kicker">Services · Employers</p>
        <h1>Nine roles. One employer hiring path.</h1>
        <p className="micro-lead">
          Pick the seat you need filled. Each page is built for US or Australian
          employers hiring dedicated Philippines staff — with an employer gate so
          job seekers don’t land in the form.
        </p>
        <div className="micro-actions">
          <Link href="/us" className="micro-btn micro-btn-primary">
            US hiring hub
          </Link>
          <Link href="/au" className="micro-btn micro-btn-ghost">
            Australia hiring hub
          </Link>
        </div>
      </header>

      <section className="micro-section">
        <div className="services-grid">
          {CATEGORY_SLUGS.map((slug) => {
            const c = CATEGORIES[slug];
            return (
              <article className="services-card" key={slug}>
                <em>{c.shortLabel}</em>
                <h2>{c.label}</h2>
                <p>{c.description.us}</p>
                <div className="services-card-links">
                  <Link href={`/us/${slug}`}>US →</Link>
                  <Link href={`/au/${slug}`}>AU →</Link>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className="micro-cta">
        <h2>Not sure which label fits?</h2>
        <p>
          Start on the market hub and pick the closest role in the form — or call
          the US business line from any US page.
        </p>
        <div className="micro-actions">
          <Link href="/how-it-works" className="micro-btn micro-btn-ghost">
            How it works
          </Link>
          <Link href="/us#gate" className="micro-btn micro-btn-primary">
            Start hiring
          </Link>
        </div>
      </section>

      <SiteFooter tone="dark" />
    </main>
  );
}
