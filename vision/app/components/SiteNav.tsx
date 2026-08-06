import Link from "next/link";
import { NAV, SITE, type NavId } from "../../config/site";
import { resolvePhone, type MarketId } from "../../config/markets";

export default function SiteNav({
  tone = "dark",
  market,
  active,
}: {
  tone?: "dark" | "light";
  market?: MarketId | null;
  active?: NavId | null;
}) {
  const phone = market ? resolvePhone(market) : resolvePhone("us");
  const showPhone = phone.configured && Boolean(phone.href);
  const hireHref = market === "au" ? "/au#gate" : "/us#gate";

  return (
    <nav className={`site-nav site-nav-${tone}`} aria-label="Primary">
      <Link href="/" className="site-nav-brand">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/brand/logo-vc.png"
          alt="Virtual Coworker"
          className={tone === "dark" ? "logo-img logo-img-on-dark" : "logo-img"}
        />
      </Link>

      <div className="site-nav-links">
        {NAV.map((item) => {
          const href = item.id === "hire" ? hireHref : item.href;
          const isActive =
            active === item.id ||
            (item.id === "us" && market === "us") ||
            (item.id === "au" && market === "au");
          return (
            <Link
              key={item.id}
              href={href}
              className={`site-nav-link${
                "primary" in item && item.primary ? " site-nav-link-primary" : ""
              }${isActive ? " is-active" : ""}`}
            >
              {item.label}
            </Link>
          );
        })}
      </div>

      <div className="site-nav-right">
        {showPhone ? (
          <a
            href={phone.href!}
            className="site-nav-call"
            data-track="phone_cta_clicked"
          >
            <span aria-hidden>☎</span> {phone.display}
          </a>
        ) : (
          <a href={hireHref} className="site-nav-call">
            Start hiring
          </a>
        )}
        <span className="site-nav-tag">{SITE.tagline}</span>
      </div>
    </nav>
  );
}
