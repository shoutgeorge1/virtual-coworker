import type { Metadata } from "next";
import CapacityChallengerLanding from "../../components/CapacityChallengerLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { CAPACITY_CHALLENGER_PATHS } from "../../../config/lp-challenger-capacity";

export const metadata: Metadata = buildPageMetadata({
  title: "Hire Filipino staff without another local hire | Virtual Coworker US",
  description:
    "Add a vetted Filipino specialist who works US business hours. We recruit. You interview. We handle payroll and HR.",
  path: CAPACITY_CHALLENGER_PATHS.us,
  indexable: false,
  ogImage: "/brand/hero-us-2026.jpg",
});

export default function USCapacityPage() {
  return (
    <CapacityChallengerLanding
      market="us"
      careersHref={resolveCareersUrl()}
    />
  );
}
