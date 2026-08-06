import type { Metadata } from "next";
import "./globals.css";

const noindex = process.env.NEXT_PUBLIC_PILOT_NOINDEX !== "false";

export const metadata: Metadata = {
  title: "Virtual Coworker · Paid Search Pilot",
  description:
    "Independent Google Search pilot microsite for US and Australian employer leads.",
  icons: { icon: "/brand/favicon.png" },
  robots: noindex
    ? { index: false, follow: false, googleBot: { index: false, follow: false } }
    : { index: true, follow: true },
};

/**
 * Root shell — no shared GTM.
 * US / AU / PH each load their own container via market layouts.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
