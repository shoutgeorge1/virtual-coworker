import type { Metadata } from "next";
import CapacityChallengerLanding from "../../components/CapacityChallengerLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { TEAMMATE_CHALLENGER_PATHS } from "../../../config/lp-challenger-capacity";

export const metadata: Metadata = buildPageMetadata({
  title: "A reliable teammate, not a freelancer | Virtual Coworker AU",
  description:
    "Interview and choose a vetted Filipino professional. We recruit. You pick. We handle employment admin. Not a gig marketplace.",
  path: TEAMMATE_CHALLENGER_PATHS.au,
  indexable: false,
  ogImage: "/brand/hero-au-2026.jpg",
});

export default function AUTeammatePage() {
  return (
    <CapacityChallengerLanding
      market="au"
      concept="teammate"
      careersHref={resolveCareersUrl()}
    />
  );
}
