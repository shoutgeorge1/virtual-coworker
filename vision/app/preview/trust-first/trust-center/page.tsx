import type { Metadata } from "next";
import { COMPANY_IDENTITY, SITE } from "../../../../config/site";
import { VERIFIED_PROOF } from "../../../../config/trust-first";
import { previewRobots } from "../../../../lib/trust-first";
import CompanyFooter from "../../../components/trust-first/CompanyFooter";
import CompanyHeader from "../../../components/trust-first/CompanyHeader";

export const metadata: Metadata = {
  title: "Trust center (Preview) | Virtual Coworker",
  robots: previewRobots(),
};

export default function TrustCenterPreviewPage() {
  return (
    <div className="tf">
      <p className="tf-banner">Concept prototype · Preview only · Not a live Ads destination</p>
      <CompanyHeader ctaHref="/preview/trust-first/us#gate" ctaLabel="Book a strategy call" />
      <main>
        <section className="tf-section">
          <div className="tf-wrap" style={{ maxWidth: 720 }}>
            <p className="tf-section-kicker">Trust center</p>
            <h1 className="tf-h1">How Virtual Coworker hires, and what we will not claim</h1>
            <p className="tf-lead">
              {SITE.name} has staffed dedicated Filipino teammates since {VERIFIED_PROOF.foundedYear}.
              Founded by {COMPANY_IDENTITY.founderName}. This page is a preview. It is not a
              certification report.
            </p>
            <h2>How hiring works</h2>
            <p className="tf-muted">
              We recruit and vet. You interview the shortlist. Nobody starts until you say yes.
              After you hire, we employ them and handle payroll. This is a staffing company, not a
              freelance marketplace.
            </p>
            <h2>Offices</h2>
            <p className="tf-muted">
              {SITE.addressUs}. {SITE.addressAu}. {SITE.addressPhLabel}.
            </p>
            <h2>Data and legal</h2>
            <p className="tf-muted">
              Hiring forms on this preview stay on this host. Live Privacy and Terms:
            </p>
            <p>
              <a href="/privacy">Privacy Policy</a>
              {" · "}
              <a href="/terms">Terms</a>
            </p>
            <h2>What this page does not include</h2>
            <p className="tf-muted">
              We do not publish SOC 2, HIPAA, or PCI claims here. Those are not documented for
              Virtual Coworker in this repo. We do not invent client counts or savings figures.
            </p>
            <p>
              <a href="/preview/trust-first">Back to the preview index</a>
            </p>
          </div>
        </section>
      </main>
      <CompanyFooter />
    </div>
  );
}
