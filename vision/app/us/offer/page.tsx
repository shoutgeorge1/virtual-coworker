import type { Metadata } from "next";
import OfferLanding from "../../components/OfferLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { OFFER_FUNNEL_PATHS } from "../../../config/lp-funnel-challengers";

export const metadata: Metadata = buildPageMetadata({
  title: "Start hiring a dedicated Filipino VA | Virtual Coworker US",
  description:
    "Send your details to start a hiring conversation. We recruit and vet. You interview. We handle payroll and HR. No recruitment fee to start.",
  path: OFFER_FUNNEL_PATHS.us,
  indexable: false,
  ogImage: "/brand/offer-desk-staff.jpg",
});

export default function USOfferPage() {
  return (
    <OfferLanding market="us" careersHref={resolveCareersUrl()} />
  );
}
