import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import { SITE } from "../../config/site";

export const metadata: Metadata = {
  title: "Privacy · Virtual Coworker",
  description: "Privacy notice for Virtual Coworker hiring pages.",
  robots: { index: false, follow: false },
};

export default function PrivacyPage() {
  return (
    <main className="micro micro-legal">
      <MarketGtm surface="us" />
      <SiteNav tone="light" market="us" />

      <article className="legal-doc">
        <p className="micro-kicker legal-kicker">Privacy</p>
        <h1>Privacy</h1>
        <p>
          This notice covers Virtual Coworker’s US and Australia hiring pages,
          Philippines careers path, services, and related forms on this site.
        </p>

        <h2>What we collect</h2>
        <p>
          When you submit a hiring request we collect the details you provide
          (name, work email, phone, company, and related hiring context), plus
          standard web attribution such as campaign tags, click identifiers when
          present, landing-page URL, referrer, and submission time. Career
          applications on the Philippines path collect the details you enter on
          that form.
        </p>

        <h2>How we use it</h2>
        <p>
          To respond to your request, route it to Virtual Coworker, and
          understand how people find these pages. We do not sell your
          information.
        </p>

        <h2>Sharing</h2>
        <p>
          Lead details are delivered to Virtual Coworker (email and/or systems
          they designate). Analytics may use separate Google Tag Manager / GA4
          setups for the US, Australia, and Philippines paths.
        </p>

        <h2>Contact</h2>
        <p>
          For privacy requests, use the US business line{" "}
          <a href={SITE.usPhoneHref}>{SITE.usPhoneDisplay}</a> or the teammate
          who follows up on your request.
        </p>
        <p>
          Office addresses: {SITE.addressUs}; {SITE.addressAu}.
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
