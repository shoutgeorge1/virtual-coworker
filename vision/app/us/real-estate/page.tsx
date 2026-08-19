import type { Metadata } from "next";
import StaffingBaselineLanding from "../../components/StaffingBaselineLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import {
  REAL_ESTATE_DESCRIPTION,
  REAL_ESTATE_PATH,
  REAL_ESTATE_ROLES_HEADING,
  REAL_ESTATE_SLUG,
  REAL_ESTATE_TITLE,
  buildRealEstateRoute,
} from "../../../config/real-estate";

export const metadata: Metadata = buildPageMetadata({
  title: REAL_ESTATE_TITLE,
  description: REAL_ESTATE_DESCRIPTION,
  path: REAL_ESTATE_PATH,
  indexable: true,
  ogImage: "/brand/hero-us-2026.jpg",
});

export default function USRealEstatePage() {
  return (
    <StaffingBaselineLanding
      market="us"
      careersHref={resolveCareersUrl()}
      routeOverride={buildRealEstateRoute()}
      rolesHeading={REAL_ESTATE_ROLES_HEADING}
      trackingCategory={REAL_ESTATE_SLUG}
    />
  );
}
