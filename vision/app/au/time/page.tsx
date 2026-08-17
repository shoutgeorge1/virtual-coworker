import type { Metadata } from "next";
import CapacityChallengerLanding from "../../components/CapacityChallengerLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { TIME_CHALLENGER_PATHS } from "../../../config/lp-challenger-capacity";

export const metadata: Metadata = buildPageMetadata({
  title: "Stop losing your mornings | Virtual Coworker AU",
  description:
    "Add a vetted Filipino specialist for the recurring work consuming your team. We recruit. You interview. We handle employment admin.",
  path: TIME_CHALLENGER_PATHS.au,
  indexable: false,
  ogImage: "/brand/hero-au-2026.jpg",
});

export default function AUTimePage() {
  return (
    <CapacityChallengerLanding
      market="au"
      concept="time"
      careersHref={resolveCareersUrl()}
    />
  );
}
