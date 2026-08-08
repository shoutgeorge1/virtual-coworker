import { PRESS_MARKS } from "../../config/site";

/**
 * Standalone “Featured in” press/awards strip.
 * Kept out of TrustBand so client logos + reviews aren’t crowded.
 * Display-only — no outbound links.
 */
export default function PressBand({ light = false }: { light?: boolean }) {
  return (
    <section
      className={`press-band${light ? " press-band-light" : ""}`}
      aria-label="Press and awards"
    >
      <div className="press-band-inner">
        <p className="trust-press-label">Featured in</p>
        <ul className="trust-press-row">
          {PRESS_MARKS.map((p) => (
            <li
              className={`trust-press-mark${p.wide ? " is-wide" : ""}`}
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
