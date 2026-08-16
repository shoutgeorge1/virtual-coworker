#!/usr/bin/env node
/**
 * Live-page smoke for vc-xray. Fails if Loading… remains or required KPIs blank.
 * Usage (from xray/): node smoke-live.mjs [baseUrl]
 * Default base: https://vc-xray.vercel.app
 */
const base = (process.argv[2] || "https://vc-xray.vercel.app").replace(/\/$/, "");

const checks = [
  {
    path: "/executive",
    forbid: [/Loading numbers/i, /id="asof">Loading/i, /Loading…/, /Say yes\/no on/i, /Ask Cursor/i, /Ask Sales/i, /Your checklist/i],
    require: [/United States/i, /Australia/i, /Cost \/ enquiry/i, /Cost \/ JO/i, /week-costs/i, /week-ads/i, /\$60\.35/, /A\$51\.58/, /vs prior agency/i, /Cost \/ Zapier JO/i, /not tracked/i, /id="us-spend"/i, /id="au-spend"/i, /Last 7 days/i, /kpi-row/i, /kpi-emph/i],
    note: "Executive baked KPIs",
  },
  {
    path: "/launch-control",
    forbid: [/Your checklist/i, /Ask Sales \/ Cursor/i, /Cursor: refresh Ads/i, /Say yes or no on the draft Zoho/i, /Ask Cursor/i],
    require: [/Current campaign strategy/i, /Daily checks/i, /Launch steps/i, /Operator detail/i, /form boxes → Zoho boxes/i, /What we know so far/i, /crm-row/i, /Zoho \+ offline conversions — DEFERRED DURING COLD START/i, /Revisit only after/i],
    note: "Checklist fold",
  },
  {
    path: "/attribution",
    forbid: [/You: write the field map/i, /You: approve the proposal/i, /Say yes\/no/i],
    require: [/Cursor:/i, /form boxes → Zoho boxes/i, /writes/i, /utm_gclid/i, /Clear/i, /deferred during cold start/i],
    note: "Funnel CRM",
  },
  {
    path: "/experiments",
    forbid: [/Loading…/, /Loading snapshot/i],
    require: [/Parked/i, /not running/i],
    note: "Experiments parked",
  },
  {
    path: "/recovery-audit",
    forbid: [],
    require: [/embedded-page-data/i, /__VC_loadPageData/i, /golden nugget/i],
    note: "Recovery embed",
  },
];

const jsonEndpoints = [
  "/data/executive-snapshot.json",
  "/data/impression-share.json",
  "/data/experiments-snapshot.json",
  "/data/recovery-audit.json",
  "/data/zoho-field-map-proposal.json",
];

async function get(url) {
  const r = await fetch(url, { cache: "no-store", redirect: "follow" });
  const text = await r.text();
  return { ok: r.ok, status: r.status, text, url: r.url };
}

let failed = 0;

for (const ep of jsonEndpoints) {
  const { ok, status, text } = await get(base + ep);
  if (!ok) {
    console.error(`FAIL JSON ${ep} HTTP ${status}`);
    failed++;
    continue;
  }
  try {
    const j = JSON.parse(text);
    if (!j || typeof j !== "object") throw new Error("not object");
    console.log(`OK JSON ${ep} (${text.length} bytes)`);
  } catch (e) {
    console.error(`FAIL JSON ${ep} invalid: ${e.message}`);
    failed++;
  }
}

for (const c of checks) {
  const { ok, status, text } = await get(base + c.path);
  if (!ok) {
    console.error(`FAIL ${c.path} HTTP ${status}`);
    failed++;
    continue;
  }
  const problems = [];
  for (const re of c.forbid || []) {
    if (re.test(text)) problems.push(`forbidden match ${re}`);
  }
  for (const re of c.require || []) {
    if (!re.test(text)) problems.push(`missing ${re}`);
  }
  // Executive: us-spend must not be em dash alone if baked
  if (c.path === "/executive") {
    const m = text.match(/id="us-spend"[^>]*>([^<]*)</);
    if (m && (!m[1].trim() || m[1].trim() === "—")) {
      problems.push("us-spend blank");
    }
    const a = text.match(/id="au-spend"[^>]*>([^<]*)</);
    if (a && (!a[1].trim() || a[1].trim() === "—")) {
      problems.push("au-spend blank");
    }
  }
  if (problems.length) {
    console.error(`FAIL ${c.path} (${c.note}): ${problems.join("; ")}`);
    failed++;
  } else {
    console.log(`OK ${c.path} (${c.note})`);
  }
}

if (failed) {
  console.error(`\n${failed} smoke check(s) failed`);
  process.exit(1);
}
console.log("\nAll smoke checks passed");
