import type { Metadata } from "next";
import MarketLanding from "../components/MarketLanding";
import { resolveLpVariant } from "../../lib/resolve-lp-variant";
import { buildPageMetadata } from "../../lib/seo";
import "./us.css";

export const metadata: Metadata = buildPageMetadata({
  title: "Hire Dedicated Filipino Staff | Virtual Coworker US",
  description:
    "Hire a dedicated Filipino teammate for your US business. Free consult. We recruit. You interview. We handle payroll. Not a gig marketplace.",
  path: "/us",
  indexable: true,
  ogImage: "/brand/hero-us-2026.jpg",
});

export default async function USHome({
  searchParams,
}: {
  searchParams: Promise<{ variant?: string }>;
}) {
  const variant = await resolveLpVariant(await searchParams);
  return <MarketLanding market="us" variant={variant} />;
}
