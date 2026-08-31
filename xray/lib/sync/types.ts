/** Shared types for the read-only daily sync pipeline. */

import type { JoinMethod } from "./join";
import type { MarketCurrency } from "./currency";

export type Market = "US" | "AU";

export type SyncSource = "google_ads" | "ga4" | "zoho";

export type SourceFreshness = {
  source: SyncSource;
  last_success_at: string | null;
  window_start: string | null;
  window_end: string | null;
  row_counts: Record<string, number>;
  ok: boolean;
  error?: string;
};

export type DashboardStatus = {
  updated_at: string;
  last_successful_sync_at: string | null;
  last_sync_run_id: string | null;
  window_start: string | null;
  window_end: string | null;
  freshness: SourceFreshness[];
  row_counts: Record<string, number>;
  partial_failures: Array<{ source: SyncSource; error: string }>;
};

export type SyncRunRecord = {
  id: string;
  started_at: string;
  finished_at: string | null;
  trigger: "cron" | "manual";
  window_start: string;
  window_end: string;
  ok: boolean;
  partial: boolean;
  error_summary: string | null;
  details: Record<string, unknown>;
};

export type CampaignDayRow = {
  date: string;
  market: Market;
  customer_id: string;
  campaign_id: string;
  campaign_name: string;
  currency: MarketCurrency;
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
  conversions_value: number;
  all_conversions: number;
};

export type AdGroupDayRow = {
  date: string;
  market: Market;
  customer_id: string;
  campaign_id: string;
  campaign_name: string;
  ad_group_id: string;
  ad_group_name: string;
  currency: MarketCurrency;
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
  conversions_value: number;
};

export type KeywordDayRow = {
  date: string;
  market: Market;
  customer_id: string;
  campaign_id: string;
  campaign_name: string;
  ad_group_id: string;
  ad_group_name: string;
  criterion_id: string;
  keyword_text: string;
  match_type: string;
  currency: MarketCurrency;
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
  conversions_value: number;
};

export type SearchTermDayRow = {
  date: string;
  market: Market;
  customer_id: string;
  campaign_name: string;
  ad_group_name: string;
  search_term: string;
  keyword_text: string;
  match_type: string;
  currency: MarketCurrency;
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
};

export type LandingPageDayRow = {
  date: string;
  market: Market;
  property_id: string;
  landing_page: string;
  sessions: number;
  engaged_sessions: number;
  conversions: number;
  total_users: number;
};

export type ZohoInquiryDayRow = {
  date: string;
  market: Market | "UNKNOWN";
  record_id: string;
  status: string;
  lead_source: string;
  utm_source: string | null;
  utm_medium: string | null;
  utm_campaign: string | null;
  utm_term: string | null;
  utm_content: string | null;
  /** Present for join only — never logged. Stored hashed via join_key. */
  has_gclid: boolean;
  landing_page: string | null;
  join_method: JoinMethod;
  join_key: string;
  /** True only for date+landing fallback — not a confirmed click match. */
  join_inferred: boolean;
  paid_likely: boolean;
};
