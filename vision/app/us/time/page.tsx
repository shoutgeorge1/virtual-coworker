import type { Metadata } from "next";
import CapacityChallengerLanding from "../../components/CapacityChallengerLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { TIME_CHALLENGER_PATHS } from "../../../config/lp-challenger-capacity";

export const metadata: Metadata = buildPageMetadata({
  title: "Stop losing your mornings | Virtual Coworker US",
  description:
    "Add a vetted Filipino specialist for the recurring work consuming your team. We recruit. You interview. We handle payroll and HR.",
  path: TIME_CHALLENGER_PATHS.us,
  indexable: false,
  ogImage: "/brand/hero-us-2026.jpg",
});

export default function USTimePage() {
  return (
    <CapacityChallengerLanding
      market="us"
      concept="time"
      careersHref={resolveCareersUrl()}
    />
  );
}
