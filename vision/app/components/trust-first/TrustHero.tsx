import type { TrustFirstPageConfig } from "../../../config/trust-first";
import EmployerQualificationForm from "./EmployerQualificationForm";
import type { TrustFirstVariant } from "../../../config/trust-first";

export default function TrustHero({
  page,
  variant,
}: {
  page: TrustFirstPageConfig;
  variant: TrustFirstVariant;
}) {
  return (
    <section className="tf-hero" id="top">
      <div className="tf-wrap tf-hero-grid">
        <div>
          <p className="tf-eyebrow">{page.eyebrow}</p>
          <h1 className="tf-h1">{page.h1}</h1>
          <p className="tf-lead">{page.supporting}</p>
          <ul className="tf-bullets">
            {page.heroBullets.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <EmployerQualificationForm page={page} variant={variant} />
      </div>
    </section>
  );
}
