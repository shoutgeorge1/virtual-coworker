import type { Metadata } from "next";
import StaffingBaselineLanding from "../components/StaffingBaselineLanding";
import { buildPageMetadata } from "../../lib/seo";
import { resolveCareersUrl } from "../../config/markets";

export const metadata: Metadata = buildPageMetadata({
  title: "Hire Dedicated Filipino Staff | Virtual Coworker AU",
  description:
    "Hire dedicated Filipino remote staff for Australian hours. We recruit and vet. You interview the shortlist. We handle employment admin.",
  path: "/au",
  indexable: true,
  ogImage: "/brand/hero-au-2026.jpg",
});

export default function AUHome() {
  return (
    <StaffingBaselineLanding market="au" careersHref={resolveCareersUrl()} />
  );
}
