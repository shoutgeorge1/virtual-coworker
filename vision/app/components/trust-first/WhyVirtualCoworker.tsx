import type { TrustFirstCard } from "../../../config/trust-first";

export default function WhyVirtualCoworker({
  items,
}: {
  items: readonly TrustFirstCard[];
}) {
  return (
    <section className="tf-section">
      <div className="tf-wrap">
        <p className="tf-section-kicker">Why Virtual Coworker</p>
        <h2>A staffing company, not a freelance app</h2>
        <div className="tf-grid-3">
          {items.map((item) => (
            <article className="tf-item" key={item.title}>
              <h3>{item.title}</h3>
              <p>{item.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
