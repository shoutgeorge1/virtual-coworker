import type { Metadata } from "next";
import StaffingBaselineLanding from "../components/StaffingBaselineLanding";
import { buildPageMetadata } from "../../lib/seo";
import { resolveCareersUrl } from "../../config/markets";

export const metadata: Metadata = buildPageMetadata({
  title: "Hire Dedicated Filipino Staff | Virtual Coworker US",
  description:
    "Hire dedicated Filipino remote staff from $7/hour. We recruit and vet. You interview the shortlist. We handle payroll.",
  path: "/us",
  indexable: true,
  ogImage: "/brand/hero-us-2026.jpg",
});

export default function USHome() {
  return (
    <StaffingBaselineLanding market="us" careersHref={resolveCareersUrl()} />
  );
}
