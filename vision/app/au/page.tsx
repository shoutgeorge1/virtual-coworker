import type { Metadata } from "next";
import GuidedMatchLanding from "../components/GuidedMatchLanding";
import { resolveLpVariant } from "../../lib/resolve-lp-variant";
import { buildPageMetadata } from "../../lib/seo";
import { resolveCareersUrl } from "../../config/markets";

export const metadata: Metadata = buildPageMetadata({
  title: "Hire Dedicated Filipino Staff | Virtual Coworker AU",
  description:
    "Hire a dedicated Filipino teammate for Australian hours. We recruit. You interview. We handle employment admin. Not a gig marketplace.",
  path: "/au",
  indexable: true,
  ogImage: "/brand/hero-au-2026.jpg",
});

export default async function AUHome({
  searchParams,
}: {
  searchParams: Promise<{ variant?: string }>;
}) {
  const variant = await resolveLpVariant(await searchParams);
  return (
    <GuidedMatchLanding
      market="au"
      variant={variant}
      careersHref={resolveCareersUrl()}
    />
  );
}
