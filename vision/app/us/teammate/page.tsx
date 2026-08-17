import type { Metadata } from "next";
import CapacityChallengerLanding from "../../components/CapacityChallengerLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { TEAMMATE_CHALLENGER_PATHS } from "../../../config/lp-challenger-capacity";

export const metadata: Metadata = buildPageMetadata({
  title: "A reliable teammate, not a freelancer | Virtual Coworker US",
  description:
    "Interview and choose a vetted Filipino professional. We recruit. You pick. We handle payroll and HR. Not a gig marketplace.",
  path: TEAMMATE_CHALLENGER_PATHS.us,
  indexable: false,
  ogImage: "/brand/hero-us-2026.jpg",
});

export default function USTeammatePage() {
  return (
    <CapacityChallengerLanding
      market="us"
      concept="teammate"
      careersHref={resolveCareersUrl()}
    />
  );
}
