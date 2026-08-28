/**
 * Executive monthly report — canonical metric definitions.
 *
 * Do not mix sales-labeled, Zoho census, and Google Ads actions without labels.
 * Blended unit economics = Ads spend ÷ validated sales outcomes (not Ads CPA).
 * Paid CPA only when a sales record has an approved click id (gclid / gbraid / wbraid).
 */

export type Market = "US" | "AU";
export type Currency = "USD" | "AUD";

export type MetricStatus =
  | "ok"
  | "pending"
  | "zero_denom"
  | "not_reliable"
  | "value_pending"
  | "no_compare";

export interface RatioResult {
  value: number | null;
  status: MetricStatus;
  numerator: number | null;
  denominator: number | null;
}

export interface PeriodBounds {
  start: string; // YYYY-MM-DD
  end: string;
  asOf: string;
  partial: boolean;
  label: string;
  statusLabel: string; // e.g. "Month to date · Partial through Aug 27"
}

export interface AdsTotals {
  spend: number;
  clicks: number;
  impressions: number;
  ctrPct: number | null;
  avgCpc: number | null;
  currency: Currency;
  source: "Ads";
}

export interface FunnelCounts {
  enquiries: number | null;
  discoveries: number | null;
  jobOrders: number | null;
  placements: number | null;
  enquiriesPending?: boolean;
  source: "Sales labeled" | "Pending";
}

export interface AttributionCoverage {
  paidAttributed: number;
  validatedSalesRecords: number;
  coverage: number | null;
  status: MetricStatus;
  display: string;
}

export interface AgencyRates {
  currency: Currency;
  baselineWindow: string;
  basis: string;
  blendedCostPerEnquiry: number | null;
  blendedCostPerDiscovery: number | null;
  blendedCostPerJobOrder: number | null;
  blendedCostPerPlacement: number | null;
  enquiriesPerThousand: number | null;
  discoveriesPerThousand: number | null;
  jobOrdersPerThousand: number | null;
  placementsPerThousand: number | null;
  ctrPct: number | null;
  avgCpc: number | null;
  typical7dSpend: number | null;
}

export interface CompareCell {
  pilot: number | null;
  agency: number | null;
  differencePct: number | null;
  interpretation: string;
  tone: "good" | "bad" | "neutral";
  pilotPeriod: string;
  agencyPeriod: string;
  metricKind: "rate" | "average" | "normalized_run_rate";
}

/** Safe division — never Infinity / NaN. Zero denom → null + zero_denom. */
export function safeDiv(
  numerator: number | null | undefined,
  denominator: number | null | undefined,
): RatioResult {
  if (numerator == null || denominator == null || Number.isNaN(Number(numerator))) {
    return { value: null, status: "pending", numerator: numerator ?? null, denominator: denominator ?? null };
  }
  const n = Number(numerator);
  const d = Number(denominator);
  if (!Number.isFinite(n) || !Number.isFinite(d)) {
    return { value: null, status: "pending", numerator: n, denominator: d };
  }
  if (d === 0) {
    return { value: null, status: "zero_denom", numerator: n, denominator: d };
  }
  return { value: n / d, status: "ok", numerator: n, denominator: d };
}

export function blendedCostPerEnquiry(spend: number | null, enquiries: number | null): RatioResult {
  return safeDiv(spend, enquiries);
}

export function blendedCostPerDiscovery(spend: number | null, discoveries: number | null): RatioResult {
  return safeDiv(spend, discoveries);
}

export function blendedCostPerJobOrder(spend: number | null, jobOrders: number | null): RatioResult {
  return safeDiv(spend, jobOrders);
}

export function blendedCostPerPlacement(spend: number | null, placements: number | null): RatioResult {
  return safeDiv(spend, placements);
}

/** Outcomes per $1,000 Ads spend. */
export function perThousand(
  outcomes: number | null,
  spend: number | null,
): RatioResult {
  if (outcomes == null || spend == null) {
    return { value: null, status: "pending", numerator: outcomes, denominator: spend };
  }
  if (spend === 0) {
    return { value: null, status: "zero_denom", numerator: outcomes, denominator: spend };
  }
  return {
    value: (outcomes / spend) * 1000,
    status: "ok",
    numerator: outcomes,
    denominator: spend,
  };
}

export function attributionCoverage(
  paidAttributed: number | null | undefined,
  validatedSalesRecords: number | null | undefined,
  minReliable = 0.4,
  minSample = 10,
): AttributionCoverage {
  const paid = Number(paidAttributed ?? 0);
  const total = Number(validatedSalesRecords ?? 0);
  if (total <= 0) {
    return {
      paidAttributed: paid,
      validatedSalesRecords: total,
      coverage: null,
      status: "pending",
      display: "Not reliable yet",
    };
  }
  const coverage = paid / total;
  const reliable = total >= minSample && coverage >= minReliable;
  return {
    paidAttributed: paid,
    validatedSalesRecords: total,
    coverage,
    status: reliable ? "ok" : "not_reliable",
    display: reliable
      ? `${Math.round(coverage * 100)}%`
      : "Not reliable yet",
  };
}

export function currencyForMarket(market: Market): Currency {
  return market === "AU" ? "AUD" : "USD";
}

export function monthBounds(
  asOfIso: string,
  monthKey?: string,
): PeriodBounds {
  const asOf = asOfIso.slice(0, 10);
  const key = monthKey || asOf.slice(0, 7);
  const [y, m] = key.split("-").map(Number);
  const start = `${key}-01`;
  const lastDay = new Date(Date.UTC(y, m, 0)).getUTCDate();
  const monthEnd = `${key}-${String(lastDay).padStart(2, "0")}`;
  const isCurrent = asOf.slice(0, 7) === key;
  const end = isCurrent && asOf < monthEnd ? asOf : monthEnd;
  const partial = end < monthEnd;
  const monthName = new Date(Date.UTC(y, m - 1, 1)).toLocaleString("en-US", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  });
  const through = new Date(end + "T12:00:00Z").toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
  return {
    start,
    end,
    asOf,
    partial,
    label: partial ? `${monthName} to date` : monthName,
    statusLabel: partial
      ? `Month to date · Partial through ${through}`
      : `Completed month · frozen`,
  };
}

/** Elapsed days in a partial month (inclusive). */
export function elapsedDays(start: string, end: string): number {
  const a = Date.parse(start + "T12:00:00Z");
  const b = Date.parse(end + "T12:00:00Z");
  if (!Number.isFinite(a) || !Number.isFinite(b) || b < a) return 0;
  return Math.round((b - a) / 86_400_000) + 1;
}

export interface ByDateRow {
  cost_usd?: number;
  clicks?: number;
  impressions?: number;
}

/** Sum Stage-1 Ads by_date for [start, end] inclusive. AU cost_usd is AUD. */
export function sumAdsByDate(
  byDate: Record<string, ByDateRow> | null | undefined,
  start: string,
  end: string,
  currency: Currency,
): AdsTotals | null {
  if (!byDate) return null;
  let spend = 0;
  let clicks = 0;
  let impressions = 0;
  let any = false;
  for (const [d, row] of Object.entries(byDate)) {
    if (d >= start && d <= end) {
      any = true;
      spend += Number(row.cost_usd || 0);
      clicks += Number(row.clicks || 0);
      impressions += Number(row.impressions || 0);
    }
  }
  if (!any) return null;
  return {
    spend,
    clicks,
    impressions,
    ctrPct: impressions > 0 ? (100 * clicks) / impressions : null,
    avgCpc: clicks > 0 ? spend / clicks : null,
    currency,
    source: "Ads",
  };
}

export interface SalesOpsSlice {
  window_start?: string;
  window_end?: string;
  enquiries?: number | null;
  sales_calls_completed?: number | null;
  job_orders_total?: number | null;
  placements?: number | null;
  caveat?: string | null;
}

function isEnquiryPending(ops: SalesOpsSlice | null | undefined): boolean {
  if (!ops) return true;
  const caveat = String(ops.caveat || "").toLowerCase();
  if (caveat.includes("count pending") || caveat.includes("enquiry count pending")) {
    return true;
  }
  return ops.enquiries == null;
}

function addNullable(a: number | null, b: number | null): number | null {
  if (a == null && b == null) return null;
  return Number(a || 0) + Number(b || 0);
}

/**
 * Sum non-overlapping sales-ops slices that fall inside [start, end].
 * Skips slices whose window is entirely outside the period.
 * Does not force unconfirmed downstream stages to 0 if null.
 */
export function sumSalesLabeled(
  slices: Array<SalesOpsSlice | null | undefined>,
  start: string,
  end: string,
): FunnelCounts {
  let enquiries: number | null = null;
  let discoveries: number | null = null;
  let jobOrders: number | null = null;
  let placements: number | null = null;
  let anyPending = false;
  let any = false;

  for (const ops of slices) {
    if (!ops) continue;
    const ws = (ops.window_start || "").slice(0, 10);
    const we = (ops.window_end || "").slice(0, 10);
    if (!ws || !we) continue;
    if (we < start || ws > end) continue;
    any = true;
    if (isEnquiryPending(ops)) {
      anyPending = true;
    } else {
      enquiries = addNullable(enquiries, ops.enquiries ?? null);
    }
    if (ops.sales_calls_completed != null) {
      discoveries = addNullable(discoveries, ops.sales_calls_completed);
    }
    if (ops.job_orders_total != null) {
      jobOrders = addNullable(jobOrders, ops.job_orders_total);
    }
    if (ops.placements != null) {
      placements = addNullable(placements, ops.placements);
    }
  }

  if (!any) {
    return {
      enquiries: null,
      discoveries: null,
      jobOrders: null,
      placements: null,
      enquiriesPending: true,
      source: "Pending",
    };
  }

  return {
    enquiries: anyPending && enquiries == null ? null : enquiries,
    discoveries,
    jobOrders,
    placements,
    enquiriesPending: anyPending && enquiries == null,
    source: anyPending && enquiries == null ? "Pending" : "Sales labeled",
  };
}

/** Month-over-month: only when a prior pilot month exists. Partial → same elapsed days. */
export function monthOverMonthCompare(
  current: number | null,
  prior: number | null,
  opts: {
    hasPriorPilotMonth: boolean;
    currentPartial: boolean;
    higherIsBetter: boolean;
  },
): { text: string; tone: "good" | "bad" | "neutral"; status: MetricStatus } {
  if (!opts.hasPriorPilotMonth) {
    return {
      text: "First pilot month — no prior monthly comparison",
      tone: "neutral",
      status: "no_compare",
    };
  }
  if (current == null || prior == null) {
    return { text: "—", tone: "neutral", status: "pending" };
  }
  if (prior === 0) {
    return { text: "—", tone: "neutral", status: "zero_denom" };
  }
  const pct = ((current - prior) / Math.abs(prior)) * 100;
  if (Math.abs(pct) < 2) {
    return { text: "≈ flat", tone: "neutral", status: "ok" };
  }
  const improved = pct > 0 ? opts.higherIsBetter : !opts.higherIsBetter;
  const dir = pct > 0 ? "↑" : "↓";
  return {
    text: `${dir} ${Math.abs(Math.round(pct))}%${opts.currentPartial ? " (same elapsed days)" : ""}`,
    tone: improved ? "good" : "bad",
    status: "ok",
  };
}

/**
 * Pilot vs agency on rate metrics. Prefer period-independent rates.
 * Lower cost / higher yield → good for pilot.
 */
export function compareRateToAgency(
  pilot: number | null,
  agency: number | null,
  opts: {
    lowerIsBetter: boolean;
    pilotPeriod: string;
    agencyPeriod: string;
    materialPct?: number;
  },
): CompareCell {
  const material = opts.materialPct ?? 15;
  if (pilot == null || agency == null || agency === 0) {
    return {
      pilot,
      agency,
      differencePct: null,
      interpretation: pilot == null ? "Pilot sample incomplete" : "Agency rate unavailable",
      tone: "neutral",
      pilotPeriod: opts.pilotPeriod,
      agencyPeriod: opts.agencyPeriod,
      metricKind: "rate",
    };
  }
  const diffPct = ((pilot - agency) / Math.abs(agency)) * 100;
  const improved = opts.lowerIsBetter ? pilot < agency : pilot > agency;
  const materialEnough = Math.abs(diffPct) >= material;
  let interpretation: string;
  let tone: "good" | "bad" | "neutral" = "neutral";
  if (!materialEnough) {
    interpretation = "Roughly in line with agency rate";
  } else if (improved) {
    interpretation = opts.lowerIsBetter
      ? "Pilot materially more efficient"
      : "Pilot materially higher yield";
    tone = "good";
  } else {
    interpretation = opts.lowerIsBetter
      ? "Pilot materially less efficient"
      : "Pilot materially lower yield";
    tone = "bad";
  }
  return {
    pilot,
    agency,
    differencePct: diffPct,
    interpretation,
    tone,
    pilotPeriod: opts.pilotPeriod,
    agencyPeriod: opts.agencyPeriod,
    metricKind: "rate",
  };
}

/** Period activity conversion — not a mature acquisition cohort. */
export function periodActivityRate(
  from: number | null,
  to: number | null,
): RatioResult & { label: string } {
  const r = safeDiv(to, from);
  return {
    ...r,
    label: "Period activity — not a mature acquisition cohort",
  };
}

export function formatMoney(
  value: number | null | undefined,
  currency: Currency,
  digits = 0,
): string {
  if (value == null || Number.isNaN(Number(value))) return "—";
  const prefix = currency === "AUD" ? "A$" : "$";
  return (
    prefix +
    Number(value).toLocaleString("en-US", {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    })
  );
}

export function formatNum(value: number | null | undefined, digits = 0): string {
  if (value == null || Number.isNaN(Number(value))) return "—";
  return Number(value).toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function formatRatioDisplay(r: RatioResult, currency: Currency, digits = 2): string {
  if (r.status === "zero_denom" || r.status === "pending" || r.value == null) return "—";
  return formatMoney(r.value, currency, digits);
}
