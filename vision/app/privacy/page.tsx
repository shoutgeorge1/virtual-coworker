import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy · Virtual Coworker Pilot",
  description: "Privacy notice for the Virtual Coworker paid Search pilot microsite.",
  robots: { index: false, follow: false },
};

export default function PrivacyPage() {
  return (
    <main style={{ maxWidth: 640, margin: "3rem auto", padding: "0 1.25rem 3rem", fontFamily: "Poppins, system-ui, sans-serif", color: "#2e333c", lineHeight: 1.65 }}>
      <p style={{ color: "#5a6270", fontSize: "0.85rem", letterSpacing: "0.04em", textTransform: "uppercase" }}>
        Virtual Coworker · Pilot microsite
      </p>
      <h1 style={{ fontSize: "1.75rem", margin: "0.5rem 0 0.75rem", color: "#214873" }}>Privacy</h1>
      <p>
        This page covers the independent paid Search pilot microsite (US and Australia
        employer landing pages). It is separate from Virtual Coworker’s legacy websites.
      </p>
      <h2 style={{ fontSize: "1.1rem", color: "#214873" }}>What we collect</h2>
      <p>
        When you submit a consultation form we collect the details you provide
        (name, work email, phone, company, and related hiring context), plus
        technical attribution fields such as UTM parameters, Google Click ID (GCLID)
        when present, landing-page URL, referrer, and submission time.
      </p>
      <h2 style={{ fontSize: "1.1rem", color: "#214873" }}>How we use it</h2>
      <p>
        To respond to your enquiry, route the lead to Virtual Coworker, and measure
        paid Search performance for this pilot. We do not sell your information.
      </p>
      <h2 style={{ fontSize: "1.1rem", color: "#214873" }}>Sharing</h2>
      <p>
        Lead details are delivered to Virtual Coworker (email and/or systems they
        designate). Analytics may use a temporary Google Tag Manager / GA4 setup
        for this pilot only.
      </p>
      <h2 style={{ fontSize: "1.1rem", color: "#214873" }}>Contact</h2>
      <p>
        For privacy requests related to this pilot, contact Virtual Coworker using
        the channels published on their main website, or the lead recipient who
        follows up on your enquiry.
      </p>
      <p style={{ marginTop: "1.5rem" }}>
        <Link href="/us" style={{ color: "#0f6e6a" }}>US</Link>
        {" · "}
        <Link href="/au" style={{ color: "#0f6e6a" }}>Australia</Link>
        {" · "}
        <Link href="/thank-you" style={{ color: "#0f6e6a" }}>Thank you</Link>
      </p>
    </main>
  );
}
