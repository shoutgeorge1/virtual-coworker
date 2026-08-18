import { APPROVED_TESTIMONIALS } from "../../../config/trust-first";

export default function Testimonials({ limit = 2 }: { limit?: number }) {
  const quotes = APPROVED_TESTIMONIALS.slice(0, limit);
  return (
    <section className="tf-section tf-section-alt">
      <div className="tf-wrap">
        <p className="tf-section-kicker">Clients</p>
        <h2>From published client stories</h2>
        <div className="tf-grid-2">
          {quotes.map((item) => (
            <blockquote className="tf-item" key={`${item.name}-${item.company}`}>
              <p className="tf-quote">“{item.quote}”</p>
              <footer>
                {item.name}
                {item.role ? `, ${item.role}` : ""}
                {item.company ? ` · ${item.company}` : ""}
              </footer>
            </blockquote>
          ))}
        </div>
      </div>
    </section>
  );
}
