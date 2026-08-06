import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import { SITE } from "../../config/site";

export const metadata: Metadata = {
  title: "Terms · Virtual Coworker",
  description: "Terms for Virtual Coworker hiring pages.",
  robots: { index: false, follow: false },
};

export default function TermsPage() {
  return (
    <main className="micro micro-legal">
      <MarketGtm surface="us" />
      <SiteNav tone="light" market="us" />

      <article className="legal-doc">
        <p className="micro-kicker legal-kicker">Terms</p>
        <h1>Terms</h1>
        <p>
          These pages help US and Australian businesses hire dedicated
          Philippines staff, and offer a separate Philippines careers path for
          talent.
        </p>
        <h2>What submitting a form means</h2>
        <p>
          Sending a hiring request on US or Australia pages asks our team to
          follow up. It is not an instant hire or a signed contract. The
          Philippines path is for talent applications only.
        </p>
        <h2>Privacy</h2>
        <p>
          How we handle your details:{" "}
          <Link href="/privacy">Privacy notice</Link>.
        </p>
        <h2>Contact</h2>
        <p>
          US business line:{" "}
          <a href={SITE.usPhoneHref}>{SITE.usPhoneDisplay}</a>. Offices:{" "}
          {SITE.addressUs}; {SITE.addressAu}.
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
