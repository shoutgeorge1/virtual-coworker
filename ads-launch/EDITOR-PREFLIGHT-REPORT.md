# Editor preflight report

- Generated: 2026-08-06 13:25 UTC
- LP version (suffix): `stage1-v7` (unchanged)
- Package hygiene: Editor ValueTrack + campaign CPC cap + US/AU split

## Operating rule (locked)

**Old account = historical archive. New `VC_*` = isolated clean system.**

- Leave old `PM_*` campaigns, shared mega negative lists, old Zoho/Zapier conversion actions, and historical reporting alone.
- This package attaches **only** curated campaign-level negatives (~172 unique, cap 220) — **not** account shared / `PM_*` 3000+ dumps.
- Do **not** attach account shared negative lists to `VC_*` after Import/Post.
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
| `google-ads-editor-import-us.csv` (1230 rows) | **Preferred** — import into USA `496-715-1855` only |
| `google-ads-editor-import-au.csv` (1230 rows) | **Preferred** — import into AU `573-539-1940` only |
| `google-ads-editor-import.csv` / `-multi-account.csv` (2460 rows) | Manager multi-account only — every row has Account |
| `phase1-enable-manifest-us.csv` / `-au.csv` | **Review-only** enable ladder (tiers 1A/1B/2/3; all Paused) |
| `PHASE1-REVIEW.md` | Tier definitions + per-market counts |

## Counts

- Campaigns: 4 (all Paused)
- Ad groups: 40
- Positive keywords: 1568
- RSAs: 116
- Active campaign negatives: 688 rows (172 unique × 4 campaigns) — VC-only curated, not shared mega lists
- Commercial holdouts (not imported): 19 (includes pay rate / hourly rate / virtual assistant reviews + cost/pricing/review research terms)
- Employer-research Broad canaries: 11 (QA fails if active Broad negs would block them)
- Shared-list / audience / PM_* rows: **none** (isolation QA)

## Budgets + bid caps (campaign only)

- `VC_US_S_CORE` · Account `496-715-1855` · Budget 75/day · Maximum CPC bid limit 8 · Maximize Clicks · Paused
- `VC_US_S_ROLES` · Account `496-715-1855` · Budget 50/day · Maximum CPC bid limit 8 · Maximize Clicks · Paused
- `VC_AU_S_CORE` · Account `573-539-1940` · Budget 75/day · Maximum CPC bid limit 6 · Maximize Clicks · Paused
- `VC_AU_S_ROLES` · Account `573-539-1940` · Budget 50/day · Maximum CPC bid limit 6 · Maximize Clicks · Paused

## Tracking (UTMs)

- Tracking template (campaign): `{lpurl}`
- Final URL suffix (campaign): `utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}&utm_device={device}&lp_version=stage1-v7`
- No `{_campaign}` / `{_adgroup}` custom params

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
Job-seeker / medical / Spanish / platform negatives stay active.

## Phase 1 review manifests

- `phase1-enable-manifest-us.csv` / `phase1-enable-manifest-au.csv` — keyword enable ladder with tiers **1A / 1B / 2 / 3** (all **Paused**).
- `PHASE1-REVIEW.md` — tier definitions + counts.
- These are **not** Enabled import files. Enable order follows `PHASED-ACTIVATION.md` after TRAFFIC READY + explicit George approval.

## Operator path

1. Leave old account machinery alone (no dig/delete/rewrite/pause binge tonight).
2. Download fresh USA + AU accounts into Editor (read-only sync).
3. Import **US split** into USA → Check changes → leave **Paused**.
4. Import **AU split** into AU → Check changes → leave **Paused**.
5. Confirm `VC_*` negatives are campaign-level curated only — **do not** attach shared mega lists.
6. Review Phase 1 manifests (1A → 1B) — still Paused until enable approval.
7. Post only after review (still Paused). Then set campaign-specific goals in Ads UI.
8. Enable is a separate explicit decision — never from Import/Post alone.

