/**
 * Daily sync orchestrator — re-fetches previous 14 complete UTC days
 * and upserts into durable storage. Read-only against Ads / GA4 / Zoho.
 */

import { randomUUID } from "node:crypto";
import type { SyncStore } from "@/lib/db/store";
import { createStore } from "@/lib/db/store";
import { previousCompleteDayWindow } from "@/lib/sync/dates";
import { syncLog, redactUnknown } from "@/lib/sync/redact";
import type {
  DashboardStatus,
  SourceFreshness,
  SyncRunRecord,
  SyncSource,
} from "@/lib/sync/types";
import {
  parseGoogleAdsConfig,
  pullGoogleAdsWindow,
} from "@/lib/google-ads/client";
import { parseGa4Config, pullGa4Window } from "@/lib/ga4/client";
import { parseZohoReadConfig, pullZohoWindow } from "@/lib/zoho/read-client";

export type SyncTrigger = "cron" | "manual";

export type DailySyncResult = {
  ok: boolean;
  partial: boolean;
  run_id: string;
  window_start: string;
  window_end: string;
  status: DashboardStatus;
  errors: string[];
};

export type RunDailySyncOptions = {
  env?: NodeJS.ProcessEnv;
  store?: SyncStore;
  trigger?: SyncTrigger;
  asOf?: Date;
  dayCount?: number;
  fetchImpl?: typeof fetch;
};

export async function runDailySync(
  opts: RunDailySyncOptions = {},
): Promise<DailySyncResult> {
  const env = opts.env || process.env;
  const store = opts.store || createStore(env);
  const trigger = opts.trigger || "manual";
  const dayCount = opts.dayCount ?? 14;
  const window = previousCompleteDayWindow(opts.asOf || new Date(), dayCount);
  const runId = randomUUID();
  const startedAt = new Date().toISOString();

  const run: SyncRunRecord = {
    id: runId,
    started_at: startedAt,
    finished_at: null,
    trigger,
    window_start: window.start,
    window_end: window.end,
    ok: false,
    partial: false,
    error_summary: null,
    details: {},
  };

  await store.ensureSchema();
  await store.insertSyncRun(run);

  syncLog({
    event: "start",
    run_id: runId,
    trigger,
    window_start: window.start,
    window_end: window.end,
  });

  const freshness: SourceFreshness[] = [];
  const partialFailures: Array<{ source: SyncSource; error: string }> = [];
  const errors: string[] = [];
  const rowCounts: Record<string, number> = {};

  // --- Google Ads ---
  const adsCfg = parseGoogleAdsConfig(env);
  if (!adsCfg) {
    const msg = "Google Ads credentials missing";
    freshness.push({
      source: "google_ads",
      last_success_at: null,
      window_start: window.start,
      window_end: window.end,
      row_counts: {},
      ok: false,
      error: msg,
    });
    partialFailures.push({ source: "google_ads", error: msg });
    errors.push(msg);
  } else {
    try {
      const ads = await pullGoogleAdsWindow(adsCfg, window.start, window.end, {
        fetchImpl: opts.fetchImpl,
      });
      const c = await store.upsertCampaigns(ads.campaigns);
      const ag = await store.upsertAdGroups(ads.adGroups);
      const kw = await store.upsertKeywords(ads.keywords);
      const st = await store.upsertSearchTerms(ads.searchTerms);
      rowCounts.campaigns = c;
      rowCounts.ad_groups = ag;
      rowCounts.keywords = kw;
      rowCounts.search_terms = st;
      const adsErrors = ads.errors;
      const ok = adsErrors.length === 0;
      if (!ok) {
        for (const e of adsErrors) {
          partialFailures.push({ source: "google_ads", error: e });
          errors.push(e);
        }
      }
      freshness.push({
        source: "google_ads",
        last_success_at: ok ? new Date().toISOString() : c + ag + kw + st > 0 ? new Date().toISOString() : null,
        window_start: window.start,
        window_end: window.end,
        row_counts: {
          campaigns: c,
          ad_groups: ag,
          keywords: kw,
          search_terms: st,
        },
        ok,
        error: adsErrors[0],
      });
    } catch (err) {
      const msg = redactUnknown(err);
      freshness.push({
        source: "google_ads",
        last_success_at: null,
        window_start: window.start,
        window_end: window.end,
        row_counts: {},
        ok: false,
        error: msg,
      });
      partialFailures.push({ source: "google_ads", error: msg });
      errors.push(msg);
    }
  }

  // --- GA4 ---
  const ga4Cfg = parseGa4Config(env);
  if (!ga4Cfg) {
    const msg = "GA4 credentials or property id missing";
    freshness.push({
      source: "ga4",
      last_success_at: null,
      window_start: window.start,
      window_end: window.end,
      row_counts: {},
      ok: false,
      error: msg,
    });
    partialFailures.push({ source: "ga4", error: msg });
    errors.push(msg);
  } else {
    try {
      const ga4 = await pullGa4Window(ga4Cfg, window.start, window.end, {
        fetchImpl: opts.fetchImpl,
      });
      const n = await store.upsertLandingPages(ga4.landingPages);
      rowCounts.landing_pages = n;
      for (const e of ga4.errors) {
        partialFailures.push({ source: "ga4", error: e });
        errors.push(e);
      }
      freshness.push({
        source: "ga4",
        last_success_at: n > 0 || ga4.errors.length === 0 ? new Date().toISOString() : null,
        window_start: window.start,
        window_end: window.end,
        row_counts: { landing_pages: n },
        ok: ga4.errors.length === 0,
        error: ga4.errors[0],
      });
    } catch (err) {
      const msg = redactUnknown(err);
      freshness.push({
        source: "ga4",
        last_success_at: null,
        window_start: window.start,
        window_end: window.end,
        row_counts: {},
        ok: false,
        error: msg,
      });
      partialFailures.push({ source: "ga4", error: msg });
      errors.push(msg);
    }
  }

  // --- Zoho (read-only) ---
  const zohoCfg = parseZohoReadConfig(env);
  if (!zohoCfg) {
    const msg = "Zoho CRM credentials missing";
    freshness.push({
      source: "zoho",
      last_success_at: null,
      window_start: window.start,
      window_end: window.end,
      row_counts: {},
      ok: false,
      error: msg,
    });
    partialFailures.push({ source: "zoho", error: msg });
    errors.push(msg);
  } else {
    try {
      const zoho = await pullZohoWindow(zohoCfg, window.start, window.end, {
        fetchImpl: opts.fetchImpl,
      });
      const n = await store.upsertZohoInquiries(zoho.inquiries);
      rowCounts.zoho_inquiries = n;
      for (const e of zoho.errors) {
        partialFailures.push({ source: "zoho", error: e });
        errors.push(e);
      }
      freshness.push({
        source: "zoho",
        last_success_at:
          n > 0 || zoho.errors.length === 0 ? new Date().toISOString() : null,
        window_start: window.start,
        window_end: window.end,
        row_counts: { zoho_inquiries: n },
        ok: zoho.errors.length === 0,
        error: zoho.errors[0],
      });
    } catch (err) {
      const msg = redactUnknown(err);
      freshness.push({
        source: "zoho",
        last_success_at: null,
        window_start: window.start,
        window_end: window.end,
        row_counts: {},
        ok: false,
        error: msg,
      });
      partialFailures.push({ source: "zoho", error: msg });
      errors.push(msg);
    }
  }

  const tableCounts = await store.countRows();
  const allSourcesOk = freshness.every((f) => f.ok);
  const anySourceOk = freshness.some((f) => f.ok);
  const partial = !allSourcesOk && anySourceOk;
  const ok = allSourcesOk;
  const finishedAt = new Date().toISOString();

  const { sanitizeDashboardStatus } = await import("@/lib/sync/status-safe");
  const status: DashboardStatus = sanitizeDashboardStatus({
    updated_at: finishedAt,
    last_successful_sync_at: ok || anySourceOk ? finishedAt : null,
    last_sync_run_id: runId,
    window_start: window.start,
    window_end: window.end,
    freshness,
    row_counts: { ...tableCounts, ...rowCounts },
    partial_failures: partialFailures,
  })!;

  run.finished_at = finishedAt;
  run.ok = ok;
  run.partial = partial;
  run.error_summary = errors[0] || null;
  run.details = {
    row_counts: rowCounts,
    table_counts: tableCounts,
    error_count: errors.length,
  };

  await store.finishSyncRun(run);
  await store.saveDashboardStatus(status);

  syncLog({
    event: "finish",
    run_id: runId,
    ok,
    partial,
    error_count: errors.length,
  });

  return {
    ok,
    partial,
    run_id: runId,
    window_start: window.start,
    window_end: window.end,
    status,
    errors,
  };
}
