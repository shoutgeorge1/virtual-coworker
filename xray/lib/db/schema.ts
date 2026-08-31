/**
 * Idempotent daily tables for the read-only sync pipeline.
 * Applied via CREATE IF NOT EXISTS on each sync (safe on Neon / Vercel Postgres).
 */

export const SCHEMA_SQL = `
CREATE TABLE IF NOT EXISTS sync_runs (
  id TEXT PRIMARY KEY,
  started_at TIMESTAMPTZ NOT NULL,
  finished_at TIMESTAMPTZ,
  trigger TEXT NOT NULL,
  window_start DATE NOT NULL,
  window_end DATE NOT NULL,
  ok BOOLEAN NOT NULL DEFAULT FALSE,
  partial BOOLEAN NOT NULL DEFAULT FALSE,
  error_summary TEXT,
  details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS dashboard_status (
  id TEXT PRIMARY KEY DEFAULT 'default',
  payload JSONB NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_campaign_performance (
  date DATE NOT NULL,
  market TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  campaign_id TEXT NOT NULL,
  campaign_name TEXT NOT NULL,
  currency TEXT NOT NULL,
  impressions BIGINT NOT NULL DEFAULT 0,
  clicks BIGINT NOT NULL DEFAULT 0,
  cost DOUBLE PRECISION NOT NULL DEFAULT 0,
  conversions DOUBLE PRECISION NOT NULL DEFAULT 0,
  conversions_value DOUBLE PRECISION NOT NULL DEFAULT 0,
  all_conversions DOUBLE PRECISION NOT NULL DEFAULT 0,
  synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (date, market, campaign_id)
);

CREATE TABLE IF NOT EXISTS daily_ad_group_performance (
  date DATE NOT NULL,
  market TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  campaign_id TEXT NOT NULL,
  campaign_name TEXT NOT NULL,
  ad_group_id TEXT NOT NULL,
  ad_group_name TEXT NOT NULL,
  currency TEXT NOT NULL,
  impressions BIGINT NOT NULL DEFAULT 0,
  clicks BIGINT NOT NULL DEFAULT 0,
  cost DOUBLE PRECISION NOT NULL DEFAULT 0,
  conversions DOUBLE PRECISION NOT NULL DEFAULT 0,
  conversions_value DOUBLE PRECISION NOT NULL DEFAULT 0,
  synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (date, market, ad_group_id)
);

CREATE TABLE IF NOT EXISTS daily_keyword_performance (
  date DATE NOT NULL,
  market TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  campaign_id TEXT NOT NULL,
  campaign_name TEXT NOT NULL,
  ad_group_id TEXT NOT NULL,
  ad_group_name TEXT NOT NULL,
  criterion_id TEXT NOT NULL,
  keyword_text TEXT NOT NULL,
  match_type TEXT NOT NULL,
  currency TEXT NOT NULL,
  impressions BIGINT NOT NULL DEFAULT 0,
  clicks BIGINT NOT NULL DEFAULT 0,
  cost DOUBLE PRECISION NOT NULL DEFAULT 0,
  conversions DOUBLE PRECISION NOT NULL DEFAULT 0,
  conversions_value DOUBLE PRECISION NOT NULL DEFAULT 0,
  synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (date, market, criterion_id)
);

CREATE TABLE IF NOT EXISTS daily_search_terms (
  date DATE NOT NULL,
  market TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  campaign_name TEXT NOT NULL,
  ad_group_name TEXT NOT NULL,
  search_term TEXT NOT NULL,
  keyword_text TEXT NOT NULL DEFAULT '',
  match_type TEXT NOT NULL DEFAULT '',
  currency TEXT NOT NULL,
  impressions BIGINT NOT NULL DEFAULT 0,
  clicks BIGINT NOT NULL DEFAULT 0,
  cost DOUBLE PRECISION NOT NULL DEFAULT 0,
  conversions DOUBLE PRECISION NOT NULL DEFAULT 0,
  synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (date, market, campaign_name, ad_group_name, search_term)
);

CREATE TABLE IF NOT EXISTS daily_landing_page_performance (
  date DATE NOT NULL,
  market TEXT NOT NULL,
  property_id TEXT NOT NULL,
  landing_page TEXT NOT NULL,
  sessions BIGINT NOT NULL DEFAULT 0,
  engaged_sessions BIGINT NOT NULL DEFAULT 0,
  conversions DOUBLE PRECISION NOT NULL DEFAULT 0,
  total_users BIGINT NOT NULL DEFAULT 0,
  synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (date, market, property_id, landing_page)
);

CREATE TABLE IF NOT EXISTS daily_zoho_inquiries (
  date DATE NOT NULL,
  market TEXT NOT NULL,
  record_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT '',
  lead_source TEXT NOT NULL DEFAULT '',
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  utm_term TEXT,
  utm_content TEXT,
  has_gclid BOOLEAN NOT NULL DEFAULT FALSE,
  landing_page TEXT,
  join_method TEXT NOT NULL,
  join_key TEXT NOT NULL,
  join_inferred BOOLEAN NOT NULL DEFAULT FALSE,
  paid_likely BOOLEAN NOT NULL DEFAULT FALSE,
  synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (date, record_id)
);

CREATE INDEX IF NOT EXISTS idx_zoho_join_key ON daily_zoho_inquiries (join_method, join_key);
CREATE INDEX IF NOT EXISTS idx_campaign_market_date ON daily_campaign_performance (market, date);
CREATE INDEX IF NOT EXISTS idx_landing_market_date ON daily_landing_page_performance (market, date);
`;
