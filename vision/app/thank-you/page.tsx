import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Thank you · Virtual Coworker",
  description: "Your consultation request was received.",
  robots: { index: false, follow: false },
};

export default function ThankYouPage() {
  return (
    <main style={{ maxWidth: 560, margin: "4rem auto", padding: "0 1.25rem", fontFamily: "Poppins, system-ui, sans-serif" }}>
      <p style={{ color: "#5a6270", fontSize: "0.85rem", letterSpacing: "0.04em", textTransform: "uppercase" }}>
        Virtual Coworker · Pilot
      </p>
      <h1 style={{ fontSize: "1.75rem", margin: "0.5rem 0 0.75rem", color: "#214873" }}>
        Thanks — we got your request.
      </h1>
      <p style={{ color: "#2e333c", lineHeight: 1.6 }}>
        A team member will follow up using the details you provided.
        If you need to reach us sooner, reply to the confirmation email once it arrives,
        or use the phone number on the landing page (when published).
      </p>
      <p style={{ marginTop: "1.5rem" }}>
        <Link href="/us" style={{ color: "#0f6e6a" }}>US</Link>
        {" · "}
        <Link href="/au" style={{ color: "#0f6e6a" }}>Australia</Link>
        {" · "}
        <Link href="/privacy" style={{ color: "#0f6e6a" }}>Privacy</Link>
      </p>
    </main>
  );
}
