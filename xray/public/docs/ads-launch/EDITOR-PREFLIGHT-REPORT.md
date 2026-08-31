# Editor preflight report

- Generated: 2026-08-08 20:11 UTC
- LP version (suffix): `stage1-v7` (unchanged)
- Package hygiene: Editor ValueTrack + campaign CPC cap + US/AU split

## Operating rule (locked)

**Existing account remains unchanged. New `VC_*` campaigns are a separate Stage 1 system.**

- Leave existing `PM_*` campaigns, shared negative lists, Zoho/Zapier conversion actions, and historical reporting alone.
- Campaign-level negatives ship in a **separate MMC CSV** (cap 220 curated + `VC_Neg_JobSeekers_Live` on `VC_US_*` only) — **not** inside the main Account Import, **not** account shared / `PM_*` mega lists.
- **Why separate:** Account-importing `Keyword` + `Campaign negative` rows dual-writes blank/`Unkown` ad groups packed with Enabled Broad *positives* (confirmed AU Editor DB 2026-08-08). Main CSV has zero of those rows.
- Do **not** attach older account shared / `PM_*` negative lists to `VC_*` after Import/Post.
- Do **not** use audiences to restrict targeting for initial Search launch (Observation later; ignore customer-lifecycle warnings until Zoho/first-party data).
- Import ≠ live. Every campaign stays **Paused**. No Enable from this package.

## Verdict

- **SAFE TO IMPORT FOR REVIEW** (local QA passed)
- **IMPORT/POST/ENABLE NOT PERFORMED**
- Import = draft on your computer. Post = upload to Google (still Paused).
- Enable is a separate explicit decision after TRAFFIC READY + George approval (CRM READY / OPTIMIZATION READY are parallel — not traffic gates).

## Files

| File | Use |
|------|-----|
| `google-ads-editor-import-us.csv` (886 rows) | **Preferred** — Account Import into USA `496-715-1855` only |
| `google-ads-editor-import-au.csv` (886 rows) | **Preferred** — Account Import into AU `573-539-1940` only |
| `google-ads-editor-campaign-negatives-us.csv` (366 rows) | **Keywords, Negative → Make multiple changes** (USA) — do **not** Account Import |
| `google-ads-editor-campaign-negatives-au.csv` (344 rows) | **Keywords, Negative → Make multiple changes** (AU) — do **not** Account Import |
| `google-ads-editor-import.csv` / `-multi-account.csv` (1772 rows) | Manager multi-account only — every row has Account |
| `phase1-enable-manifest-us.csv` / `-au.csv` | **Review-only** enable ladder (tiers 1A/1B/2/3 + PHRASE_HOLD + LIVE_PAUSED; all Paused) |
| `PHASE1-REVIEW.md` | Tier definitions + per-market counts |
| `VC-NEG-JOBSEEKERS-LIVE.md` | Live job-seeker Phrase cohort (`VC_Neg_JobSeekers_Live`) |
| `VC-KEYWORDS-PAUSED-LIVE.md` | Live-paused positives (`VC_Keywords_Paused_Live`) |

## Counts

- Campaigns: 4 (all Paused)
- Ad groups: 40
- Positive keywords: 1568 (Exact + Phrase only — **zero Broad positives**)
- Live-paused positives (`VC_Keywords_Paused_Live`): 538 rows (US+AU; keep Paused — George paused live USA Exact junk/general/job-seeker-y terms; synced from Editor DB ape_4967151855 (Get recent changes). Phrase stays paused (Exact-only bidding).)
- RSAs: 116
- Campaign negatives (MMC file): 710 rows (183 unique texts) — Stage1 curated Broad on all 4 VC_* campaigns + `VC_Neg_JobSeekers_Live` Phrase on `VC_US_*` only
- `VC_Neg_JobSeekers_Live`: 11 Phrase terms × 2 US campaigns (22 rows) — job-seeker / WFH junk from live US search terms (2026-08-06)
- Commercial holdouts (not imported): 19 (includes pay rate / hourly rate / virtual assistant reviews + cost/pricing/review research terms)
- Employer-research Broad canaries: 12 (QA fails if active Broad negs would block them; includes `va workers ph`)
- Shared-list / audience / PM_* rows: **none** (isolation QA)
- Bare Broad negative `workers`: **removed** (employer shorthand — do not restore)

## Budgets + bid caps (campaign only)

- `VC_US_S_CORE` · Account `496-715-1855` · Budget 75/day · Maximum CPC bid limit 12 · Maximize Clicks · Paused
- `VC_US_S_ROLES` · Account `496-715-1855` · Budget 50/day · Maximum CPC bid limit 10 · Maximize Clicks · Paused
- `VC_AU_S_CORE` · Account `573-539-1940` · Budget 75/day · Maximum CPC bid limit 6 · Maximize Clicks · Paused
- `VC_AU_S_ROLES` · Account `573-539-1940` · Budget 50/day · Maximum CPC bid limit 6 · Maximize Clicks · Paused

## Tracking (UTMs)

- Tracking template (campaign): `{lpurl}`
- Final URL suffix (campaign): `utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}&utm_device={device}&lp_version=stage1-v7`
- No `{_campaign}` / `{_adgroup}` custom params
- **Final URL host (production):** `www.virtualcoworker.app` with path markets (`/us`, `/au`, category pages). One host — not two country domains. Preview `vision-three-alpha.vercel.app` still exists but **Import CSVs use www**. Apex `virtualcoworker.app` → 308 → `www`. Domain ≠ TRAFFIC READY substitute. Override: `ADS_FINAL_URL_HOST=host python3 ads-launch/build_stage1_editor_package.py`.

## Conversion actions + campaign goals (after Post — Ads UI)

Editor CSV does **not** fully express conversion goals. After Post, George sets these in Google Ads UI. Do **not** replace or delete old Zoho/Zapier conversion actions — leave them for historical reporting.

### New conversion actions (via **new** per-market GTM — plan, not live yet)

| Action (create new) | Fires when | Primary for Stage 1? |
|---------------------|------------|----------------------|
| Employer inquiry delivered | `employer_inquiry_submitted` after durable delivery (not log-only) | **Yes** |
| Qualified phone call (~60s) | Call tracking / CallRail when wired (phone click alone ≠ qualified) | **Yes** (when ready) |

Wire tags in the **new** US/AU GTM containers → new Ads conversion actions. Keep `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false` until mapping is tested. Details: `10-tracking-event-spec.md` · `DECISIONS.md`.

### Campaign-specific goals (required for each `VC_*`)

1. Open each `VC_US_*` / `VC_AU_*` campaign → **Settings → Goals** (or Goals on the campaign).
2. Choose **campaign-specific** goals — do **not** use the account-default goal basket that includes old Zoho/Zapier micros.
3. Include **only** the new actions above (inquiry delivered + phone ~60s when ready).
4. Leave Maximize Clicks for now — do **not** switch to Max Conversions until those new actions are verified.

Launch Control checklist encodes the same steps in plain English.

## Audiences

- **Launch:** no audience targeting restrictions on `VC_*`.
- **Later:** Observation-only audiences OK once first-party/Zoho data exists.
- Ignore customer-lifecycle / audience warnings until then — not launch-critical.

## Negative holdouts (not in CSV)

Held out so cost/review/comparison/rate employer research is not blocked pre-launch (**19** terms; not in import CSVs):

- `review`
- `reviews`
- `pricing`
- `virtual assistant cost`
- `virtual assistant philippines cost`
- `cost of a virtual assistant`
- `cost of virtual assistant philippines`
- `how much does a virtual assistant cost`
- `how much is a virtual assistant`
- `how much does a va cost`
- `how much do virtual assistants cost`
- `top 10 virtual assistant companies`
- `top 10`
- `cheap`
- `cheapest`
- `filipina va`
- `pay rate`
- `hourly rate`
- `virtual assistant reviews`

Competitor-named review/pricing terms (e.g. `bruntwork reviews`) stay active.
Job-seeker / medical / Spanish / platform Stage1 Broad negatives stay active.

## `VC_Neg_JobSeekers_Live` (live ST cohort)

- Topic: job-seeker / WFH junk from live US search terms (2026-08-06)
- Scope: `VC_US_S_CORE` + `VC_US_S_ROLES` only (Phrase campaign negatives)
- Spot in Editor: Keywords → filter Comment contains `VC_Neg_JobSeekers_Live` (or search that string)
- **Not** mixed into the curated Stage1 Broad blob comments
- **Not** an account shared / `PM_*` mega list attach
- Bare Broad `workers` intentionally **absent** (`va workers ph` is employer shorthand)

Phrase terms in this cohort:

- `"work as"` (Phrase)
- `"work from home customer service"` (Phrase)
- `"work from home customer service representative"` (Phrase)
- `"work from home virtual assistant"` (Phrase)
- `"work from home social media manager"` (Phrase)
- `"work from home representative"` (Phrase)
- `"customer service work from home"` (Phrase)
- `"customer support representative work from home"` (Phrase)
- `"customer service representative wfh"` (Phrase)
- `"virtual assistant work from home"` (Phrase)
- `"work as customer service from home"` (Phrase)

Details: `VC-NEG-JOBSEEKERS-LIVE.md`.

## `VC_Keywords_Paused_Live` (live-paused positives)

- Date: 2026-08-07
- Reason: George paused live USA Exact junk/general/job-seeker-y terms; synced from Editor DB ape_4967151855 (Get recent changes). Phrase stays paused (Exact-only bidding).
- Scope: matching positive keyword texts on `VC_US_*` and `VC_AU_*` (Exact + Phrase when present); Keyword Status stays **Paused**
- Spot in Editor: Keywords → filter Comment contains `VC_Keywords_Paused_Live`
- Enable manifests mark these as tier **LIVE_PAUSED** — do not enable
- Details: `VC-KEYWORDS-PAUSED-LIVE.md`

## Phase 1 review manifests

- `phase1-enable-manifest-us.csv` / `phase1-enable-manifest-au.csv` — keyword enable ladder with tiers **1A / 1B / 2 / 3 / PHRASE_HOLD / LIVE_PAUSED** (all **Paused**).
- `PHASE1-REVIEW.md` — tier definitions + counts.
- These are **not** Enabled import files. Enable order follows `PHASED-ACTIVATION.md` after TRAFFIC READY + explicit George approval.

## Operator path

1. Leave existing account campaigns and settings unchanged (no dig/delete/rewrite/pause pass on historical structure).
2. Clear **TRAFFIC READY** (durable delivery + live test + named responder).
3. **Domain live:** `www.virtualcoworker.app` — package Final URLs already on www. Confirm `/us` `/au` `/ph` LPs still 200 before Import.
4. Download fresh USA + AU accounts into Editor (read-only sync).
5. Import **US split** (`google-ads-editor-import-us.csv`) into USA → Check changes → leave **Paused**. Do **not** Account-import the negatives CSV.
6. Import **AU split** (`google-ads-editor-import-au.csv`) into AU → Check changes → leave **Paused**.
7. Add campaign negatives via **Keywords and Targeting → Keywords, Negative → Make multiple changes** using `google-ads-editor-campaign-negatives-*.csv` (campaign column, no ad group; Add as campaign-level). If AU already has the 172 Stage1 campaign negs from an earlier import, skip re-adding — just delete any blank/`Unkown` ad groups with Broad positives.
8. Confirm every Final URL uses `www.virtualcoworker.app` (not `*.vercel.app`).
9. Confirm `VC_*` Stage1 curated Broad negs + `VC_Neg_JobSeekers_Live` Phrase cohort on `VC_US_*` — **do not** attach older `PM_*` / account shared mega lists.
10. Review Phase 1 manifests (1A → 1B) — still Paused until enable approval. Skip tier **LIVE_PAUSED** (`VC_Keywords_Paused_Live`).
11. Post only after review (still Paused). Then set campaign-specific goals in Ads UI.
12. Enable is a separate explicit decision after TRAFFIC READY — never from Import/Post alone. Still **NOT** paid-ready until TRAFFIC READY.

