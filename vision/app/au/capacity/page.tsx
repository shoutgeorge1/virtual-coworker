import type { Metadata } from "next";
import CapacityChallengerLanding from "../../components/CapacityChallengerLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { CAPACITY_CHALLENGER_PATHS } from "../../../config/lp-challenger-capacity";

export const metadata: Metadata = buildPageMetadata({
  title: "Hire Filipino staff without another local hire | Virtual Coworker AU",
  description:
    "Add a vetted Filipino specialist who works Australian business hours. We recruit. You interview. We handle employment admin.",
  path: CAPACITY_CHALLENGER_PATHS.au,
  indexable: false,
  ogImage: "/brand/hero-au-2026.jpg",
});

export default function AUCapacityPage() {
  return (
    <CapacityChallengerLanding
      market="au"
      careersHref={resolveCareersUrl()}
    />
  );
}
