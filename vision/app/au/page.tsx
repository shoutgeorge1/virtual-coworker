import type { Metadata } from "next";
import MarketLanding from "../components/MarketLanding";
import { resolveLpVariant } from "../../lib/resolve-lp-variant";
import { normalizeHeroOverlay } from "../../lib/hero-overlay";
import "./au.css";

export const metadata: Metadata = {
  title: "Hire Offshore Staff | Virtual Coworker Australia",
  description:
    "Hire dedicated Philippines staff for your Australian business — recruit, screen, interview, and hire with Virtual Coworker.",
  robots: { index: false, follow: false },
};

export default async function AUHome({
  searchParams,
}: {
  searchParams: Promise<{ variant?: string; hero?: string }>;
}) {
  const sp = await searchParams;
  const variant = await resolveLpVariant(sp);
  const heroOverlay = normalizeHeroOverlay(sp.hero);
  return (
    <MarketLanding market="au" variant={variant} heroOverlay={heroOverlay} />
  );
}
