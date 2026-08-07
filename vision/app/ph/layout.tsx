import type { Metadata } from "next";
import MarketGtm from "../components/MarketGtm";
import { buildPageMetadata } from "../../lib/seo";

/** Job-seeker exit ramp — not the careers destination of record. Keep noindex. */
export const metadata: Metadata = buildPageMetadata({
  title: "Looking for work? · Virtual Coworker",
  description:
    "This hiring microsite is for businesses. Job applications continue on our Philippines careers site.",
  path: "/ph",
  indexable: false,
});

export default function PhLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <MarketGtm surface="ph" />
      {children}
    </>
  );
}
