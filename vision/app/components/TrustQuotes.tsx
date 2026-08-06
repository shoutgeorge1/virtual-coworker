import { PUBLIC_QUOTES, SITE } from "../../config/site";

export default function TrustQuotes({ light = false }: { light?: boolean }) {
  return (
    <section className={`trust-quotes${light ? " trust-quotes-light" : ""}`}>
      <div className="trust-quotes-inner">
        <p className="trust-quotes-label">What clients say</p>
        <h2>Published on virtualcoworker.com — not invented for ads.</h2>
        <p className="trust-quotes-note">
          Short excerpts from client stories on{" "}
          <a href={SITE.corporateUrl} rel="noopener noreferrer" target="_blank">
            virtualcoworker.com
          </a>
          . No star ratings or client counts added here.
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
