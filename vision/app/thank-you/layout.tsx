import type { ReactNode } from "react";
import Script from "next/script";

/** Thank-you only: warm Calendly widget assets. Do not load on /us or /au LPs. */
export default function ThankYouLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <link rel="preconnect" href="https://calendly.com" />
      <link rel="preconnect" href="https://assets.calendly.com" crossOrigin="anonymous" />
      <link rel="dns-prefetch" href="https://calendly.com" />
      <link rel="dns-prefetch" href="https://assets.calendly.com" />
      <link rel="stylesheet" href="https://assets.calendly.com/assets/external/widget.css" />
      <Script
        src="https://assets.calendly.com/assets/external/widget.js"
        strategy="afterInteractive"
      />
      {children}
    </>
  );
}
