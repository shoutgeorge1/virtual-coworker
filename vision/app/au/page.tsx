import type { Metadata } from "next";
import MarketLanding from "../components/MarketLanding";
import { resolveLpVariant } from "../../lib/resolve-lp-variant";
import { buildPageMetadata } from "../../lib/seo";
import "./au.css";

export const metadata: Metadata = buildPageMetadata({
  title: "Hire Dedicated Filipino Staff | Virtual Coworker AU",
  description:
    "Hire a dedicated Filipino teammate for Australian hours. Free chat. We recruit. You interview. We handle employment admin. Not a gig marketplace.",
  path: "/au",
  indexable: true,
  ogImage: "/brand/hero-au-2026.jpg",
});

export default async function AUHome({
  searchParams,
}: {
  searchParams: Promise<{ variant?: string }>;
}) {
  const sp = await searchParams;
  const variant = await resolveLpVariant(sp);
  return <MarketLanding market="au" variant={variant} />;
}
