import type { Metadata } from "next";
import ConsultLanding from "../../components/ConsultLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { CONSULT_PATHS } from "../../../config/lp-consult";

export const metadata: Metadata = buildPageMetadata({
  title: "Your team is maxed. Hire staff who can learn your systems. | Virtual Coworker US",
  description:
    "Capacity, first-time offshore hiring, and how to grant access safely. We recruit for the role. You interview. Part-time from 20 hours/week. Obligation free.",
  path: CONSULT_PATHS.us,
  indexable: false,
  ogImage: "/brand/va-us.jpg",
});

export default function USConsultPage() {
  return <ConsultLanding market="us" careersHref={resolveCareersUrl()} />;
}
