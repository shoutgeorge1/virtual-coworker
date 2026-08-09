import { PUBLIC_QUOTES } from "../../config/site";
import type { MarketId } from "../../config/markets";
import QuoteBody from "./QuoteBody";

/**
 * Standalone quote band — kept for reuse.
 * Market landings render quotes inside TrustBand (prominent, above the quiz).
 */
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
        <p className="trust-quotes-label">Happy customers</p>
        <h2>
          {isAu
            ? "What Australian & global clients say."
            : "What customers say after they hire."}
        </h2>
        <div className="trust-quotes-grid">
          {PUBLIC_QUOTES.map((q) => (
            <figure className="trust-quote-card" key={q.name}>
              <blockquote>
                “
                <QuoteBody quote={q.quote} pop={q.pop} boom={q.boom} />
                ”
              </blockquote>
              <figcaption>
                <b>{q.name}</b>
                <span>
                  {q.role}
                  {q.company ? ` · ${q.company}` : ""}
                </span>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
