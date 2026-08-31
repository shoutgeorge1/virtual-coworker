import { COMPANY_IDENTITY, SITE } from "../../../config/site";
import { JOB_SEEKER_DIVERSION, VERIFIED_PROOF } from "../../../config/trust-first";

export default function CompanyFooter({
  surface = "preview",
}: {
  surface?: "preview" | "production";
}) {
  return (
    <footer className="tf-footer">
      <div className="tf-wrap tf-footer-grid">
        <div>
          <p>
            <strong>{SITE.name}</strong>
          </p>
          <p>{SITE.disclaimer}</p>
          <p>
            Founded {VERIFIED_PROOF.foundedYear} by {COMPANY_IDENTITY.founderName}.
          </p>
        </div>
        <div>
          <p>
            <strong>US office</strong>
            <br />
            {SITE.addressUs}
          </p>
          <p>
            <strong>Call</strong>
            <br />
            <a
              href={VERIFIED_PROOF.phoneHref}
              data-track="phone_cta_clicked"
              data-market="us"
              data-cta-location="footer"
            >
              {SITE.usPhoneDisplay}
            </a>
          </p>
        </div>
        <div>
          <p className="tf-footer-legal">
            <a href="/privacy">Privacy Policy</a>
            <a href="/terms">Terms</a>
            {surface === "preview" ? (
              <a href="/preview/trust-first/trust-center">Trust center</a>
            ) : null}
            <a href={VERIFIED_PROOF.careersUrl}>{JOB_SEEKER_DIVERSION.cta}</a>
          </p>
          <p>{SITE.copyright}</p>
        </div>
      </div>
    </footer>
  );
}
