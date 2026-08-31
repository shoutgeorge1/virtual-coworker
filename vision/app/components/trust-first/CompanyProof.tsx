import { VERIFIED_PROOF, type TrustFirstCard } from "../../../config/trust-first";

export default function CompanyProof({
  modules,
}: {
  modules: readonly TrustFirstCard[];
}) {
  return (
    <section className="tf-section">
      <div className="tf-wrap">
        <p className="tf-section-kicker">Company</p>
        <h2>What we can show without inventing numbers</h2>
        <div className="tf-grid-2">
          {modules.map((item) => (
            <article className="tf-item" key={item.title}>
              <h3>{item.title}</h3>
              <p>{item.body}</p>
            </article>
          ))}
        </div>
        <p className="tf-muted" style={{ margin: "1rem 0 0" }}>
          {VERIFIED_PROOF.linkedinDisplay} on LinkedIn. {VERIFIED_PROOF.facebookDisplay} on
          Facebook. Floors confirmed in company records, not live scrapes on this page.
        </p>
      </div>
    </section>
  );
}
