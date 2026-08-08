import type { Metadata } from "next";
import MarketLanding from "../components/MarketLanding";
import { resolveLpVariant } from "../../lib/resolve-lp-variant";
import { buildPageMetadata } from "../../lib/seo";
import "./au.css";

export const metadata: Metadata = buildPageMetadata({
  title: "Hire Dedicated Filipino Staff | Virtual Coworker AU",
  description:
    "Add dependable capacity for Australian business hours with dedicated Filipino teammates — we recruit and shortlist, you interview and choose.",
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
