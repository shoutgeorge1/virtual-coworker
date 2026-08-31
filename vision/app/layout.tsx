import type { Metadata } from "next";
import DataTrackClicks from "./components/DataTrackClicks";
import HashScroll from "./components/HashScroll";
import {
  SITE_URL,
  buildPageMetadata,
  robotsFor,
} from "../lib/seo";
import { SITE } from "../config/site";
import { EXPERIMENTS_BOOT_SCRIPT } from "../lib/experiments";
import "./globals.css";

/**
 * Root defaults. Employer money pages set their own indexable metadata.
 * NEXT_PUBLIC_PILOT_NOINDEX=true forces noindex sitewide (QA). Production: false/unset.
 */
export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  ...buildPageMetadata({
    title: `${SITE.name} · Hire Filipino Staff`,
    description:
      "Hire dedicated Filipino staff for US and Australian businesses - recruit, screen, interview, and hire with Virtual Coworker.",
    path: "/",
    indexable: true,
  }),
  icons: { icon: "/brand/favicon.png" },
  robots: robotsFor("index"),
};

/**
 * Root shell - no shared GTM.
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
        {/* Runs before first paint. Marks the document as JS-capable (scroll
            reveal animations only arm themselves when it is, so content is never
            stuck invisible without JS), applies ?vc_exp=&vc_var= force overrides
            into sticky storage, and paints lp_density lean (parked default) so
            old sticky wordy arms never flash. */}
        <script
          dangerouslySetInnerHTML={{
            __html: EXPERIMENTS_BOOT_SCRIPT,
          }}
        />
      </head>
      <body>
        <HashScroll />
        <DataTrackClicks />
        {children}
      </body>
    </html>
  );
}
