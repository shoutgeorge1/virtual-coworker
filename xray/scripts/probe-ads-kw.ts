import { readFileSync } from "node:fs";
import { parseGoogleAdsConfig, searchGaql, keywordQuery, searchTermQuery } from "../lib/google-ads/client";
for (const line of readFileSync(".env.local", "utf8").split("\n")) {
  const t = line.trim();
  if (!t || t.startsWith("#") || !t.includes("=")) continue;
  const i = t.indexOf("=");
  const k = t.slice(0, i);
  let v = t.slice(i + 1);
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
  if (!(k in process.env)) process.env[k] = v;
}
async function main() {
  const cfg = parseGoogleAdsConfig()!;
  const kw = await searchGaql(cfg, cfg.customerIdUs, keywordQuery("2026-08-18", "2026-08-20", "US"));
  const st = await searchGaql(cfg, cfg.customerIdUs, searchTermQuery("2026-08-18", "2026-08-20", "US"));
  console.log(JSON.stringify({ keywords: kw.length, search_terms: st.length }, null, 2));
}
main().catch((e) => { console.error(e); process.exit(1); });
