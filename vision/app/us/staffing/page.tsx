import type { Metadata } from "next";
import StaffingBaselineLanding from "../../components/StaffingBaselineLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { STAFFING_AGENCY_PATH } from "../../../config/lp-staffing-agency";

export const metadata: Metadata = buildPageMetadata({
  title: "Philippines Remote Staffing Partner | Virtual Coworker US",
  description:
    "A Philippines remote staffing partner for US businesses. We recruit and vet. You interview. We employ the person after you hire.",
  path: STAFFING_AGENCY_PATH,
  indexable: false,
  ogImage: "/brand/hero-us-2026.jpg",
});

/** Unused staffing-agency candidate. Not an Ads Final URL. Noindex. */
export default function USStaffingAgencyPage() {
  return (
    <StaffingBaselineLanding
      market="us"
      careersHref={resolveCareersUrl()}
      profile="staffing_agency"
    />
  );
}
