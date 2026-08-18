"use client";

import type { TrustFirstPageConfig, TrustFirstVariant } from "../../../config/trust-first";
import { isProofHeavy } from "../../../lib/trust-first";
import CompanyFooter from "./CompanyFooter";
import CompanyHeader from "./CompanyHeader";
import CompanyProof from "./CompanyProof";
import EmployerComparison from "./EmployerComparison";
import FAQ from "./FAQ";
import HowItWorks from "./HowItWorks";
import ObjectionHandling from "./ObjectionHandling";
import ProofStrip from "./ProofStrip";
import RoleOrTaskCards from "./RoleOrTaskCards";
import Testimonials from "./Testimonials";
import TrustHero from "./TrustHero";
import WhyVirtualCoworker from "./WhyVirtualCoworker";

export default function TrustFirstLanding({
  page,
  variant,
}: {
  page: TrustFirstPageConfig;
  variant: TrustFirstVariant;
}) {
  const heavy = isProofHeavy(variant);
  const faqs = heavy ? page.faqs : page.faqs.slice(0, 3);
  const roles = heavy ? page.roles : page.roles.slice(0, 3);

  return (
    <div className="tf">
      <p className="tf-banner">Concept prototype · Preview only · Not a live Ads destination</p>
      <CompanyHeader ctaHref="#gate" ctaLabel={page.cta} />
      <main>
        <TrustHero page={page} variant={variant} />
        <div className="tf-wrap">
          <ProofStrip items={page.trustStrip} />
        </div>
        <HowItWorks steps={page.process} />
        <RoleOrTaskCards
          title={heavy ? "Work this seat can own" : "Typical seats"}
          items={roles}
        />
        {heavy ? <WhyVirtualCoworker items={page.whyItems} /> : null}
        {heavy ? <EmployerComparison rows={page.comparison} /> : null}
        {heavy ? <CompanyProof modules={page.proofModules} /> : null}
        {heavy ? <Testimonials limit={3} /> : null}
        {heavy ? <ObjectionHandling items={page.objections} /> : null}
        <FAQ items={faqs} />
      </main>
      <CompanyFooter />
    </div>
  );
}
