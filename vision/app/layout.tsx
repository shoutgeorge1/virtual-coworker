import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

const noindex = process.env.NEXT_PUBLIC_PILOT_NOINDEX !== "false";
const gtmId = process.env.NEXT_PUBLIC_GTM_ID;

export const metadata: Metadata = {
  title: "Virtual Coworker · Paid Search Pilot",
  description:
    "Independent Google Search pilot microsite for US and Australian employer leads.",
  icons: { icon: "/brand/favicon.png" },
  robots: noindex
    ? { index: false, follow: false, googleBot: { index: false, follow: false } }
    : { index: true, follow: true },
};

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
      <body>
        {gtmId ? (
          <>
            <Script id="gtm-init" strategy="afterInteractive">{`
              window.dataLayer = window.dataLayer || [];
              window.dataLayer.push({ 'gtm.start': new Date().getTime(), event: 'gtm.js' });
            `}</Script>
            <Script
              id="gtm"
              strategy="afterInteractive"
              src={`https://www.googletagmanager.com/gtm.js?id=${encodeURIComponent(gtmId)}`}
            />
          </>
        ) : null}
        {children}
      </body>
    </html>
  );
}
