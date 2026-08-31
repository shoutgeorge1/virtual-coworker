/**
 * Keep GCLID / UTM / variant query string when linking within the microsite.
 */

/** Append current window.search onto a path (client only). */
export function withCurrentSearch(path: string): string {
  if (typeof window === "undefined") return path;
  const qs = window.location.search;
  if (!qs || qs === "?") return path;
  const base = path.split("#")[0];
  const hash = path.includes("#") ? `#${path.split("#").slice(1).join("#")}` : "";
  if (base.includes("?")) {
    const [p, existing] = base.split("?");
    const merged = new URLSearchParams(existing);
    const incoming = new URLSearchParams(qs);
    incoming.forEach((value, key) => {
      if (!merged.has(key)) merged.set(key, value);
    });
    const out = merged.toString();
    return out ? `${p}?${out}${hash}` : `${p}${hash}`;
  }
  return `${base}${qs}${hash}`;
}

/** Direct employer Calendly booking path for a market. */
export function bookPathForMarket(market: "us" | "au"): string {
  return market === "au" ? "/au/book" : "/us/book";
}
