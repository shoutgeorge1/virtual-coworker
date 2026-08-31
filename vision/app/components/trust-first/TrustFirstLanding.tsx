"use client";

import { useEffect } from "react";
import type { TrustFirstPageConfig, TrustFirstVariant } from "../../../config/trust-first";
import {
  TRUST_FIRST_EXPERIMENT_ID,
  TRUST_FIRST_PRODUCTION_LANDING_PAGE_TYPE,
  TRUST_FIRST_PRODUCTION_LP_VERSION,
} from "../../../config/trust-first";
import { US_BASELINE_LABEL } from "../../../config/lp-version";
import { isProofHeavy } from "../../../lib/trust-first";
import { captureAttribution } from "../../../lib/tracking";
import { trackLpView } from "../../../lib/lp-events";
import "../../preview/trust-first/trust-first.css";
import CompanyFooter from "./CompanyFooter";
import CompanyHeader from "./CompanyHeader";
import CompanyProof from "./CompanyProof";
import EmployerComparison from "./EmployerComparison";
import FAQ from "./FAQ";
import HowItWorks from "./HowItWorks";
import ObjectionHandling from "./ObjectionHandling";
import PhilippinesMarketFacts from "./PhilippinesMarketFacts";
import ProofStrip from "./ProofStrip";
import ReviewBadges from "./ReviewBadges";
import RoleOrTaskCards from "./RoleOrTaskCards";
import Testimonials from "./Testimonials";
import TrustHero from "./TrustHero";
import BuiltForTrust from "./BuiltForTrust";
import PressRow from "./PressRow";
import WhyVirtualCoworker from "./WhyVirtualCoworker";

export default function TrustFirstLanding({
  page,
  variant,
  surface = "preview",
}: {
  page: TrustFirstPageConfig;
  variant: TrustFirstVariant;
  surface?: "preview" | "production";
}) {
  const heavy = isProofHeavy(variant);
  const faqs = heavy ? page.faqs : page.faqs.slice(0, 3);
  const roles = heavy ? page.roles : page.roles.slice(0, 3);
  const live = surface === "production";

  useEffect(() => {
    if (!live) return;
    const category = page.key === "us" ? "" : page.key;
    captureAttribution("us", {
      category,
      variant,
      lp_variant: variant,
      lp_version: TRUST_FIRST_PRODUCTION_LP_VERSION,
      baseline_label: US_BASELINE_LABEL,
    });
    trackLpView({
      market: "us",
      lp_version: TRUST_FIRST_PRODUCTION_LP_VERSION,
      baseline_label: US_BASELINE_LABEL,
      landing_page_type: TRUST_FIRST_PRODUCTION_LANDING_PAGE_TYPE,
      experiment_id: TRUST_FIRST_EXPERIMENT_ID,
      variant,
      split_running: false,
    });
  }, [live, page.key, variant]);

  return (
    <div className="tf">
      {live ? null : (
        <p className="tf-banner">Concept prototype · Preview only · Not a live Ads destination</p>
      )}
      <CompanyHeader ctaHref="#gate" ctaLabel={page.cta} />
      <main>
        <TrustHero page={page} variant={variant} surface={surface} />
        <div className="tf-strip-band">
          <div className="tf-wrap">
            <ProofStrip items={page.trustStrip} />
          </div>
        </div>
        {heavy ? <ReviewBadges /> : null}
        {page.key === "philippines-virtual-assistants" ? (
          <PhilippinesMarketFacts />
        ) : null}
        <HowItWorks steps={page.process} />
        <RoleOrTaskCards
          title={heavy ? "Work this seat can own" : "Typical seats"}
          items={roles}
        />
        <EmployerComparison
          rows={heavy ? page.comparison : page.comparison.slice(0, 4)}
          lead={page.comparisonLead}
        />
        {heavy ? <WhyVirtualCoworker items={page.whyItems} /> : null}
        {heavy ? <CompanyProof modules={page.proofModules} /> : null}
        {heavy ? <Testimonials limit={3} /> : null}
        {heavy ? <ObjectionHandling items={page.objections} /> : null}
        <FAQ items={faqs} />
        {heavy ? <BuiltForTrust /> : null}
        {heavy ? <PressRow /> : null}
      </main>
      <CompanyFooter surface={surface} />
    </div>
  );
}
