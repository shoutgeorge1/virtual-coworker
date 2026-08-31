import type { MarketId } from "../../config/markets";
import { pressMarksForMarket } from "../../config/site";

/**
 * Standalone “Featured in” press/awards strip.
 * Same layout language as the TrustBand client logo strip —
 * white panel, equal flex cells, constrained width. Display-only.
 */
export default function PressBand({
  light = false,
  market = "us",
}: {
  light?: boolean;
  market?: MarketId;
}) {
  const marks = pressMarksForMarket(market);
  if (marks.length === 0) return null;
  return (
    <section
      className={`press-band${light ? " press-band-light" : ""}`}
      aria-label="Press and awards"
    >
      <div className="press-band-inner">
        <p className="trust-press-label">As featured in</p>
        <ul className="trust-press-row">
          {marks.map((p) => (
            <li className={`trust-press-mark is-${p.id}`} key={p.id}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={p.src} alt={p.alt} loading="lazy" />
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
