# Stage 1 Google Ads Editor package — FULL BUILD REPORT

**For:** ChatGPT audit + George operator handoff  
**Generated:** 2026-08-05  
**Remediated:** 2026-08-05 (v3 creatives) → **v4 evidence fold** (same evening)  
**Package:** `ads-launch/google-ads-editor-import.csv`  
**Builder:** `ads-launch/build_stage1_editor_package.py` (re-runnable)  
**Accounts:** USA `496-715-1855` · Australia `573-539-1940`  
**Status of all entities in CSV:** **Paused**  
**Live Ads mutations:** none (no API, no enable)  
**LP version:** `lp_version=stage1-v4`

---

## 0. What changed vs v3 (honest)

v3 fixed lazy RSAs / fat AGs / thin KWs / AU clone. It did **not** use performance CSVs (they arrived later the same evening).

**v4 folds real ~2y Editor search-term + campaign metrics** from `audit-data/performance/` into positives and negatives.

| Gap in v3 | v4 fix |
|-----------|--------|
| Keywords archaeology-only | Promoted converting / high-intent employer ST into Exact+Phrase (79 audited keepers all present) |
| Negatives strategy-curated | Expanded with real waste: DSA catch-alls, Spanish/LATAM, WFH fluff, review/pricing, salary/jobs clusters |
| Blanket `how to` negative | Removed — was blocking converting `how to hire a virtual assistant` (8.5 conv / $730). Kept DIY how-tos (`how to become`, `how to make money`, …) |
| Admin RSA still generic-ish | Rewrote Hire_PH angles around hire-VA / PH services / offshore VA ST language |
| Report oversold “mined” without ST | This file cites cost/clicks/conv from exports |

**Unchanged (still correct):** brand deferred · 9 roles US+AU · Hire_PH + Outsource_PH · Exact+Phrase only · Max Clicks · full unique RSAs · microsite Final URLs · `[APPROVAL_*]` budgets/CPC · no DSA/PMax/Broad positives.

---

## 1. Executive verdict (v4)

Stage 1 is **role-first Search** for Philippine remote staffing employers across **nine service lines**, now keyword-ranked from ~2y search terms. Brand deferred. Every primary theme has keywords + **fully filled unique RSAs** (15H / 4D). Exact + Phrase only. Maximize Clicks. Final URLs → vision microsite `/us` and `/au`. Budgets and Max CPC remain George placeholders.

**Do not clone** historical DSA catch-alls or thin `PM_*_RSA_*` theme farms — campaign metrics show those as CPA traps.

---

## 2. Evidence sources

| Source | Path | Used for |
|--------|------|----------|
| USA search terms | `audit-data/performance/search_terms_usa_4967151855_2026-08-05.csv` | Keep/kill ranking (~66.9k rows, UTF-16 TSV) |
| AU search terms | `audit-data/performance/search_terms_au_5735391940_2026-08-05.csv` | Same (~26.2k rows) |
| USA campaign metrics | `audit-data/performance/campaigns_metrics_usa_4967151855_2026-08-05.csv` | Avoid cloning DSA/RSA farms |
| AU campaign metrics | `audit-data/performance/campaigns_metrics_au_5735391940_2026-08-05.csv` | Same |
| Cite scratch | `ads-launch/_evidence_search_terms.json` | Aggregated keep/kill cites for this report |
| Editor structure (earlier) | `audit-data/editor-exports/*`, scratch JSON | Archaeology long-tail where ST thin (HR/recruitment) |

**Window:** Editor stats ~2024-08-01 → 2026-08-04.  
**Honesty:** ST cost totals < campaign totals (not every click has an ST row; PMax mix). Treat **CPA = cost÷conversions**, not conv-value ROAS, until tracking re-audit. Frequency ≠ quality — employer intent + conv used together.

### Campaign-level picture (~2y)

| Account | Cost | Clicks | Conv | Worst CPA traps (do not clone) | Better cores (context only) |
|---------|------|--------|------|--------------------------------|-----------------------------|
| USA | ~$724k | ~87k | ~2,597 | `PM_US_DSA_Generic_Catch-all` (~$1.3k CPA), `PM_US_RSA_*` Role/Pain/Core/Competitors (CPA $2.5k–$16k) | Brand Search (~$101 CPA), SKAG VA / Specific Services / Generic VA (CPA ~$270–$440) |
| AU | ~$457k | ~49k | ~1,413 | `PM_AU_DSA_Generic_Catch-all` (~$2.3k CPA), `PM_AU_RSA_*` Role/Core/Pain/Competitors | Brand / DSA / Competitor Search (lower CPA than RSA farms) |

---

## 3. Search-term KEEP table (employer intent → package)

Aggregated USA+AU. Metrics from exports — not invented. Brand / competitor conquest **not** added as positives (deferred).

| Search term | Conv | Cost | Clicks | Package placement |
|-------------|-----:|-----:|-------:|-------------------|
| virtual assistant | 341.2 | $107,756 | 4,975 | Admin Hire Exact |
| virtual assistant philippines | 81.5 | $37,503 | 847 | Admin Hire Exact |
| virtual assistants | 32.5 | $11,476 | 419 | Admin Hire Exact |
| philippines virtual assistant | 25.8 | $13,947 | 280 | Admin Hire Exact |
| virtual assistant services | 14.0 | $6,160 | 227 | Admin Hire Exact |
| hire virtual assistant | 11.5 | $3,970 | 120 | Admin Hire Exact |
| virtual assistants philippines | 10.3 | $7,735 | 144 | Admin Hire Exact |
| filipino virtual assistant | 9.0 | $4,725 | 113 | Admin Hire Exact |
| how to hire a virtual assistant | 8.5 | $730 | 40 | Admin Hire Exact+Phrase (not negatived) |
| virtual assistant hire | 8.0 | $1,626 | 44 | Admin Hire Exact |
| hire a virtual assistant | 7.9 | $2,672 | 73 | Admin Hire Exact+Phrase |
| hire a va | 6.0 | $3,177 | 78 | Admin Hire Exact |
| virtual assistants for hire | 6.0 | $2,504 | 70 | Admin Hire Exact |
| social media manager philippines | 6.0 | $2,451 | 81 | Social Hire Exact+Phrase |
| virtual marketing assistant | 6.0 | $2,152 | 84 | Digital Hire Exact+Phrase |
| va philippines | 5.6 | $5,314 | 135 | Admin Hire Exact |
| lead generation virtual assistant | 5.3 | $331 | 11 | Sales Hire Exact+Phrase |
| hire virtual assistant from philippines | 5.0 | $1,231 | 24 | Admin Hire Exact |
| marketing virtual assistant | 4.5 | $1,192 | 35 | Digital Hire Exact+Phrase |
| philippine virtual assistant | 4.0 | $3,307 | 88 | Admin Hire Exact |
| philippines bookkeeper | 3.0 | $1,366 | 15 | Bookkeeping Hire Exact+Phrase |
| sales virtual assistant / sales va / VA for sales | 2–3 | $236–$272 | — | Sales Hire Exact |
| philippines accounting outsourcing | 1.0 | $466 | 7 | Accounting Outsource Exact+Phrase |
| bookkeeper philippines | 1.0 | $997 | 18 | Bookkeeping Hire Exact+Phrase |
| customer service virtual assistant | 1.0 | $96 | 5 | CS Hire Exact+Phrase |
| human resources virtual assistant | 0 | $61 | 1 | HR Hire Exact (thin ST; kept as employer VA) |
| recruitment VA terms | — | near-zero ST | — | Curated long-tail only — **not** invented winners |

**Also promoted (high employer intent / spend even if low conv):** `offshore va`, `hire philippines virtual assistant`, `filipino social media manager`, `digital marketing outsourcing philippines`, `outsource accounting philippines`, `appointment setter philippines`, `philippines executive assistant`, `admin assistant philippines`, etc.

**Explicitly NOT kept as positives:** brand (`virtual coworker`, `remote coworker`), competitors as conquest (`bruntwork`, `myoutdesk`, `beepo`, `onlinejobs ph` — onlinejobs is marketplace/job bleed), `free virtual assistant` (junk), bare `social media manager` without PH/hire/VA qualifier.

---

## 4. Search-term KILL / NEGATIVE table (real waste)

| Search term / cluster | Conv | Cost | Clicks | Negative treatment |
|-----------------------|-----:|-----:|-------:|--------------------|
| onlinejobs ph | 87.0 | $32,108 | 2,307 | Negated (marketplace / wrong funnel for employer Max Clicks) |
| hello rache / hellorache | 4.0 | $3,315+ | 148+ | Negated (DSA/competitor bleed) |
| free virtual assistant | 7.0 | $2,510 | 1,913 | `free` + specific |
| bruntwork reviews | 1.0 | $2,184 | 61 | `reviews` / `bruntwork reviews` |
| onlinejobs ph pricing | 4.0 | $1,978 | 127 | pricing + onlinejobs cluster |
| online ph | 0 | $1,893 | 115 | DSA catch-all |
| virtual world assistants | 0 | $1,024 | 82 | Negated |
| onlinejobs / onlineph | 0 | $892 / $810 | — | Negated |
| remote coworker reviews | 0 | $850 | 14 | reviews (brand deferred anyway) |
| virtual assistant philippines cost | 1.0 | $771 | 28 | cost/pricing cluster |
| virtual assistant jobs | 4.0 | $723 | 187 | `jobs` / VA jobs |
| wing assistant | 0 | $715 | 14 | DSA bleed |
| upwork virtual assistant | 0 | $656 | 36 | upwork |
| virtual assistant cost | 0 | $641 | 45 | cost |
| top 10 virtual assistant companies | 0 | $596 | 13 | top 10 / research |
| work from home (+ variants) | ~1 | $448+ | — | bare `work from home` / `wfh` (v4) |
| what is a virtual assistant | 0 | $387 | 100 | `what is` |
| virtual assistant salary (+ PH/AU variants) | 0–1 | $270+ | — | salary cluster |
| asistente virtual (+ ES job variants) | 0 | ~$298+ | — | Spanish/LATAM block (~$1.3k cluster) |
| virtual assistant colombia / argentina VA | 0 | $43–$50 | — | LATAM geo bleed |

**Intentionally NOT negatived:** bare `hire` / `hiring`; `how to hire a virtual assistant` (converting employer intent).

---

## 5. Final account architecture (unchanged shape)

```
USA (496-715-1855)                          AU (573-539-1940)
├─ VC_US_S_ROLE_digital_marketing           ├─ VC_AU_S_ROLE_digital_marketing
│   ├─ Digital_Marketing_Hire_PH            │   ├─ … same AG shape
│   └─ Digital_Marketing_Outsource_PH
├─ VC_US_S_ROLE_social_media
├─ VC_US_S_ROLE_accounting
├─ VC_US_S_ROLE_bookkeeping
├─ VC_US_S_ROLE_administration
│   ├─ Administration_Hire_PH   ← general VA / CORE depth (ST-heavy)
│   ├─ Administration_EA_PH
│   └─ Admin_City_Test
├─ VC_US_S_ROLE_customer_service
├─ VC_US_S_ROLE_hr
├─ VC_US_S_ROLE_recruitment
└─ VC_US_S_ROLE_sales

BRAND: deferred — not in CSV
```

| Layer | Spec |
|-------|------|
| Type | Search · **Paused** |
| Networks | Google Search only (partners/Display **OFF**) |
| Geo | US or AU · Presence |
| Language | English |
| Bid | Maximize Clicks · Max CPC = `[APPROVAL_MAX_CPC]` |
| Budget | `[APPROVAL_DAILY_BUDGET_USD]` / `[APPROVAL_DAILY_BUDGET_AUD]` |
| Ad groups | Hire_PH + Outsource_PH (Admin: Hire + EA + City) |
| RSAs | 2 angles per theme AG · DKI on Hire/EA B |
| Assets | 6 callouts · 1 structured snippet · 4 microsite sitelinks |
| Negatives | **191** unique curated Broad per campaign |

---

## 6. Keyword counts (v4 machine)

| Match | Count (package total) | Notes |
|-------|----------------------:|-------|
| Exact | 1178 | ST keepers + employer long-tail; admin densest |
| Phrase | 368 | Discovery from converting clusters — not Exact clones only |
| Broad (positives) | **0** | Forbidden |
| Campaign negatives (Broad) | 3438 | 191 × 18 campaigns |

**Per market positive keywords:** 773.  
**Builder QA** refuses positive Broad, empty shells, single-AG campaigns, RSA blanks, boilerplate spam, medical/tech/spanish leaks, and bare `hire`/`hiring` negatives.

---

## 7. Negative strategy (v4)

1. **Job seeker** — jobs/salary/careers/resume + VA jobs/salary PH/AU variants from ST  
2. **WFH fluff** — bare `work from home` / `wfh` (new from ST)  
3. **Info / DIY** — what is, how to become / make money / get a job / start — **not** bare `how to`  
4. **Review / pricing research** — reviews, cost, how much, top 10, competitor review queries  
5. **DSA / marketplace catch-alls** — online ph, onlineph, onlinejobs*, wing assistant, hellorache, virtual world assistants, VA hub junk  
6. **Platforms** — upwork, fiverr, wishup, athena, myoutdesk, bruntwork, zirtual…  
7. **Spanish / LATAM** — asistente virtual*, español, colombia/argentina/mexico/latam  
8. **Excluded verticals** — medical / tech / graphic-web design  

---

## 8. RSA strategy

Every RSA: **15 unique headlines ≤30** + **4 unique descriptions ≤90**. Admin Hire rewritten for ST hire-VA language. Other roles keep v3 unique angles (not role-noun swaps). AU uses Australian / SMEs / organisation / specialise. Banned: Top 1%, Save 80%, $/hr, guaranteed/cheapest.

---

## 9. Final URLs

| Market | Primary Final URL pattern |
|--------|---------------------------|
| USA | `https://vision-three-alpha.vercel.app/us?role={role}` |
| AU | `https://vision-three-alpha.vercel.app/au?role={role}` |

- Sitelinks: same host only. **No WordPress.**  
- Tracking: UTMs + `lp_version=stage1-v4`  
- Domain TBD when George attaches custom paid domain  

---

## 10. Placeholders George must still approve

| Placeholder | Where |
|-------------|-------|
| `[APPROVAL_DAILY_BUDGET_USD]` | Each US campaign Budget |
| `[APPROVAL_DAILY_BUDGET_AUD]` | Each AU campaign Budget |
| `[APPROVAL_MAX_CPC]` | Campaign + AG Max CPC |
| Final URL host | vision-three-alpha until custom domain |
| Enable order | Launch Control — roles after gates green |
| Old live brand | Pause `PM_*_RSA_Brand` is a George click |

---

## 11. Package inventory (v4)

| Entity | Count |
|--------|------:|
| Campaigns | 18 |
| Ad groups | 38 |
| Positive keywords | 1546 |
| RSAs | 74 |
| Campaign negative keyword rows | 3438 |
| Unique negatives | 191 |
| Callouts | 108 |
| Structured snippets | 18 |
| Sitelinks | 72 |
| **Total CSV rows** | **5312** |

---

## 12. How ChatGPT should spot-check (re-audit)

1. **Open CSV** → `Row Type = Ad` → every row Headline 1–15 + Description 1–4 non-empty.  
2. Confirm **no** `VC_*_S_BRAND` and **no** empty ROLE shells.  
3. Confirm 18 `VC_{US|AU}_S_ROLE_*` campaigns for the nine roles.  
4. Confirm **≥2 ad groups per campaign** (Admin has 3).  
5. Filter positives → Criterion Type only Exact or Phrase.  
6. Grep creatives for `Top 1%`, `$/hr`, `80%`, `guaranteed` — expect zero.  
7. Grep Final URL for `virtualcoworker.com` WP paths — expect zero.  
8. Confirm DKI: many ads contain `{KeyWord:`.  
9. Confirm AU copy uses `Australian` / `specialise` / `organisation`.  
10. Confirm ST keepers present: `virtual assistants`, `how to hire a virtual assistant`, `social media manager philippines`, `philippines bookkeeper`, `virtual marketing assistant`.  
11. Confirm ST waste negatived: `online ph`, `asistente virtual`, `work from home`, `virtual assistant cost`, `wing assistant`.  
12. Confirm `lp_version=stage1-v4`. Budgets/Max CPC still `[APPROVAL_*]`. All **Paused**.

---

## 13. Operator enable guidance (after approvals)

1. Import CSV in Editor (split US vs AU rows or import then delete other market).  
2. Replace budget + Max CPC placeholders.  
3. Confirm networks/geo/presence.  
4. Confirm Final URL host.  
5. Post **Paused** → UI spot-check.  
6. Enable only after Launch Control gates green — **roles**, not brand.  
7. First 14 days: search-term mining → add negatives / promote Exact variants. Never Broad to “fix” volume. Never re-enable DSA catch-alls.

---

## 14. Files touched this rebuild (v4)

| File | Action |
|------|--------|
| `ads-launch/google-ads-editor-import.csv` | Regenerated (v4) |
| `ads-launch/build_stage1_editor_package.py` | ST evidence keywords + negatives + Admin RSA + `stage1-v4` |
| `ads-launch/_evidence_search_terms.json` | Aggregated keep/kill cites |
| `ads-launch/LAUNCH-SHEET.md` | Updated |
| `ads-launch/FULL-BUILD-REPORT.md` | This file |
| `ads-launch/IMPLEMENTATION-REPORT.md` | Pointer |
| `xray/docs/ads-launch/*` | Mirrored |
| `xray/launch-control.html` | Step 6 hint → v4 evidence package |

---

*End of report — v4 evidence fold from Editor performance exports. No Ads API; no invented metrics; no live enable.*
