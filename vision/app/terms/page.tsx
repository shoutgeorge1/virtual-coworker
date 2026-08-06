import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import { SITE } from "../../config/site";

export const metadata: Metadata = {
  title: "Terms · Virtual Coworker Hiring Microsite",
  description:
    "Terms pointer for the Virtual Coworker paid hiring microsite.",
  robots: { index: false, follow: false },
};

export default function TermsPage() {
  return (
    <main className="micro micro-legal">
      <SiteNav tone="light" />

      <article className="legal-doc">
        <p className="micro-kicker legal-kicker">Hiring microsite</p>
        <h1>Terms</h1>
        <p>
          This paid hiring microsite is operated for Virtual Coworker employer
          inquiries (US and Australia). It is separate from the main WordPress
          websites.
        </p>
        <p>
          We do <b>not</b> invent a separate commercial terms of service for this
          pilot. For Virtual Coworker’s published Terms &amp; Conditions, see the
          corporate page:
        </p>
        <p>
          <a
            href={SITE.termsCorporate}
            rel="noopener noreferrer"
            target="_blank"
          >
            {SITE.termsCorporate}
          </a>
        </p>
        <h2>What this microsite is for</h2>
        <p>
          Employer hiring inquiries only. Submitting a form is a request for
          follow-up — not a confirmed job order, placement, or contract.
        </p>
        <h2>Privacy</h2>
        <p>
          How this microsite handles inquiry data:{" "}
          <Link href="/privacy">Microsite privacy notice</Link>. Corporate
          privacy policy:{" "}
          <a
            href={SITE.privacyCorporate}
            rel="noopener noreferrer"
            target="_blank"
          >
            {SITE.privacyCorporate}
          </a>
          .
        </p>
        <h2>Contact</h2>
        <p>
          US business line for this pilot:{" "}
          <a href={SITE.usPhoneHref}>{SITE.usPhoneDisplay}</a>. Addresses
          published on the corporate contact page: {SITE.addressUs};{" "}
          {SITE.addressAu}.
        </p>
        <p className="legal-back">
          <Link href="/">← Hiring microsite home</Link>
        </p>
      </article>

      <SiteFooter tone="light" />
    </main>
  );
}
