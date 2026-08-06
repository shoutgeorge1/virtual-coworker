import { PUBLIC_QUOTES } from "../../config/site";

export default function TrustQuotes({ light = false }: { light?: boolean }) {
  return (
    <section className={`trust-quotes${light ? " trust-quotes-light" : ""}`}>
      <div className="trust-quotes-inner">
        <p className="trust-quotes-label">What clients say</p>
        <h2>Real client words — not invented for ads.</h2>
        <p className="trust-quotes-note">
          Short excerpts from published Virtual Coworker client stories. No star
          ratings or client counts added here.
        </p>
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
