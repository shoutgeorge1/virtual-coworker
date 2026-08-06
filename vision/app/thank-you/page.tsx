import type { Metadata } from "next";
import Link from "next/link";
import ThankYouClient from "./ThankYouClient";

export const metadata: Metadata = {
  title: "Thank you · Virtual Coworker",
  description: "Thanks — we got your hiring request.",
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
  const isAu = market === "au";

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
        Virtual Coworker
        {market === "au" ? " · Australia" : market === "us" ? " · United States" : ""}
      </p>
      <h1 style={{ fontSize: "1.75rem", margin: "0.5rem 0 0.75rem", color: "#214873" }}>
        {conversionEligible
          ? isAu
            ? "Thanks — we got your request."
            : "Thanks — we got your request."
          : "Thanks — this was a test submission."}
      </h1>
      {conversionEligible ? (
        <>
          <p style={{ color: "#2e333c", lineHeight: 1.6 }}>
            {isAu
              ? "A teammate will follow up to talk through the role and next steps. From there we’ll take your brief, shortlist screened candidates, and you’ll interview before anyone starts."
              : "A teammate will follow up to talk through the role and next steps. From there we’ll take your brief, shortlist screened candidates, and you’ll interview before anyone starts."}
          </p>
          <ol
            style={{
              color: "#2e333c",
              lineHeight: 1.55,
              paddingLeft: "1.25rem",
              margin: "1.25rem 0 0",
            }}
          >
            <li>Hiring conversation with our team</li>
            <li>Role brief → we recruit and screen</li>
            <li>You interview the shortlist</li>
            <li>Hire and onboard with our support</li>
          </ol>
        </>
      ) : (
        <p style={{ color: "#2e333c", lineHeight: 1.6 }}>
          Our hiring team was not notified. If you meant to send a real request,
          please try again from the hiring page — or contact us if something
          looks wrong.
        </p>
      )}
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
