import type { Metadata } from "next";
import MarketLanding from "../components/MarketLanding";
import { resolveLpVariant } from "../../lib/resolve-lp-variant";
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
  searchParams: Promise<{ variant?: string }>;
}) {
  const sp = await searchParams;
  const variant = await resolveLpVariant(sp);
  return <MarketLanding market="au" variant={variant} />;
}
