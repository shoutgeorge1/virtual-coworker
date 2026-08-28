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
    forbid: [/Loading numbers/i, /id="asof">Loading/i, /Say yes\/no on/i, /Ask Cursor/i, /Ask Sales/i, /Your checklist/i, /may be paid/i, /Watch next week/i],
    require: [/Executive Performance/i, /Australia/i, /United States/i, /Pilot ramp by month/i, /Data confidence and next action/i],
    note: "Executive performance canonical dashboard",
  },
  {
    path: "/nav.js",
    forbid: [/Stage 1 command center/i],
    require: [/Search pilot/, /LP QA/, /A\/B tests/, /ab-tests\.html/],
    note: "Sidebar label",
  },
  {
    path: "/lp-qa",
    forbid: [/may be paid/i, /watch —/i],
    require: [/Trust pages, landing pages, conversion checks/, /TF_PH_VA/, /Company field/, /phone_cta_clicked/, /Good to go/],
    note: "LP QA 19 Aug",
  },
  {
    path: "/trust-first-rollout",
    forbid: [/may be paid/i, /watch —/i],
    require: [/TF_PH_VA/, /TF_Hire_Dedicated/, /TF_Real_Estate/, /TF_Bookkeeping/, /Paused/, /Live H1/, /does not touch/],
    note: "TF test groups — new paused AGs only",
  },
  {
    path: "/launch-control",
    forbid: [/Your checklist/i, /Ask Sales \/ Cursor/i, /Cursor: refresh Ads/i, /Say yes or no on the draft Zoho/i, /Ask Cursor/i, /Stage 1 command center/i, /DEFERRED DURING COLD START/, /send Job Orders and Placements into the two Ads conversion actions/i, /Leave competitor brand names in the report/i, /After Aug 18 — next/i, /Do these first/i],
    require: [/Daily checks/i, /Waiting/i, /Guardrails/i, /Deferred projects/i],
    note: "Launch Control ops dashboard",
  },
  {
    path: "/attribution",
    forbid: [/You: write the field map/i, /You: approve the proposal/i, /Say yes\/no/i],
    require: [/Where a lead goes/i, /Checklist/i, /click ID/i, /Data Manager/i],
    note: "Funnel CRM",
  },
  {
    path: "/experiments",
    forbid: [/Loading…/, /Loading snapshot/i],
    require: [/Most tests parked/i, /A\/B tests/i],
    note: "Experiments parked note",
  },
  {
    path: "/ab-tests",
    forbid: [/Loading…/, /Loading snapshot/i],
    require: [/A\/B tests/i, /Baseline control untouched/i, /us_hero_portrait/i, /Marketing A orange/i, /embedded-page-data/i],
    note: "A/B tests live scoreboard",
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
