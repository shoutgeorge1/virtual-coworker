import type { Metadata } from "next";
import Link from "next/link";
import ThankYouClient from "./ThankYouClient";

export const metadata: Metadata = {
  title: "Thank you · Virtual Coworker",
  description: "Your employer inquiry was received.",
  robots: { index: false, follow: false },
};

export default async function ThankYouPage({
  searchParams,
}: {
  searchParams: Promise<{ market?: string; sid?: string; eligible?: string }>;
}) {
  const sp = await searchParams;
  const market = sp?.market === "au" ? "au" : sp?.market === "us" ? "us" : "";
  const sid = sp?.sid || "";
  const conversionEligible = sp?.eligible !== "0";

  return (
    <main
      style={{
        maxWidth: 560,
        margin: "4rem auto",
        padding: "0 1.25rem",
        fontFamily: "Poppins, system-ui, sans-serif",
      }}
    >
      <p
        style={{
          color: "#5a6270",
          fontSize: "0.85rem",
          letterSpacing: "0.04em",
          textTransform: "uppercase",
        }}
      >
        Virtual Coworker ·{" "}
        {conversionEligible ? "Employer inquiry confirmed" : "QA / log-only receipt"}
      </p>
      <h1 style={{ fontSize: "1.75rem", margin: "0.5rem 0 0.75rem", color: "#214873" }}>
        {conversionEligible
          ? "Thanks — we got your request."
          : "Request logged (delivery not live)."}
      </h1>
      <p style={{ color: "#2e333c", lineHeight: 1.6 }}>
        {conversionEligible
          ? "A team member will follow up using the details you provided. This confirmation only appears after your employer inquiry was accepted and delivered."
          : "This environment is in log-only / blocked delivery mode. Your details were written to server logs for QA — they were not delivered to a live inbox, and this is not a paid conversion."}
      </p>
      {sid ? (
        <p style={{ color: "#5a6270", fontSize: "0.85rem", marginTop: "1rem" }}>
          Reference: <code>{sid}</code>
        </p>
      ) : null}
      <ThankYouClient
        market={market}
        submissionId={sid}
        conversionEligible={conversionEligible}
      />
      <p style={{ marginTop: "1.5rem" }}>
        {market === "au" ? (
          <Link href="/au" style={{ color: "#0f6e6a" }}>
            Back to Australia
          </Link>
        ) : (
          <Link href="/us" style={{ color: "#0f6e6a" }}>
            Back to United States
          </Link>
        )}
        {" · "}
        <Link href="/privacy" style={{ color: "#0f6e6a" }}>
          Privacy
        </Link>
      </p>
    </main>
  );
}
