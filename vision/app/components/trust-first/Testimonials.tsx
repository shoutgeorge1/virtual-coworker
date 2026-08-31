import { APPROVED_TESTIMONIALS } from "../../../config/trust-first";

function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("");
}

export default function Testimonials({ limit = 2 }: { limit?: number }) {
  const quotes = APPROVED_TESTIMONIALS.slice(0, limit);
  return (
    <section className="tf-section">
      <div className="tf-wrap">
        <p className="tf-section-kicker">Clients</p>
        <h2>From published client stories</h2>
        <div className="tf-grid-2">
          {quotes.map((item) => (
            <blockquote className="tf-item" key={`${item.name}-${item.company}`}>
              <p className="tf-quote">“{item.quote}”</p>
              <footer className="tf-quote-by">
                <span className="tf-avatar" aria-hidden="true">
                  {initials(item.name)}
                </span>
                <span>
                  {item.name}
                  {item.role ? `, ${item.role}` : ""}
                  {item.company ? ` · ${item.company}` : ""}
                </span>
              </footer>
            </blockquote>
          ))}
        </div>
      </div>
    </section>
  );
}
