import Link from "next/link";
import { SITE, type SiteSurface } from "../../config/site";

/**
 * Minimal per-market footer.
 * Working microsite links only · zero WordPress egress · one quiet cross-site line.
 */
export default function SiteFooter({
  tone = "dark",
  market = "us",
  categoryLabel,
}: {
  tone?: "dark" | "light";
  market?: SiteSurface | null;
  categoryLabel?: string | null;
}) {
  const surface: SiteSurface = market ?? "us";
  const isPh = surface === "ph";
  const isAu = surface === "au";
  const isUs = surface === "us";

  const marketLabel = isUs
    ? "United States"
    : isAu
      ? "Australia"
      : "Philippines careers";

  const address = isAu ? SITE.addressAu : isUs ? SITE.addressUs : null;

  const siteLinks = isPh
    ? ([
        { href: "/ph", label: "Careers home" },
        { href: "/ph/apply", label: "Apply" },
        { href: "/privacy", label: "Privacy" },
        { href: "/terms", label: "Terms" },
      ] as const)
    : ([
        { href: `/services?market=${surface}`, label: "Services" },
        { href: `/how-it-works?market=${surface}`, label: "How it works" },
        { href: "/privacy", label: "Privacy" },
        { href: "/terms", label: "Terms" },
      ] as const);

  const cross = isUs
    ? ([
        { href: "/au", label: "Australia" },
        { href: "/ph", label: "Careers" },
      ] as const)
    : isAu
      ? ([
          { href: "/us", label: "United States" },
          { href: "/ph", label: "Careers" },
        ] as const)
      : ([
          { href: "/us", label: "US employers" },
          { href: "/au", label: "AU employers" },
        ] as const);

  return (
    <footer className={`site-footer site-footer-${tone}`}>
      <div className="site-footer-inner">
        <div className="site-footer-top">
          <div className="site-footer-brand-block">
            <p className="site-footer-name">{SITE.name}</p>
            <p className="site-footer-meta">
              {isPh
                ? "Careers for talent — not a business hiring form."
                : SITE.disclaimer}
              {categoryLabel ? ` · ${categoryLabel}` : ""}
            </p>
            <p className="site-footer-market">{marketLabel}</p>
          </div>

          <div className="site-footer-contact">
            {address ? (
              <p className="site-footer-address">
                <span className="site-footer-label">Office</span>
                <span>{address}</span>
              </p>
            ) : null}
            {isUs ? (
              <p className="site-footer-phone">
                <span className="site-footer-label">US business line</span>
                <a href={SITE.usPhoneHref}>{SITE.usPhoneDisplay}</a>
              </p>
            ) : null}
            {isAu ? (
              <p className="site-footer-phone site-footer-phone-muted">
                <span className="site-footer-label">Contact</span>
                <span>Send your role above — we’ll follow up.</span>
              </p>
            ) : null}
          </div>

          <nav className="site-footer-nav" aria-label="Footer">
            {siteLinks.map((item) => (
              <Link key={item.href} href={item.href}>
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="site-footer-bottom">
          <p className="site-footer-cross">
            <span className="site-footer-label">Also</span>
            {cross.map((item, i) => (
              <span key={item.href}>
                {i > 0 ? <span aria-hidden> · </span> : null}
                <Link href={item.href}>{item.label}</Link>
              </span>
            ))}
          </p>
          <p className="site-footer-copy">{SITE.copyright}</p>
        </div>
      </div>
    </footer>
  );
}
