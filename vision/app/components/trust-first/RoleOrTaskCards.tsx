import type { TrustFirstCard } from "../../../config/trust-first";

export default function RoleOrTaskCards({
  title,
  items,
}: {
  title: string;
  items: readonly TrustFirstCard[];
}) {
  return (
    <section className="tf-section">
      <div className="tf-wrap">
        <p className="tf-section-kicker">Roles</p>
        <h2>{title}</h2>
        <div className="tf-grid-2">
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
