import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import { SITE } from "../../config/site";

export const metadata: Metadata = {
  title: "Privacy · Virtual Coworker",
  description:
    "How Virtual Coworker collects, uses, and protects personal information on this website.",
  robots: { index: false, follow: false },
};

export default function PrivacyPage() {
  return (
    <main className="micro micro-legal">
      <MarketGtm surface="us" />
      <SiteNav tone="light" market="us" />

      <article className="legal-doc">
        <p className="micro-kicker legal-kicker">Virtual Coworker</p>
        <h1>Privacy notice</h1>
        <p>
          Virtual Coworker Inc. and Virtual Coworker Pty. Ltd. (ABN 49 154 746
          004) (“Virtual Coworker,” “we,” “us”) respect your privacy. This
          notice explains how we handle personal information submitted through
          this website — including US and Australia hiring pages, the
          Philippines careers path, services, how-it-works, and related forms.
        </p>
        <p>
          By using this website or submitting a form, you acknowledge this
          notice. We do not sell, rent, or share your personal information —
          including mobile numbers — with third parties for their marketing.
        </p>

        <h2>Who this covers</h2>
        <p>
          Employers using US or Australia hiring pages, and talent using the
          Philippines careers path. Office addresses published on this site:{" "}
          {SITE.addressUs}; {SITE.addressAu}.
        </p>

        <h2>What we collect</h2>
        <p>
          When you send a hiring request we collect the details you provide —
          typically name, work email, phone, company, and role context — plus
          standard web attribution such as campaign tags, click identifiers when
          present, landing-page URL, referrer, and submission time. Career
          applications on the Philippines path collect the details you enter on
          that form. If you call us, we may collect information you share on
          the call.
        </p>
        <p>
          Like most websites, we and our analytics providers may collect device
          and usage data (for example pages viewed, approximate location from IP,
          and browser type) to operate and improve the site.
        </p>

        <h2>How we use it</h2>
        <p>We use personal information to:</p>
        <ul>
          <li>Respond to hiring requests and career applications</li>
          <li>Route leads and applications to the right Virtual Coworker team</li>
          <li>Schedule follow-up conversations and support onboarding</li>
          <li>Understand how people find and use these pages</li>
          <li>Maintain security, prevent abuse, and meet legal obligations</li>
        </ul>

        <h2>Meetings and recordings</h2>
        <p>
          Hiring conversations, interviews, or related meetings may be recorded
          for documentation, quality assurance, training, or internal review,
          where permitted by law. Where required, we will provide notice before
          recording. If you prefer not to be recorded, tell the meeting host or
          leave the session.
        </p>

        <h2>Sharing</h2>
        <p>
          Lead and application details are delivered to Virtual Coworker (email
          and/or systems we designate). We may share information with trusted
          service providers who help us operate email, hosting, analytics, or
          communications — under obligations to protect it — and with
          authorities when required by law. Analytics on these pages may use
          separate Google Tag Manager / GA4 setups for the US, Australia, and
          Philippines paths.
        </p>

        <h2>Retention and security</h2>
        <p>
          We keep personal information only as long as needed for the purposes
          above, or as required by law or legitimate business needs. We maintain
          administrative, technical, and physical safeguards designed to protect
          information from unauthorized access, alteration, disclosure, misuse,
          loss, or destruction. Access is limited to authorized personnel on a
          business-need basis.
        </p>

        <h2>Your choices</h2>
        <p>
          You may request access to, correction of, or deletion of personal
          information we hold about you, subject to applicable law (including,
          for Australian residents, the Australian Privacy Principles). Contact
          us using the details below. If SMS messaging is offered and you opt
          in, message frequency may vary and carrier rates may apply; reply STOP
          or CANCEL to opt out, or HELP for assistance.
        </p>

        <h2>Contact</h2>
        <p>
          Privacy and data requests:{" "}
          <a href="mailto:dpo@virtualcoworker.com">dpo@virtualcoworker.com</a>.
          US business line:{" "}
          <a href={SITE.usPhoneHref}>{SITE.usPhoneDisplay}</a>. You may also
          reach the teammate who follows up on your request.
        </p>
        <p>
          We review this notice as our practices evolve. The version on this
          page is current for this website.
        </p>

        <p className="legal-back">
          <Link href="/us">← US hiring home</Link>
          {" · "}
          <Link href="/au">Australia</Link>
          {" · "}
          <Link href="/terms">Terms</Link>
        </p>
      </article>

      <SiteFooter tone="light" market="us" />
    </main>
  );
}
