import { pressMarksForMarket } from "../../../config/site";

const SKIP = new Set(["google", "clutch-us", "smh", "zoho"]);

export default function PressRow() {
  const marks = pressMarksForMarket("us").filter((mark) => !SKIP.has(mark.id));
  return (
    <section className="tf-section">
      <div className="tf-wrap">
        <p className="tf-section-kicker">As featured in</p>
        <h2>Press and awards we can actually show</h2>
        <p className="tf-muted" style={{ marginBottom: "0.9rem" }}>
          Company marks already on Virtual Coworker pages. Display only. No outbound links.
        </p>
        <div className="tf-press" aria-label="Press and awards">
          {marks.map((mark) => (
            // eslint-disable-next-line @next/next/no-img-element
            <img key={mark.id} src={mark.src} alt={mark.alt} />
          ))}
        </div>
      </div>
    </section>
  );
}
