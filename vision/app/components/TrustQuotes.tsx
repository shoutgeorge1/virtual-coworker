import { PUBLIC_QUOTES } from "../../config/site";
import type { MarketId } from "../../config/markets";

export default function TrustQuotes({
  light = false,
  market = "us",
}: {
  light?: boolean;
  market?: MarketId;
}) {
  const isAu = market === "au";

  return (
    <section className={`trust-quotes${light ? " trust-quotes-light" : ""}`}>
      <div className="trust-quotes-inner">
        <p className="trust-quotes-label">
          {isAu ? "From Australian & global clients" : "From clients"}
        </p>
        <h2>
          {isAu
            ? "Businesses that hired through Virtual Coworker."
            : "Businesses that hired through Virtual Coworker."}
        </h2>
        <div className="trust-quotes-grid">
          {PUBLIC_QUOTES.map((q) => (
            <figure className="trust-quote-card" key={q.name}>
              <blockquote>“{q.quote}”</blockquote>
              <figcaption>
                <b>{q.name}</b>
                <span>{q.role}</span>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
