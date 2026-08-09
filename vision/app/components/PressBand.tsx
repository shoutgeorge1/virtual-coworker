import type { MarketId } from "../../config/markets";
import { pressMarksForMarket } from "../../config/site";

/**
 * Standalone “Featured in” press/awards strip.
 * Display-only — no outbound links.
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
            <li
              className={`trust-press-mark${p.wide ? " is-wide" : ""}${
                p.id === "forbes"
                  ? " is-pop is-forbes"
                  : p.id === "clutch-us" || p.id === "google"
                    ? " is-pop"
                    : ""
              }${
                p.id === "smh" || p.id === "startupdaily" ? " is-masthead" : ""
              }${p.id === "startupsmart" ? " is-smart" : ""}${
                p.id === "anthill" ? " is-end" : ""
              }`}
              key={p.id}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={p.src} alt={p.alt} loading="lazy" />
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
