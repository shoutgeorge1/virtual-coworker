import type { Metadata } from "next";
import ProofLanding from "../../components/ProofLanding";
import { buildPageMetadata } from "../../../lib/seo";
import { resolveCareersUrl } from "../../../config/markets";
import { PROOF_FUNNEL_PATHS } from "../../../config/lp-funnel-challengers";

export const metadata: Metadata = buildPageMetadata({
  title: "How employers hire dedicated Filipino staff | Virtual Coworker AU",
  description:
    "Read a named employer story, then send your details. We recruit and vet. You interview. We handle employment admin.",
  path: PROOF_FUNNEL_PATHS.au,
  indexable: false,
  ogImage: "/guided-match/trust-consult.jpg",
});

export default function AUProofPage() {
  return (
    <ProofLanding market="au" careersHref={resolveCareersUrl()} />
  );
}
