import { PH_MARKET_FACTS } from "../../../config/trust-first";

export default function PhilippinesMarketFacts() {
  return (
    <section className="tf-section">
      <div className="tf-wrap">
        <p className="tf-section-kicker">Philippines talent market</p>
        <h2>Why employers look to the Philippines</h2>
        <p className="tf-muted" style={{ marginBottom: "0.9rem" }}>
          These are public market facts, not Virtual Coworker company statistics.
        </p>
        <div className="tf-grid-2">
          {PH_MARKET_FACTS.map((fact) => (
            <article className="tf-item" key={fact.title}>
              <h3>{fact.title}</h3>
              <p>{fact.body}</p>
              <p className="tf-source">Source: {fact.sourceLabel}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
