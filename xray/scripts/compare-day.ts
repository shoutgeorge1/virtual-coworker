import { readFileSync } from "node:fs";
import { neon } from "@neondatabase/serverless";
import {
  parseGoogleAdsConfig,
  searchGaql,
  campaignQuery,
  normalizeCampaignRows,
} from "../lib/google-ads/client";

for (const line of readFileSync(".env.local", "utf8").split("\n")) {
  const t = line.trim();
  if (!t || t.startsWith("#") || !t.includes("=")) continue;
  const i = t.indexOf("=");
  const k = t.slice(0, i);
  let v = t.slice(i + 1);
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    v = v.slice(1, -1);
  }
  if (!(k in process.env)) process.env[k] = v;
}

async function main() {
  const url = process.env.DATABASE_URL || process.env.POSTGRES_URL;
  if (!url) throw new Error("no DATABASE_URL");
  const sql = neon(url);
  const date = "2026-08-18";

  const ads = await sql`
    SELECT market,
      SUM(impressions)::int AS impressions,
      SUM(clicks)::int AS clicks,
      ROUND(SUM(cost)::numeric, 2) AS spend,
      ROUND(SUM(conversions)::numeric, 2) AS conversions
    FROM daily_campaign_performance
    WHERE date = ${date}::date
    GROUP BY market ORDER BY market`;

  const ga4 = await sql`
    SELECT market,
      SUM(sessions)::int AS sessions,
      ROUND(SUM(conversions)::numeric, 2) AS conversions
    FROM daily_landing_page_performance
    WHERE date = ${date}::date
    GROUP BY market ORDER BY market`;

  const zoho = await sql`
    SELECT market, COUNT(*)::int AS inquiries
    FROM daily_zoho_inquiries
    WHERE date = ${date}::date
    GROUP BY market ORDER BY market`;

  const cfg = parseGoogleAdsConfig()!;
  const rawUs = await searchGaql(cfg, cfg.customerIdUs, campaignQuery(date, date, "US"));
  const rawAu = await searchGaql(cfg, cfg.customerIdAu, campaignQuery(date, date, "AU"));
  const liveUs = normalizeCampaignRows(rawUs, "US", cfg.customerIdUs).reduce(
    (a, r) => ({
      impressions: a.impressions + r.impressions,
      clicks: a.clicks + r.clicks,
      spend: a.spend + r.cost,
      conversions: a.conversions + r.conversions,
    }),
    { impressions: 0, clicks: 0, spend: 0, conversions: 0 },
  );
  const liveAu = normalizeCampaignRows(rawAu, "AU", cfg.customerIdAu).reduce(
    (a, r) => ({
      impressions: a.impressions + r.impressions,
      clicks: a.clicks + r.clicks,
      spend: a.spend + r.cost,
      conversions: a.conversions + r.conversions,
    }),
    { impressions: 0, clicks: 0, spend: 0, conversions: 0 },
  );
  liveUs.spend = Math.round(liveUs.spend * 100) / 100;
  liveAu.spend = Math.round(liveAu.spend * 100) / 100;

  console.log(
    JSON.stringify(
      {
        date,
        db_ads: ads,
        live_ads: { US: liveUs, AU: liveAu },
        db_ga4: ga4,
        db_zoho: zoho,
      },
      null,
      2,
    ),
  );
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
