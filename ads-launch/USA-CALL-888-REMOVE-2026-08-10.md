# USA Call 888 remove — 2026-08-10

Account `496-715-1855` only. AU `573-539-1940` untouched. Brand not re-enabled. Campaign status not changed.

Toolkit: `~/Developer/shoutgeorge-ads/scripts/remove_vc_us_call_888.py` (`.venv` + gitignored `.env`). No tokens in this repo. No email. No commit.

Live public number **(310) 730-9126** / `3107309126` asset `404927491581` — **kept ENABLED**.

## What was unlinked (associations removed)

All 888 Call links — PAUSED or otherwise — **REMOVED** so they cannot be flipped back on.

| Level | Count | Assets | Result |
|-------|------:|--------|--------|
| Campaign Call | **18** | 964 `49435983302` (12), 964 museum `49435983308` (4), 954 `405704361176` (2 on CORE+ROLES) | **REMOVED** |
| Ad group Call | **21** | all VC_* on `49435983302` | **REMOVED** |
| Account Call | **1** | `49435983302` | **REMOVED** |

310 campaign Call on `VC_US_S_CORE` + `VC_US_S_ROLES` and account 310 were **not mutated**.

## What was not deleted (library)

Google Ads API **cannot delete Call assets**. `AssetOperation` is create/update only — no `remove`. No AssetService RPC was sent after that was confirmed. No retry.

Still in the USA Call library (unlinked, not serving):

| Asset ID | Phone | Note |
|----------|-------|------|
| `405704361176` | `888-954-8644` | created tonight by mistake — unlinked; API cannot delete |
| `49435983302` | `(888) 964-8644` | legacy — unlinked; API cannot delete |
| `49435983308` | `(888) 964 8644` | museum — unlinked; API cannot delete |

If Ads UI still lists them under **Assets → Call**, try deleting there (954 is the most likely to allow UI delete). Legacy 964 may refuse even in UI.

## Verify

| Where | Phone | Asset | Link |
|-------|-------|-------|------|
| `VC_US_S_CORE` | `(310) 730-9126` | `404927491581` | **ENABLED** |
| `VC_US_S_ROLES` | `(310) 730-9126` | `404927491581` | **ENABLED** |
| Account Call | `(310) 730-9126` | `404927491581` | **ENABLED** |

Digit check on live VC_* + account Call: **`3107309126`**.

**ENABLED 888 anywhere:** none (campaign + account). All former 888 campaign/account links are **REMOVED** (Search still returns those historical rows; they are not serving).

AU not queried. No RSA / sitelink / callout / snippet / lead form / image changes. No new assets created. 310 not deleted.

## Google errors

- Unlink mutates: **none** (18 + 21 + 1 all OK).
- Asset delete: **not attempted as an RPC** — `AssetOperation` has no `remove` field (API v21). Reported, not retried.

## API op count

| Step | Service | RPCs | Mutate ops | Result |
|------|---------|-----:|-----------:|--------|
| Probe Search 1–4 | `GoogleAdsService.Search` (campaign / AG / customer / library CALL) | 4 | 0 | inventory |
| Unlink campaign | `CampaignAssetService.mutate` REMOVE | 1 | **18** | OK |
| Unlink ad group | `AdGroupAssetService.mutate` REMOVE | 1 | **21** | OK |
| Unlink account | `CustomerAssetService.mutate` REMOVE | 1 | **1** | OK |
| Asset delete | — | 0 | 0 | skipped (no remove field) |
| Verify Search 1–3 | `GoogleAdsService.Search` (campaign / library / customer CALL) | 3 | 0 | 310 only ENABLED |

**Total: 10 RPCs · 40 mutate ops · 7 Search ops.** No `RESOURCE_EXHAUSTED`.

Dump (toolkit, not this repo): `shoutgeorge-ads/output/vc-us-call-888-remove-probe.json`, `shoutgeorge-ads/output/vc-us-call-888-remove.json`.

## Ads UI glance (George)

One screen: **Assets → Call**.

Expect **(310) 730-9126** as the live Call. 888 should not be serving. Library may still *list* the three 888 numbers (API cannot wipe them). If any 888 still shows as usable, delete in that UI.
