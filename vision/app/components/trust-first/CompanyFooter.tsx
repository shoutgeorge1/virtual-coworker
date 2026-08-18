import { COMPANY_IDENTITY, SITE } from "../../../config/site";
import { JOB_SEEKER_DIVERSION, VERIFIED_PROOF } from "../../../config/trust-first";

export default function CompanyFooter() {
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
            <strong>Australia office</strong>
            <br />
            {SITE.addressAu}
          </p>
          <p>
            <strong>Philippines</strong>
            <br />
            {SITE.addressPhLabel}
          </p>
        </div>
        <div>
          <p>
            <a href={VERIFIED_PROOF.phoneHref}>{SITE.usPhoneDisplay}</a>
          </p>
          <p>
            <a href="/privacy">Privacy</a>
            {" · "}
            <a href="/terms">Terms</a>
          </p>
          <p>
            <a href={VERIFIED_PROOF.careersUrl}>{JOB_SEEKER_DIVERSION.cta}</a>
          </p>
          <p>{SITE.copyright}</p>
        </div>
      </div>
    </footer>
  );
}
