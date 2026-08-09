import type { EmployerFaqItem } from "../../config/employer-cro";

/** Scannable FAQ — tap a question, don’t wade through a card grid. */
export default function FaqAccordion({
  items,
  light = false,
}: {
  items: EmployerFaqItem[];
  light?: boolean;
}) {
  if (items.length === 0) return null;
  return (
    <div className={`faq-acc${light ? " faq-acc-light" : ""}`}>
      {items.map((item, i) => (
        <details className="faq-acc-item" key={item.q} open={i === 0}>
          <summary>{item.q}</summary>
          <p>{item.a}</p>
        </details>
      ))}
    </div>
  );
}
