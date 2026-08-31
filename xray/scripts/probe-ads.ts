import { readFileSync } from "node:fs";
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
  const cfg = parseGoogleAdsConfig();
  if (!cfg) throw new Error("no google ads cfg");
  const raw = await searchGaql(
    cfg,
    cfg.customerIdUs,
    campaignQuery("2026-08-18", "2026-08-20", "US"),
  );
  const rows = normalizeCampaignRows(raw, "US", cfg.customerIdUs);
  console.log(
    JSON.stringify(
      {
        raw: raw.length,
        normalized: rows.length,
        sample: rows[0]
          ? {
              date: rows[0].date,
              campaign: rows[0].campaign_name,
              impressions: rows[0].impressions,
              clicks: rows[0].clicks,
              cost: rows[0].cost,
              currency: rows[0].currency,
            }
          : null,
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
