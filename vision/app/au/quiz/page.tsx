import type { Metadata } from "next";
import MarketLanding from "../../components/MarketLanding";
import { resolveLpVariant } from "../../../lib/resolve-lp-variant";
import { buildPageMetadata } from "../../../lib/seo";
import "../au.css";

export const metadata: Metadata = buildPageMetadata({
  title: "Employer hiring quiz | Find the right virtual assistant | Virtual Coworker AU",
  description:
    "Take the employer hiring quiz. We’ll name the dedicated Filipino teammate that takes the load. For Australian businesses hiring staff - not job seekers.",
  path: "/au/quiz",
  indexable: false,
  ogImage: "/brand/hero-au-2026.jpg",
});

export default async function AUQuizPage({
  searchParams,
}: {
  searchParams: Promise<{ variant?: string }>;
}) {
  const variant = await resolveLpVariant(await searchParams);
  return <MarketLanding market="au" variant={variant} conversionSurface="quiz" />;
}
