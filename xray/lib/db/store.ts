import { neon, type NeonQueryFunction } from "@neondatabase/serverless";
import { SCHEMA_SQL } from "./schema";
import type {
  AdGroupDayRow,
  CampaignDayRow,
  DashboardStatus,
  KeywordDayRow,
  LandingPageDayRow,
  SearchTermDayRow,
  SyncRunRecord,
  ZohoInquiryDayRow,
} from "@/lib/sync/types";

export type SqlTag = NeonQueryFunction<false, false>;

export type SyncStore = {
  ensureSchema(): Promise<void>;
  upsertCampaigns(rows: CampaignDayRow[]): Promise<number>;
  upsertAdGroups(rows: AdGroupDayRow[]): Promise<number>;
  upsertKeywords(rows: KeywordDayRow[]): Promise<number>;
  upsertSearchTerms(rows: SearchTermDayRow[]): Promise<number>;
  upsertLandingPages(rows: LandingPageDayRow[]): Promise<number>;
  upsertZohoInquiries(rows: ZohoInquiryDayRow[]): Promise<number>;
  insertSyncRun(run: SyncRunRecord): Promise<void>;
  finishSyncRun(run: SyncRunRecord): Promise<void>;
  saveDashboardStatus(status: DashboardStatus): Promise<void>;
  getDashboardStatus(): Promise<DashboardStatus | null>;
  countRows(): Promise<Record<string, number>>;
};

function databaseUrl(env: NodeJS.ProcessEnv = process.env): string | null {
  return (
    (env.DATABASE_URL || env.POSTGRES_URL || env.POSTGRES_PRISMA_URL || "").trim() ||
    null
  );
}

export function createSql(env: NodeJS.ProcessEnv = process.env): SqlTag | null {
  const url = databaseUrl(env);
  if (!url) return null;
  return neon(url);
}

/** Production Postgres store (Neon / Vercel Postgres). */
export function createPostgresStore(sql: SqlTag): SyncStore {
  return {
    async ensureSchema() {
      // neon serverless executes one statement per call — split on semicolons carefully
      const parts = SCHEMA_SQL.split(";")
        .map((s) => s.trim())
        .filter(Boolean);
      for (const stmt of parts) {
        await sql.query(stmt);
      }
    },

    async upsertCampaigns(rows) {
      let n = 0;
      for (const r of rows) {
        await sql`
          INSERT INTO daily_campaign_performance (
            date, market, customer_id, campaign_id, campaign_name, currency,
            impressions, clicks, cost, conversions, conversions_value, all_conversions, synced_at
          ) VALUES (
            ${r.date}::date, ${r.market}, ${r.customer_id}, ${r.campaign_id}, ${r.campaign_name},
            ${r.currency}, ${r.impressions}, ${r.clicks}, ${r.cost}, ${r.conversions},
            ${r.conversions_value}, ${r.all_conversions}, NOW()
          )
          ON CONFLICT (date, market, campaign_id) DO UPDATE SET
            campaign_name = EXCLUDED.campaign_name,
            currency = EXCLUDED.currency,
            impressions = EXCLUDED.impressions,
            clicks = EXCLUDED.clicks,
            cost = EXCLUDED.cost,
            conversions = EXCLUDED.conversions,
            conversions_value = EXCLUDED.conversions_value,
            all_conversions = EXCLUDED.all_conversions,
            synced_at = NOW()
        `;
        n += 1;
      }
      return n;
    },

    async upsertAdGroups(rows) {
      let n = 0;
      for (const r of rows) {
        await sql`
          INSERT INTO daily_ad_group_performance (
            date, market, customer_id, campaign_id, campaign_name, ad_group_id, ad_group_name,
            currency, impressions, clicks, cost, conversions, conversions_value, synced_at
          ) VALUES (
            ${r.date}::date, ${r.market}, ${r.customer_id}, ${r.campaign_id}, ${r.campaign_name},
            ${r.ad_group_id}, ${r.ad_group_name}, ${r.currency}, ${r.impressions}, ${r.clicks},
            ${r.cost}, ${r.conversions}, ${r.conversions_value}, NOW()
          )
          ON CONFLICT (date, market, ad_group_id) DO UPDATE SET
            campaign_id = EXCLUDED.campaign_id,
            campaign_name = EXCLUDED.campaign_name,
            ad_group_name = EXCLUDED.ad_group_name,
            currency = EXCLUDED.currency,
            impressions = EXCLUDED.impressions,
            clicks = EXCLUDED.clicks,
            cost = EXCLUDED.cost,
            conversions = EXCLUDED.conversions,
            conversions_value = EXCLUDED.conversions_value,
            synced_at = NOW()
        `;
        n += 1;
      }
      return n;
    },

    async upsertKeywords(rows) {
      let n = 0;
      for (const r of rows) {
        await sql`
          INSERT INTO daily_keyword_performance (
            date, market, customer_id, campaign_id, campaign_name, ad_group_id, ad_group_name,
            criterion_id, keyword_text, match_type, currency,
            impressions, clicks, cost, conversions, conversions_value, synced_at
          ) VALUES (
            ${r.date}::date, ${r.market}, ${r.customer_id}, ${r.campaign_id}, ${r.campaign_name},
            ${r.ad_group_id}, ${r.ad_group_name}, ${r.criterion_id}, ${r.keyword_text},
            ${r.match_type}, ${r.currency}, ${r.impressions}, ${r.clicks}, ${r.cost},
            ${r.conversions}, ${r.conversions_value}, NOW()
          )
          ON CONFLICT (date, market, criterion_id) DO UPDATE SET
            campaign_id = EXCLUDED.campaign_id,
            campaign_name = EXCLUDED.campaign_name,
            ad_group_id = EXCLUDED.ad_group_id,
            ad_group_name = EXCLUDED.ad_group_name,
            keyword_text = EXCLUDED.keyword_text,
            match_type = EXCLUDED.match_type,
            currency = EXCLUDED.currency,
            impressions = EXCLUDED.impressions,
            clicks = EXCLUDED.clicks,
            cost = EXCLUDED.cost,
            conversions = EXCLUDED.conversions,
            conversions_value = EXCLUDED.conversions_value,
            synced_at = NOW()
        `;
        n += 1;
      }
      return n;
    },

    async upsertSearchTerms(rows) {
      let n = 0;
      for (const r of rows) {
        await sql`
          INSERT INTO daily_search_terms (
            date, market, customer_id, campaign_name, ad_group_name, search_term,
            keyword_text, match_type, currency, impressions, clicks, cost, conversions, synced_at
          ) VALUES (
            ${r.date}::date, ${r.market}, ${r.customer_id}, ${r.campaign_name}, ${r.ad_group_name},
            ${r.search_term}, ${r.keyword_text}, ${r.match_type}, ${r.currency},
            ${r.impressions}, ${r.clicks}, ${r.cost}, ${r.conversions}, NOW()
          )
          ON CONFLICT (date, market, campaign_name, ad_group_name, search_term) DO UPDATE SET
            keyword_text = EXCLUDED.keyword_text,
            match_type = EXCLUDED.match_type,
            currency = EXCLUDED.currency,
            impressions = EXCLUDED.impressions,
            clicks = EXCLUDED.clicks,
            cost = EXCLUDED.cost,
            conversions = EXCLUDED.conversions,
            synced_at = NOW()
        `;
        n += 1;
      }
      return n;
    },

    async upsertLandingPages(rows) {
      let n = 0;
      for (const r of rows) {
        await sql`
          INSERT INTO daily_landing_page_performance (
            date, market, property_id, landing_page, sessions, engaged_sessions,
            conversions, total_users, synced_at
          ) VALUES (
            ${r.date}::date, ${r.market}, ${r.property_id}, ${r.landing_page},
            ${r.sessions}, ${r.engaged_sessions}, ${r.conversions}, ${r.total_users}, NOW()
          )
          ON CONFLICT (date, market, property_id, landing_page) DO UPDATE SET
            sessions = EXCLUDED.sessions,
            engaged_sessions = EXCLUDED.engaged_sessions,
            conversions = EXCLUDED.conversions,
            total_users = EXCLUDED.total_users,
            synced_at = NOW()
        `;
        n += 1;
      }
      return n;
    },

    async upsertZohoInquiries(rows) {
      let n = 0;
      for (const r of rows) {
        await sql`
          INSERT INTO daily_zoho_inquiries (
            date, market, record_id, status, lead_source,
            utm_source, utm_medium, utm_campaign, utm_term, utm_content,
            has_gclid, landing_page, join_method, join_key, join_inferred, paid_likely, synced_at
          ) VALUES (
            ${r.date}::date, ${r.market}, ${r.record_id}, ${r.status}, ${r.lead_source},
            ${r.utm_source}, ${r.utm_medium}, ${r.utm_campaign}, ${r.utm_term}, ${r.utm_content},
            ${r.has_gclid}, ${r.landing_page}, ${r.join_method}, ${r.join_key}, ${r.join_inferred},
            ${r.paid_likely}, NOW()
          )
          ON CONFLICT (date, record_id) DO UPDATE SET
            market = EXCLUDED.market,
            status = EXCLUDED.status,
            lead_source = EXCLUDED.lead_source,
            utm_source = EXCLUDED.utm_source,
            utm_medium = EXCLUDED.utm_medium,
            utm_campaign = EXCLUDED.utm_campaign,
            utm_term = EXCLUDED.utm_term,
            utm_content = EXCLUDED.utm_content,
            has_gclid = EXCLUDED.has_gclid,
            landing_page = EXCLUDED.landing_page,
            join_method = EXCLUDED.join_method,
            join_key = EXCLUDED.join_key,
            join_inferred = EXCLUDED.join_inferred,
            paid_likely = EXCLUDED.paid_likely,
            synced_at = NOW()
        `;
        n += 1;
      }
      return n;
    },

    async insertSyncRun(run) {
      await sql`
        INSERT INTO sync_runs (
          id, started_at, finished_at, trigger, window_start, window_end,
          ok, partial, error_summary, details
        ) VALUES (
          ${run.id}, ${run.started_at}::timestamptz, ${run.finished_at},
          ${run.trigger}, ${run.window_start}::date, ${run.window_end}::date,
          ${run.ok}, ${run.partial}, ${run.error_summary}, ${run.details}
        )
        ON CONFLICT (id) DO NOTHING
      `;
    },

    async finishSyncRun(run) {
      await sql`
        INSERT INTO sync_runs (
          id, started_at, finished_at, trigger, window_start, window_end,
          ok, partial, error_summary, details
        ) VALUES (
          ${run.id}, ${run.started_at}::timestamptz, ${run.finished_at},
          ${run.trigger}, ${run.window_start}::date, ${run.window_end}::date,
          ${run.ok}, ${run.partial}, ${run.error_summary}, ${run.details}
        )
        ON CONFLICT (id) DO UPDATE SET
          finished_at = EXCLUDED.finished_at,
          ok = EXCLUDED.ok,
          partial = EXCLUDED.partial,
          error_summary = EXCLUDED.error_summary,
          details = EXCLUDED.details
      `;
    },

    async saveDashboardStatus(status) {
      await sql`
        INSERT INTO dashboard_status (id, payload, updated_at)
        VALUES ('default', ${status as unknown as string}, NOW())
        ON CONFLICT (id) DO UPDATE SET
          payload = EXCLUDED.payload,
          updated_at = NOW()
      `;
    },

    async getDashboardStatus() {
      const rows = await sql`SELECT payload FROM dashboard_status WHERE id = 'default' LIMIT 1`;
      if (!rows[0]) return null;
      return rows[0].payload as DashboardStatus;
    },

    async countRows() {
      const tables = [
        "daily_campaign_performance",
        "daily_ad_group_performance",
        "daily_keyword_performance",
        "daily_search_terms",
        "daily_landing_page_performance",
        "daily_zoho_inquiries",
        "sync_runs",
      ] as const;
      const out: Record<string, number> = {};
      for (const t of tables) {
        // Table names are fixed constants — not user input.
        const rows = (await sql.query(`SELECT COUNT(*)::int AS c FROM ${t}`)) as Array<{
          c: number;
        }>;
        out[t] = Number(rows[0]?.c ?? 0);
      }
      return out;
    },
  };
}

type MemMaps = {
  campaigns: Map<string, CampaignDayRow>;
  adGroups: Map<string, AdGroupDayRow>;
  keywords: Map<string, KeywordDayRow>;
  searchTerms: Map<string, SearchTermDayRow>;
  landingPages: Map<string, LandingPageDayRow>;
  zoho: Map<string, ZohoInquiryDayRow>;
  runs: Map<string, SyncRunRecord>;
  status: DashboardStatus | null;
};

function memKey(parts: Array<string | number>): string {
  return parts.join("\u0001");
}

/** In-memory store for unit tests (idempotent upserts). */
export function createMemoryStore(): SyncStore & { _maps: MemMaps } {
  const maps: MemMaps = {
    campaigns: new Map(),
    adGroups: new Map(),
    keywords: new Map(),
    searchTerms: new Map(),
    landingPages: new Map(),
    zoho: new Map(),
    runs: new Map(),
    status: null,
  };

  return {
    _maps: maps,
    async ensureSchema() {},
    async upsertCampaigns(rows) {
      for (const r of rows) {
        maps.campaigns.set(memKey([r.date, r.market, r.campaign_id]), { ...r });
      }
      return rows.length;
    },
    async upsertAdGroups(rows) {
      for (const r of rows) {
        maps.adGroups.set(memKey([r.date, r.market, r.ad_group_id]), { ...r });
      }
      return rows.length;
    },
    async upsertKeywords(rows) {
      for (const r of rows) {
        maps.keywords.set(memKey([r.date, r.market, r.criterion_id]), { ...r });
      }
      return rows.length;
    },
    async upsertSearchTerms(rows) {
      for (const r of rows) {
        maps.searchTerms.set(
          memKey([r.date, r.market, r.campaign_name, r.ad_group_name, r.search_term]),
          { ...r },
        );
      }
      return rows.length;
    },
    async upsertLandingPages(rows) {
      for (const r of rows) {
        maps.landingPages.set(
          memKey([r.date, r.market, r.property_id, r.landing_page]),
          { ...r },
        );
      }
      return rows.length;
    },
    async upsertZohoInquiries(rows) {
      for (const r of rows) {
        maps.zoho.set(memKey([r.date, r.record_id]), { ...r });
      }
      return rows.length;
    },
    async insertSyncRun(run) {
      if (!maps.runs.has(run.id)) maps.runs.set(run.id, { ...run });
    },
    async finishSyncRun(run) {
      maps.runs.set(run.id, { ...run });
    },
    async saveDashboardStatus(status) {
      maps.status = { ...status };
    },
    async getDashboardStatus() {
      return maps.status ? { ...maps.status } : null;
    },
    async countRows() {
      return {
        daily_campaign_performance: maps.campaigns.size,
        daily_ad_group_performance: maps.adGroups.size,
        daily_keyword_performance: maps.keywords.size,
        daily_search_terms: maps.searchTerms.size,
        daily_landing_page_performance: maps.landingPages.size,
        daily_zoho_inquiries: maps.zoho.size,
        sync_runs: maps.runs.size,
      };
    },
  };
}

export function createStore(env: NodeJS.ProcessEnv = process.env): SyncStore {
  const sql = createSql(env);
  if (!sql) {
    throw new Error(
      "DATABASE_URL (or POSTGRES_URL) is required for persistent sync storage",
    );
  }
  return createPostgresStore(sql);
}
