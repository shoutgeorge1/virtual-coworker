import type { Metadata } from "next";
import MarketLanding from "../components/MarketLanding";
import { resolveLpVariant } from "../../lib/resolve-lp-variant";
import { buildPageMetadata } from "../../lib/seo";
import "./au.css";

export const metadata: Metadata = buildPageMetadata({
  title: "Hire Filipino Staff for Australian Business Hours | Virtual Coworker AU",
  description:
    "Hire dedicated Filipino teammates for your Australian business — recruit, screen, interview, and hire. Australian business hours. Not a gig marketplace.",
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
