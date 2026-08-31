/** Micros → major units; market currency labels. */

export type MarketCurrency = "USD" | "AUD";

export function currencyForMarket(market: string): MarketCurrency {
  const m = market.trim().toUpperCase();
  if (m === "AU" || m === "AUD" || m === "AUSTRALIA") return "AUD";
  return "USD";
}

/** Google Ads cost_micros → major currency units (not rounded for storage). */
export function microsToMajor(micros: number | string | null | undefined): number {
  if (micros === null || micros === undefined || micros === "") return 0;
  const n = typeof micros === "string" ? Number(micros) : micros;
  if (!Number.isFinite(n)) return 0;
  return n / 1_000_000;
}

/** Round for display / status payloads — not for idempotent storage keys. */
export function roundMoney(amount: number, digits = 2): number {
  if (!Number.isFinite(amount)) return 0;
  const f = 10 ** digits;
  return Math.round(amount * f) / f;
}

export function formatMoney(
  amount: number,
  currency: MarketCurrency,
  digits = 2,
): string {
  const n = roundMoney(amount, digits);
  const prefix = currency === "AUD" ? "A$" : "$";
  return `${prefix}${n.toFixed(digits)}`;
}
