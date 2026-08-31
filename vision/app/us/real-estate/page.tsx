import type { Metadata } from "next";
import StaffingBaselineLanding from "../../components/StaffingBaselineLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { REAL_ESTATE_PATH, REAL_ESTATE_SLUG } from "../../../config/lp-real-estate";

export const metadata: Metadata = buildPageMetadata({
  title: "Hire a Real Estate Virtual Assistant | Virtual Coworker US",
  description:
    "Hire dedicated Philippines staff for US brokerages, teams, investors, and property managers. Admin, lead follow-up, and file work.",
  path: REAL_ESTATE_PATH,
  indexable: true,
  ogImage: "/brand/hero-us-2026.jpg",
});

/** Previous real-estate LP. Live ads did not use this URL. TF test is /us/tf/real-estate. */
export default function USRealEstatePage() {
  return (
    <StaffingBaselineLanding
      market="us"
      category={REAL_ESTATE_SLUG}
      careersHref={resolveCareersUrl()}
    />
  );
}
