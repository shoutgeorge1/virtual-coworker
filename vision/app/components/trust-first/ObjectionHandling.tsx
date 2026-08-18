import type { TrustFirstFaq } from "../../../config/trust-first";

export default function ObjectionHandling({
  items,
}: {
  items: readonly TrustFirstFaq[];
}) {
  return (
    <section className="tf-section">
      <div className="tf-wrap">
        <p className="tf-section-kicker">Common questions</p>
        <h2>Straight answers before you call</h2>
        <div className="tf-grid-2">
          {items.map((item) => (
            <article className="tf-item" key={item.q}>
              <h3>{item.q}</h3>
              <p>{item.a}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
