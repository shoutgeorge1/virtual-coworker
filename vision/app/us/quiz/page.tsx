import type { Metadata } from "next";
import MarketLanding from "../../components/MarketLanding";
import { resolveLpVariant } from "../../../lib/resolve-lp-variant";
import { buildPageMetadata } from "../../../lib/seo";
import "../us.css";

export const metadata: Metadata = buildPageMetadata({
  title: "Employer hiring quiz | Find the right virtual assistant | Virtual Coworker US",
  description:
    "Take the employer hiring quiz. We’ll name the dedicated Filipino teammate that buys back your week. For US businesses hiring staff - not job seekers.",
  path: "/us/quiz",
  indexable: false,
  ogImage: "/brand/hero-us-2026.jpg",
});

export default async function USQuizPage({
  searchParams,
}: {
  searchParams: Promise<{ variant?: string }>;
}) {
  const variant = await resolveLpVariant(await searchParams);
  return <MarketLanding market="us" variant={variant} conversionSurface="quiz" />;
}
