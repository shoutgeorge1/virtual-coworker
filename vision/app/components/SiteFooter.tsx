import Link from "next/link";
import { SITE, type SiteSurface } from "../../config/site";
import {
  isExternalCareersUrl,
  resolveCareersUrl,
} from "../../config/markets";

/**
 * Minimal per-market footer.
 * Employer pages stay on-host except intentional job-seeker egress → PH WordPress.
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
  const careers = resolveCareersUrl();
  const careersExternal = isExternalCareersUrl(careers);

  const marketLabel = isUs
    ? "United States"
    : isAu
      ? "Australia"
      : "Philippines careers";

  const address = isAu ? SITE.addressAu : isUs ? SITE.addressUs : null;

  const siteLinks = isPh
    ? ([
        { href: careers, label: "Philippines careers", external: careersExternal },
        { href: "/privacy", label: "Privacy", external: false },
        { href: "/terms", label: "Terms", external: false },
      ] as const)
    : ([
        { href: `/services?market=${surface}`, label: "Services", external: false },
        {
          href: `/how-it-works?market=${surface}`,
          label: "How it works",
          external: false,
        },
        { href: "/privacy", label: "Privacy", external: false },
        { href: "/terms", label: "Terms", external: false },
      ] as const);

  const cross = isUs
    ? ([
        { href: "/au", label: "Australia", external: false },
        {
          href: careers,
          label: "Looking for a job?",
          external: careersExternal,
        },
      ] as const)
    : isAu
      ? ([
          { href: "/us", label: "United States", external: false },
          {
            href: careers,
            label: "Looking for a job?",
            external: careersExternal,
          },
        ] as const)
      : ([
          { href: "/us", label: "US employers", external: false },
          { href: "/au", label: "AU employers", external: false },
        ] as const);

  const renderLink = (
    item: { href: string; label: string; external?: boolean },
    key: string,
  ) => {
    if (item.external) {
      return (
        <a
          key={key}
          href={item.href}
          target="_blank"
          rel="noopener noreferrer"
        >
          {item.label}
        </a>
      );
    }
    return (
      <Link key={key} href={item.href}>
        {item.label}
      </Link>
    );
  };

  return (
    <footer className={`site-footer site-footer-${tone}`}>
      <div className="site-footer-inner">
        <div className="site-footer-top">
          <div className="site-footer-brand-block">
            <p className="site-footer-name">{SITE.name}</p>
            <p className="site-footer-meta">
              {isPh
                ? "Careers for talent — continue on our Philippines careers site."
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
            {siteLinks.map((item) => renderLink(item, item.href + item.label))}
          </nav>
        </div>

        <div className="site-footer-bottom">
          <p className="site-footer-cross">
            <span className="site-footer-label">Also:</span>{" "}
            {cross.map((item, i) => (
              <span key={item.href + item.label}>
                {i > 0 ? <span aria-hidden> · </span> : null}
                {renderLink(item, `cross-${item.href}`)}
              </span>
            ))}
          </p>
          <p className="site-footer-copy">{SITE.copyright}</p>
        </div>
      </div>
    </footer>
  );
}
