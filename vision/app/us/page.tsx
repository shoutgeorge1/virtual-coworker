import type { Metadata } from "next";
import MarketLanding from "../components/MarketLanding";
import { resolveLpVariant } from "../../lib/resolve-lp-variant";
import { buildPageMetadata } from "../../lib/seo";
import "./us.css";

export const metadata: Metadata = buildPageMetadata({
  title: "Hire Dedicated Filipino Staff | Virtual Coworker US",
  description:
    "Free your team from work that keeps slipping. Hire dedicated Filipino coworkers for your US business — we recruit and vet, you interview and decide.",
  path: "/us",
  indexable: true,
  ogImage: "/brand/hero-us-2026.jpg",
});

export default async function USHome({
  searchParams,
}: {
  searchParams: Promise<{ variant?: string }>;
}) {
  const sp = await searchParams;
  const variant = await resolveLpVariant(sp);
  return <MarketLanding market="us" variant={variant} />;
}
