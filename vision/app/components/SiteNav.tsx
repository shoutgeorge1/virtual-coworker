import Link from "next/link";
import {
  SITE,
  homeForSurface,
  navForSurface,
  type NavId,
  type SiteSurface,
} from "../../config/site";
import { primaryHireCta } from "../../config/employer-cro";
import { resolvePhone, type MarketId } from "../../config/markets";

export default function SiteNav({
  tone = "dark",
  market = "us",
  active,
}: {
  tone?: "dark" | "light";
  /** Employer market or PH talent surface — scopes logo + nav. */
  market?: SiteSurface;
  active?: NavId | null;
}) {
  const surface: SiteSurface = market ?? "us";
  const items = navForSurface(surface);
  const home = homeForSurface(surface);
  const employerMarket: MarketId | null =
    surface === "us" || surface === "au" ? surface : null;
  const phone = employerMarket ? resolvePhone(employerMarket) : null;
  const showPhone = Boolean(phone?.configured && phone.href);
  const hireHref =
    surface === "au" ? "/au#gate" : surface === "ph" ? "/ph/apply" : "/us#gate";
  // Employer nav already includes Free consultation → #gate. Without a phone, the
  // right-slot CTA was a second identical link (AU desktop + mobile).
  const hireAlreadyInNav = items.some((item) => item.id === "hire");

  return (
    <nav className={`site-nav site-nav-${tone}`} aria-label="Primary">
      <Link href={home} className="site-nav-brand">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/brand/logo-vc.png"
          alt="Virtual Coworker"
          className={tone === "dark" ? "logo-img logo-img-on-dark" : "logo-img"}
        />
      </Link>

      <div className="site-nav-links">
        {items.map((item) => {
          const isActive = active === item.id;
          return (
            <Link
              key={item.id}
              href={item.href}
              className={`site-nav-link${
                item.primary ? " site-nav-link-primary" : ""
              }${isActive ? " is-active" : ""}`}
            >
              {item.label}
            </Link>
          );
        })}
      </div>

      <div className="site-nav-right">
        {showPhone && phone?.href ? (
          <a
            href={phone.href}
            className="site-nav-call"
            data-track="phone_cta_clicked"
            data-cta-location="header"
          >
            <span aria-hidden>☎</span> {phone.display}
          </a>
        ) : surface === "ph" ? (
          <Link href="/ph/apply" className="site-nav-call">
            Apply
          </Link>
        ) : !hireAlreadyInNav ? (
          <a href={hireHref} className="site-nav-call">
            {employerMarket ? primaryHireCta(employerMarket) : "Book a Free Strategy Call"}
          </a>
        ) : null}
        <span className="site-nav-tag">{SITE.tagline}</span>
      </div>
    </nav>
  );
}
