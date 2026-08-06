import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import { SITE } from "../../config/site";

export const metadata: Metadata = {
  title: "Terms · Virtual Coworker Hiring Microsite",
  description:
    "Terms for the Virtual Coworker paid hiring microsite.",
  robots: { index: false, follow: false },
};

export default function TermsPage() {
  return (
    <main className="micro micro-legal">
      <MarketGtm surface="us" />
      <SiteNav tone="light" market="us" />

      <article className="legal-doc">
        <p className="micro-kicker legal-kicker">Hiring microsite</p>
        <h1>Terms</h1>
        <p>
          This paid hiring microsite is operated for Virtual Coworker employer
          inquiries (US and Australia) and a separate Philippines careers path.
          It is independent of the main WordPress websites. Paid traffic stays on
          this microsite — we do not deep-link WordPress from these pages.
        </p>
        <h2>What this microsite is for</h2>
        <p>
          Employer hiring inquiries on US/AU pages. Submitting a form is a
          request for follow-up — not a confirmed job order, placement, or
          contract. The Philippines path is for talent applications only.
        </p>
        <h2>Privacy</h2>
        <p>
          How this microsite handles inquiry data:{" "}
          <Link href="/privacy">Microsite privacy notice</Link>.
        </p>
        <h2>Contact</h2>
        <p>
          US business line for this pilot:{" "}
          <a href={SITE.usPhoneHref}>{SITE.usPhoneDisplay}</a>. Offices listed on
          this microsite: {SITE.addressUs}; {SITE.addressAu}.
        </p>
        <p className="legal-back">
          <Link href="/us">← US hiring home</Link>
          {" · "}
          <Link href="/privacy">Privacy</Link>
        </p>
      </article>

      <SiteFooter tone="light" market="us" />
    </main>
  );
}
