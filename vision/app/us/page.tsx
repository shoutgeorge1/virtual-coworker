import type { Metadata } from "next";
import MarketLanding from "../components/MarketLanding";
import { resolveLpVariant } from "../../lib/resolve-lp-variant";
import "./us.css";

export const metadata: Metadata = {
  title: "Hire Offshore Staff | Virtual Coworker US",
  description:
    "Employer landing page for US businesses hiring dedicated Philippines-based staff through Virtual Coworker.",
  robots: { index: false, follow: false },
};

export default async function USHome({
  searchParams,
}: {
  searchParams: Promise<{ variant?: string }>;
}) {
  const sp = await searchParams;
  const variant = await resolveLpVariant(sp);
  return <MarketLanding market="us" variant={variant} />;
}
