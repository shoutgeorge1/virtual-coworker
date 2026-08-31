import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "./SiteNav";
import SiteFooter from "./SiteFooter";
import BookCalendlyEmbed from "./BookCalendlyEmbed";
import BookPageClient from "./BookPageClient";
import {
  calendlyEmbedDomain,
  calendlyPopupUrl,
  calendlyUrlForMarket,
} from "../../lib/calendly";
import { buildPageMetadata } from "../../lib/seo";
import {
  resolveCareersUrl,
  resolvePhone,
  type MarketId,
} from "../../config/markets";

export function bookPageMetadata(market: MarketId): Metadata {
  const isAu = market === "au";
  const path = isAu ? "/au/book" : "/us/book";
  return buildPageMetadata({
    title: isAu
      ? "Book an Employer Consultation | Virtual Coworker Australia"
      : "Book an Employer Consultation | Virtual Coworker",
    description:
      "Book a free consultation to hire remote staff through Virtual Coworker. Tell us about the role and choose a time with our staffing team.",
    path,
    indexable: true,
  });
}

export default function EmployerBookPage({ market }: { market: MarketId }) {
  const isAu = market === "au";
  const home = isAu ? "/au" : "/us";
  const marketLabel = isAu ? "Australia" : "United States";
  const calendlyUrl = calendlyUrlForMarket(market);
  const widgetUrl = calendlyUrl
    ? calendlyPopupUrl(calendlyUrl, { embedDomain: calendlyEmbedDomain() })
    : null;
  const phone = resolvePhone(market);
  const showPhone = phone.configured && Boolean(phone.href);

  if (!calendlyUrl || !widgetUrl) {
    throw new Error(
      `Missing Calendly URL for market "${market}". Set NEXT_PUBLIC_CALENDLY_${market.toUpperCase()} or corporate defaults in lib/calendly.ts.`,
    );
  }

  return (
    <main className={`micro micro-light book-page book-page-${market}`}>
      <SiteNav tone="light" market={market} />
      <BookPageClient market={market} />

      <header className="book-hero">
        <p className="micro-kicker">
          Virtual Coworker · {marketLabel} · Employers
        </p>
        <h1>Book an Employer Consultation</h1>
        <p className="micro-lead">
          Tell us about the role you need to fill and choose a convenient time
          to speak with our staffing team.
        </p>
        <p className="book-employer-note">
          This consultation is for businesses interested in hiring remote
          staff. Looking for work?{" "}
          <a href={resolveCareersUrl()}>Visit our careers site</a>.
        </p>
        {showPhone ? (
          <p className="book-phone-alt">
            Prefer to talk now?{" "}
            <a href={phone.href!} data-track="phone_cta_clicked">
              Call {phone.display}
            </a>
          </p>
        ) : null}
      </header>

      <section className="book-embed-section" aria-label="Scheduling calendar">
        <BookCalendlyEmbed
          market={market}
          widgetUrl={widgetUrl}
          bookUrl={calendlyUrl}
        />
      </section>

      <p className="book-home-link">
        <Link href={home}>
          {isAu ? "Back to Australia hiring" : "Back to United States hiring"}
        </Link>
      </p>

      <SiteFooter tone="light" market={market} />
    </main>
  );
}
