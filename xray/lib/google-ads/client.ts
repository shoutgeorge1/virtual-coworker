/**
 * Google Ads client — read-only GAQL via google-ads-api (Opteo).
 * Never mutates campaigns/ads/keywords.
 */

import { GoogleAdsApi } from "google-ads-api";
import { withRetry, QuotaExhaustedError } from "@/lib/sync/retry";
import { redactUnknown } from "@/lib/sync/redact";
import { currencyForMarket, microsToMajor } from "@/lib/sync/currency";
import type {
  AdGroupDayRow,
  CampaignDayRow,
  KeywordDayRow,
  Market,
  SearchTermDayRow,
} from "@/lib/sync/types";

export type GoogleAdsConfig = {
  developerToken: string;
  clientId: string;
  clientSecret: string;
  refreshToken: string;
  loginCustomerId: string;
  customerIdUs: string;
  customerIdAu: string;
};

export function parseGoogleAdsConfig(env: NodeJS.ProcessEnv = process.env): GoogleAdsConfig | null {
  const developerToken = (env.GOOGLE_ADS_DEVELOPER_TOKEN || "").trim();
  const clientId = (env.GOOGLE_ADS_CLIENT_ID || "").trim();
  const clientSecret = (env.GOOGLE_ADS_CLIENT_SECRET || "").trim();
  const refreshToken = (env.GOOGLE_ADS_REFRESH_TOKEN || "").trim();
  const loginCustomerId = normalizeCustomerId(env.GOOGLE_ADS_LOGIN_CUSTOMER_ID || "");
  const customerIdUs = normalizeCustomerId(
    env.GOOGLE_ADS_CUSTOMER_ID_US || env.GOOGLE_ADS_CUSTOMER_ID || "4967151855",
  );
  const customerIdAu = normalizeCustomerId(
    env.GOOGLE_ADS_CUSTOMER_ID_AU || "5735391940",
  );
  if (!developerToken || !clientId || !clientSecret || !refreshToken || !loginCustomerId) {
    return null;
  }
  return {
    developerToken,
    clientId,
    clientSecret,
    refreshToken,
    loginCustomerId,
    customerIdUs,
    customerIdAu,
  };
}

export function normalizeCustomerId(raw: string): string {
  return String(raw || "").replace(/\D/g, "");
}

function buildApi(cfg: GoogleAdsConfig): GoogleAdsApi {
  return new GoogleAdsApi({
    client_id: cfg.clientId,
    client_secret: cfg.clientSecret,
    developer_token: cfg.developerToken,
  });
}

function customerFor(cfg: GoogleAdsConfig, customerId: string) {
  return buildApi(cfg).Customer({
    customer_id: customerId,
    login_customer_id: cfg.loginCustomerId,
    refresh_token: cfg.refreshToken,
  });
}

function isQuota(err: unknown): boolean {
  const text = redactUnknown(err).toUpperCase();
  return text.includes("RESOURCE_EXHAUSTED") || text.includes("QUOTA");
}

export async function searchGaql(
  cfg: GoogleAdsConfig,
  customerId: string,
  query: string,
): Promise<Record<string, unknown>[]> {
  return withRetry(async () => {
    try {
      const customer = customerFor(cfg, customerId);
      const rows = await customer.query(query);
      return rows as unknown as Record<string, unknown>[];
    } catch (err) {
      if (isQuota(err)) {
        throw new QuotaExhaustedError(
          `Google Ads RESOURCE_EXHAUSTED for customer ${customerId}`,
        );
      }
      throw err;
    }
  });
}

function num(v: unknown): number {
  const n = Number(v ?? 0);
  return Number.isFinite(n) ? n : 0;
}

function str(v: unknown): string {
  return v == null ? "" : String(v);
}

function nest(obj: Record<string, unknown>, path: string[]): unknown {
  let cur: unknown = obj;
  for (const p of path) {
    if (!cur || typeof cur !== "object") return undefined;
    cur = (cur as Record<string, unknown>)[p];
  }
  return cur;
}

const VC_PREFIX: Record<Market, string> = {
  US: "VC_US_%",
  AU: "VC_AU_%",
};

export function campaignQuery(start: string, end: string, market: Market): string {
  return `
    SELECT
      campaign.id,
      campaign.name,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.conversions_value,
      metrics.all_conversions
    FROM campaign
    WHERE segments.date BETWEEN '${start}' AND '${end}'
      AND campaign.name LIKE '${VC_PREFIX[market]}'
      AND campaign.status != 'REMOVED'
  `.trim();
}

export function adGroupQuery(start: string, end: string, market: Market): string {
  return `
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.conversions_value
    FROM ad_group
    WHERE segments.date BETWEEN '${start}' AND '${end}'
      AND campaign.name LIKE '${VC_PREFIX[market]}'
      AND ad_group.status != 'REMOVED'
  `.trim();
}

export function keywordQuery(start: string, end: string, market: Market): string {
  return `
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      ad_group_criterion.criterion_id,
      ad_group_criterion.keyword.text,
      ad_group_criterion.keyword.match_type,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.conversions_value
    FROM keyword_view
    WHERE segments.date BETWEEN '${start}' AND '${end}'
      AND campaign.name LIKE '${VC_PREFIX[market]}'
      AND metrics.impressions > 0
  `.trim();
}

export function searchTermQuery(start: string, end: string, market: Market): string {
  return `
    SELECT
      campaign.name,
      ad_group.name,
      search_term_view.search_term,
      segments.keyword.info.text,
      segments.keyword.info.match_type,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions
    FROM search_term_view
    WHERE segments.date BETWEEN '${start}' AND '${end}'
      AND campaign.name LIKE '${VC_PREFIX[market]}'
      AND metrics.impressions > 0
  `.trim();
}

function costFrom(row: Record<string, unknown>): number {
  const metrics = (row.metrics || {}) as Record<string, unknown>;
  return microsToMajor(
    num(metrics.cost_micros ?? metrics.costMicros ?? nest(row, ["metrics", "cost_micros"])),
  );
}

export function normalizeCampaignRows(
  results: Record<string, unknown>[],
  market: Market,
  customerId: string,
): CampaignDayRow[] {
  const currency = currencyForMarket(market);
  return results.map((row) => {
    const campaign = (row.campaign || {}) as Record<string, unknown>;
    const segments = (row.segments || {}) as Record<string, unknown>;
    const metrics = (row.metrics || {}) as Record<string, unknown>;
    return {
      date: str(segments.date),
      market,
      customer_id: customerId,
      campaign_id: str(campaign.id),
      campaign_name: str(campaign.name),
      currency,
      impressions: num(metrics.impressions),
      clicks: num(metrics.clicks),
      cost: costFrom(row),
      conversions: num(metrics.conversions),
      conversions_value: num(metrics.conversions_value ?? metrics.conversionsValue),
      all_conversions: num(metrics.all_conversions ?? metrics.allConversions),
    };
  });
}

export function normalizeAdGroupRows(
  results: Record<string, unknown>[],
  market: Market,
  customerId: string,
): AdGroupDayRow[] {
  const currency = currencyForMarket(market);
  return results.map((row) => {
    const campaign = (row.campaign || {}) as Record<string, unknown>;
    const adGroup = (row.ad_group || row.adGroup || {}) as Record<string, unknown>;
    const segments = (row.segments || {}) as Record<string, unknown>;
    const metrics = (row.metrics || {}) as Record<string, unknown>;
    return {
      date: str(segments.date),
      market,
      customer_id: customerId,
      campaign_id: str(campaign.id),
      campaign_name: str(campaign.name),
      ad_group_id: str(adGroup.id),
      ad_group_name: str(adGroup.name),
      currency,
      impressions: num(metrics.impressions),
      clicks: num(metrics.clicks),
      cost: costFrom(row),
      conversions: num(metrics.conversions),
      conversions_value: num(metrics.conversions_value ?? metrics.conversionsValue),
    };
  });
}

export function normalizeKeywordRows(
  results: Record<string, unknown>[],
  market: Market,
  customerId: string,
): KeywordDayRow[] {
  const currency = currencyForMarket(market);
  return results.map((row) => {
    const campaign = (row.campaign || {}) as Record<string, unknown>;
    const adGroup = (row.ad_group || row.adGroup || {}) as Record<string, unknown>;
    const crit = (row.ad_group_criterion || row.adGroupCriterion || {}) as Record<string, unknown>;
    const kw = (crit.keyword || {}) as Record<string, unknown>;
    const segments = (row.segments || {}) as Record<string, unknown>;
    const metrics = (row.metrics || {}) as Record<string, unknown>;
    const match = kw.match_type ?? kw.matchType;
    return {
      date: str(segments.date),
      market,
      customer_id: customerId,
      campaign_id: str(campaign.id),
      campaign_name: str(campaign.name),
      ad_group_id: str(adGroup.id),
      ad_group_name: str(adGroup.name),
      criterion_id: str(crit.criterion_id ?? crit.criterionId),
      keyword_text: str(kw.text),
      match_type: str(match),
      currency,
      impressions: num(metrics.impressions),
      clicks: num(metrics.clicks),
      cost: costFrom(row),
      conversions: num(metrics.conversions),
      conversions_value: num(metrics.conversions_value ?? metrics.conversionsValue),
    };
  });
}

export function normalizeSearchTermRows(
  results: Record<string, unknown>[],
  market: Market,
  customerId: string,
): SearchTermDayRow[] {
  const currency = currencyForMarket(market);
  return results.map((row) => {
    const campaign = (row.campaign || {}) as Record<string, unknown>;
    const adGroup = (row.ad_group || row.adGroup || {}) as Record<string, unknown>;
    const st = (row.search_term_view || row.searchTermView || {}) as Record<string, unknown>;
    const segments = (row.segments || {}) as Record<string, unknown>;
    const kwInfo =
      ((segments.keyword as Record<string, unknown> | undefined)?.info as Record<
        string,
        unknown
      >) || {};
    const metrics = (row.metrics || {}) as Record<string, unknown>;
    return {
      date: str(segments.date),
      market,
      customer_id: customerId,
      campaign_name: str(campaign.name),
      ad_group_name: str(adGroup.name),
      search_term: str(st.search_term ?? st.searchTerm),
      keyword_text: str(kwInfo.text),
      match_type: str(kwInfo.match_type ?? kwInfo.matchType),
      currency,
      impressions: num(metrics.impressions),
      clicks: num(metrics.clicks),
      cost: costFrom(row),
      conversions: num(metrics.conversions),
    };
  });
}

export type GoogleAdsPullResult = {
  campaigns: CampaignDayRow[];
  adGroups: AdGroupDayRow[];
  keywords: KeywordDayRow[];
  searchTerms: SearchTermDayRow[];
  errors: string[];
};

export async function pullGoogleAdsWindow(
  cfg: GoogleAdsConfig,
  start: string,
  end: string,
  _opts: { fetchImpl?: typeof fetch } = {},
): Promise<GoogleAdsPullResult> {
  const out: GoogleAdsPullResult = {
    campaigns: [],
    adGroups: [],
    keywords: [],
    searchTerms: [],
    errors: [],
  };

  const markets: Array<{ market: Market; customerId: string }> = [
    { market: "US", customerId: cfg.customerIdUs },
    { market: "AU", customerId: cfg.customerIdAu },
  ];

  for (const { market, customerId } of markets) {
    const jobs: Array<{
      name: string;
      query: string;
      apply: (rows: Record<string, unknown>[]) => void;
    }> = [
      {
        name: `${market}_campaigns`,
        query: campaignQuery(start, end, market),
        apply: (rows) => {
          out.campaigns.push(...normalizeCampaignRows(rows, market, customerId));
        },
      },
      {
        name: `${market}_ad_groups`,
        query: adGroupQuery(start, end, market),
        apply: (rows) => {
          out.adGroups.push(...normalizeAdGroupRows(rows, market, customerId));
        },
      },
      {
        name: `${market}_keywords`,
        query: keywordQuery(start, end, market),
        apply: (rows) => {
          out.keywords.push(...normalizeKeywordRows(rows, market, customerId));
        },
      },
      {
        name: `${market}_search_terms`,
        query: searchTermQuery(start, end, market),
        apply: (rows) => {
          out.searchTerms.push(...normalizeSearchTermRows(rows, market, customerId));
        },
      },
    ];

    for (const job of jobs) {
      try {
        const rows = await searchGaql(cfg, customerId, job.query);
        job.apply(rows);
      } catch (err) {
        if (err instanceof QuotaExhaustedError) {
          out.errors.push(redactUnknown(err));
          return out;
        }
        out.errors.push(`${job.name}: ${redactUnknown(err)}`);
      }
    }
  }

  return out;
}
