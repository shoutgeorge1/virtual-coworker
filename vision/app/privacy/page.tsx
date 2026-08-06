import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import { SITE } from "../../config/site";

export const metadata: Metadata = {
  title: "Privacy · Virtual Coworker Hiring Microsite",
  description:
    "Privacy notice for the Virtual Coworker paid hiring microsite.",
  robots: { index: false, follow: false },
};

export default function PrivacyPage() {
  return (
    <main className="micro micro-legal">
      <MarketGtm surface="us" />
      <SiteNav tone="light" market="us" />

      <article className="legal-doc">
        <p className="micro-kicker legal-kicker">Hiring microsite</p>
        <h1>Privacy</h1>
        <p>
          This notice covers the independent paid hiring microsite (US and
          Australia employer pages, Philippines careers path, services, and
          related forms). It is separate from Virtual Coworker’s main WordPress
          websites. This microsite does not send visitors to WordPress for
          privacy or terms.
        </p>

        <h2>What we collect</h2>
        <p>
          When you submit a hiring inquiry we collect the details you provide
          (name, work email, phone, company, and related hiring context), plus
          technical attribution fields such as UTM parameters, Google Click ID
          (GCLID) when present, landing-page URL, referrer, and submission time.
          Career applications on the Philippines path collect the details you
          enter on that form.
        </p>

        <h2>How we use it</h2>
        <p>
          To respond to your enquiry, route the lead to Virtual Coworker, and
          measure paid Search performance for this microsite. We do not sell your
          information.
        </p>

        <h2>Sharing</h2>
        <p>
          Lead details are delivered to Virtual Coworker (email and/or systems
          they designate). Analytics may use market-specific Google Tag Manager /
          GA4 containers for this microsite only (US, AU, and PH are separate
          identities).
        </p>

        <h2>Contact</h2>
        <p>
          For privacy requests related to this microsite, use the US business
          line{" "}
          <a href={SITE.usPhoneHref}>{SITE.usPhoneDisplay}</a> or the teammate
          who follows up on your enquiry.
        </p>
        <p>
          Published office addresses used on this microsite: {SITE.addressUs};{" "}
          {SITE.addressAu}.
        </p>

        <p className="legal-back">
          <Link href="/us">← US hiring home</Link>
          {" · "}
          <Link href="/terms">Terms</Link>
        </p>
      </article>

      <SiteFooter tone="light" market="us" />
    </main>
  );
}
