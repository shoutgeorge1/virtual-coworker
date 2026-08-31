import type { TrustFirstFaq } from "../../../config/trust-first";

export default function FAQ({ items }: { items: readonly TrustFirstFaq[] }) {
  return (
    <section className="tf-section">
      <div className="tf-wrap tf-faq">
        <p className="tf-section-kicker">FAQ</p>
        <h2>Before you send the form</h2>
        {items.map((item) => (
          <details key={item.q}>
            <summary>{item.q}</summary>
            <p>{item.a}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
