import Link from "next/link";
import { SITE } from "../../config/site";
import type { MarketId } from "../../config/markets";

export default function SiteFooter({
  tone = "dark",
  market,
  categoryLabel,
}: {
  tone?: "dark" | "light";
  market?: MarketId | null;
  categoryLabel?: string | null;
}) {
  const marketLabel =
    market === "us" ? "United States" : market === "au" ? "Australia" : null;

  return (
    <footer className={`site-footer site-footer-${tone}`}>
      <div className="site-footer-inner">
        <div className="site-footer-main">
          <p className="site-footer-brand">
            <b>{SITE.name}</b>
            <span>
              {SITE.disclaimer}
              {marketLabel ? ` · ${marketLabel}` : ""}
              {categoryLabel ? ` · ${categoryLabel}` : ""}
            </span>
          </p>
          <p className="site-footer-address">
            <span>{SITE.addressUs}</span>
            <span>{SITE.addressAu}</span>
          </p>
          <p className="site-footer-phone">
            US business line:{" "}
            <a href={SITE.usPhoneHref}>{SITE.usPhoneDisplay}</a>
          </p>
        </div>

        <nav className="site-footer-links" aria-label="Legal and site">
          <Link href="/privacy">Privacy</Link>
          <Link href="/terms">Terms</Link>
          <a href={SITE.privacyCorporate} rel="noopener noreferrer" target="_blank">
            Corporate privacy
          </a>
          <a href={SITE.termsCorporate} rel="noopener noreferrer" target="_blank">
            Corporate terms
          </a>
          <a href={SITE.corporateUrl} rel="noopener noreferrer" target="_blank">
            virtualcoworker.com
          </a>
          <Link href="/services">Services</Link>
          <Link href="/how-it-works">How it works</Link>
          <Link href="/ph">Careers (PH)</Link>
        </nav>

        <p className="site-footer-copy">{SITE.copyright}</p>
      </div>
    </footer>
  );
}
