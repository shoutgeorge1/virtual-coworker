import { SITE } from "../../../config/site";
import { VERIFIED_PROOF } from "../../../config/trust-first";

export default function CompanyHeader({
  ctaHref,
  ctaLabel,
}: {
  ctaHref: string;
  ctaLabel: string;
}) {
  return (
    <header className="tf-header">
      <div className="tf-wrap tf-header-inner">
        <a className="tf-logo" href="#top" aria-label="Virtual Coworker">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/logo-vc.png" alt="Virtual Coworker" width={180} height={42} />
        </a>
        <div className="tf-header-right">
          <a className="tf-phone" href={VERIFIED_PROOF.phoneHref}>
            {SITE.usPhoneDisplay}
          </a>
          <a className="tf-header-cta" href={ctaHref}>
            {ctaLabel}
          </a>
        </div>
      </div>
    </header>
  );
}
