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
  searchParams: Promise<{ market?: string; sid?: string }>;
}) {
  const sp = await searchParams;
  const market = sp?.market === "au" ? "au" : sp?.market === "us" ? "us" : "";
  const sid = sp?.sid || "";

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
        Virtual Coworker · Employer inquiry confirmed
      </p>
      <h1 style={{ fontSize: "1.75rem", margin: "0.5rem 0 0.75rem", color: "#214873" }}>
        Thanks — we got your request.
      </h1>
      <p style={{ color: "#2e333c", lineHeight: 1.6 }}>
        A team member will follow up using the details you provided. This confirmation only
        appears after your employer inquiry was accepted by our server.
      </p>
      {sid ? (
        <p style={{ color: "#5a6270", fontSize: "0.85rem", marginTop: "1rem" }}>
          Reference: <code>{sid}</code>
        </p>
      ) : null}
      <ThankYouClient market={market} submissionId={sid} />
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
