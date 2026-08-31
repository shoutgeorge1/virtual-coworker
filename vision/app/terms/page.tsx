import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import { SITE } from "../../config/site";

import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Terms · Virtual Coworker",
  description:
    "Terms for using Virtual Coworker’s hiring website and related forms.",
  path: "/terms",
  indexable: true,
});

export default function TermsPage() {
  return (
    <main className="micro micro-legal">
      <MarketGtm surface="us" />
      <SiteNav tone="light" market="us" />

      <article className="legal-doc">
        <p className="micro-kicker legal-kicker">Virtual Coworker</p>
        <h1>Terms of use</h1>
        <p>
          These terms apply to this Virtual Coworker website - US and Australia
          hiring pages, services, how-it-works, the Philippines careers path,
          and related forms. By using the site you agree to these terms and our{" "}
          <Link href="/privacy">Privacy notice</Link>.
        </p>
        <p>
          Virtual Coworker helps businesses hire dedicated Filipino staff and
          offers a separate careers path for talent. Content on this site is for
          general information; it is not legal, tax, or employment advice for
          your specific situation.
        </p>

        <h2>What submitting a form means</h2>
        <p>
          Sending a hiring request on US or Australia pages asks our team to
          follow up for a hiring conversation. It is not an instant hire, a job
          offer, or a signed contract. Placement, rates, and employment terms -
          if any - are confirmed separately. The Philippines path is for talent
          applications only and is not a business hiring form.
        </p>

        <h2>Acceptable use</h2>
        <p>
          Use this website lawfully and in good faith. Do not misuse forms
          (including automated spam), attempt unauthorized access, or interfere
          with the site’s operation. We may decline or remove submissions that
          appear abusive, fraudulent, or unrelated to hiring or careers.
        </p>

        <h2>Accuracy and availability</h2>
        <p>
          We aim to keep information current, but roles, availability, pricing,
          and processes can change. The site may be updated, interrupted, or
          unavailable from time to time. We are not responsible for third-party
          sites or tools you choose to use alongside ours.
        </p>

        <h2>Intellectual property</h2>
        <p>
          Branding, text, layout, and media on this website belong to Virtual
          Coworker or its licensors. You may not copy or reuse them for
          commercial purposes without permission, except for fair personal use
          of publicly available pages.
        </p>

        <h2>Limitation of liability</h2>
        <p>
          To the fullest extent permitted by law, Virtual Coworker is not liable
          for indirect, incidental, or consequential losses arising from use of
          this website or reliance on its content. Nothing in these terms
          excludes rights that cannot be excluded under applicable consumer law.
        </p>

        <h2>SMS (if offered)</h2>
        <p>
          If you opt into SMS from Virtual Coworker, messages may relate to
          scheduling or inquiries; frequency varies; carrier message and data
          rates may apply. Reply STOP or CANCEL to opt out, or HELP for help.
          Contact details for messaging support may also be provided in those
          messages.
        </p>

        <h2>Privacy</h2>
        <p>
          How we handle personal information is described in our{" "}
          <Link href="/privacy">Privacy notice</Link>. We do not sell your
          information for third-party marketing.
        </p>

        <h2>Contact</h2>
        <p>
          US business line:{" "}
          <a href={SITE.usPhoneHref}>{SITE.usPhoneDisplay}</a>. Privacy:{" "}
          <a href="mailto:dpo@virtualcoworker.com">dpo@virtualcoworker.com</a>.
          Offices: {SITE.addressUs}; {SITE.addressAu}.
        </p>
        <p>
          We may update these terms as the site evolves. Continued use after
          changes means you accept the updated terms.
        </p>

        <p className="legal-back">
          <Link href="/us">← US hiring home</Link>
          {" · "}
          <Link href="/au">Australia</Link>
          {" · "}
          <Link href="/privacy">Privacy</Link>
        </p>
      </article>

      <SiteFooter tone="light" market="us" />
    </main>
  );
}
