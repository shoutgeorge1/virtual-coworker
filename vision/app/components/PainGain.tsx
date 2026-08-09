import type { MarketId } from "../../config/markets";
import {
  painGainCopy,
  painGainBooms,
  primaryHireCta,
} from "../../config/employer-cro";

/**
 * Compact pain → relief comparison for employer landings.
 * Sits after hero/trust, before the detailed hiring process.
 */
export default function PainGain({
  market,
  light = false,
  ctaHref = "#gate",
}: {
  market: MarketId;
  light?: boolean;
  /** Gate anchor on LPs; hub pages pass `/{market}#gate`. */
  ctaHref?: string;
}) {
  const copy = painGainCopy(market);
  const booms = painGainBooms(market);
  const shell = market === "us" ? "us" : "au";

  return (
    <section
      className={`pain-gain${light ? " pain-gain-light" : ""}`}
      aria-labelledby="pain-gain-title"
    >
      <div className="pain-gain-inner">
        <header className="pain-gain-head">
          <p className={market === "us" ? "us-proof-label" : "au-proof-label"}>
            {copy.eyebrow}
          </p>
          <h2 id="pain-gain-title">{copy.title}</h2>
          <p className="pain-gain-lead">{copy.lead}</p>
        </header>

        <div className="pain-gain-grid">
          <div className="pain-gain-col pain-gain-before">
            <h3>{copy.beforeLabel}</h3>
            <ul>
              {copy.before.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="pain-gain-col pain-gain-after">
            <h3>{copy.afterLabel}</h3>
            <ul>
              {copy.after.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>

        <ul className="pain-gain-booms">
          {booms.map((b) => (
            <li key={b.title}>
              <b>{b.title}</b>
              {b.body}
            </li>
          ))}
        </ul>
        <p className="pain-gain-foot">
          <a href={ctaHref} className={`${shell}-inline-cta`}>
            {primaryHireCta(market)} →
          </a>
        </p>
      </div>
    </section>
  );
}
