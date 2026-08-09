import type { ReactNode } from "react";

function escapeRe(s: string) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/** Renders a client quote with optional bold / extra-large words. */
export default function QuoteBody({
  quote,
  pop = [],
  boom,
}: {
  quote: string;
  pop?: readonly string[];
  boom?: string;
}): ReactNode {
  const tokens = [...pop, ...(boom ? [boom] : [])];
  if (tokens.length === 0) return quote;

  const sorted = [...tokens].sort((a, b) => b.length - a.length);
  const re = new RegExp(`(${sorted.map(escapeRe).join("|")})`, "gi");
  const parts = quote.split(re);
  const boomLower = boom?.toLowerCase();
  const popLower = new Set(pop.map((p) => p.toLowerCase()));

  return (
    <>
      {parts.map((part, i) => {
        const key = `${i}-${part.slice(0, 16)}`;
        const lower = part.toLowerCase();
        if (boomLower && lower === boomLower) {
          return (
            <em key={key} className="trust-quote-boom">
              {part}
            </em>
          );
        }
        if (popLower.has(lower)) {
          return (
            <strong key={key} className="trust-quote-pop">
              {part}
            </strong>
          );
        }
        return <span key={key}>{part}</span>;
      })}
    </>
  );
}
