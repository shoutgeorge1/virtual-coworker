import type { Metadata } from "next";
import ConsultLanding from "../../components/ConsultLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { CONSULT_PATHS } from "../../../config/lp-consult";

export const metadata: Metadata = buildPageMetadata({
  title: "Your team is maxed. Hire staff who can learn your systems. | Virtual Coworker AU",
  description:
    "Capacity, first-time offshore hiring, AU/NZ industry experience, and how to grant access safely. We recruit for Australian hours. You interview. Part-time from 20 hours/week. Obligation free.",
  path: CONSULT_PATHS.au,
  indexable: false,
  ogImage: "/brand/va-au.jpg",
});

export default function AUConsultPage() {
  return <ConsultLanding market="au" careersHref={resolveCareersUrl()} />;
}
