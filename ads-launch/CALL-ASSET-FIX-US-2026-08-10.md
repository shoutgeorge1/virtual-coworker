# USA Call asset fix — 2026-08-10

Account `496-715-1855` only. AU untouched. Brand campaigns not re-enabled. Pickup on 954 is VC ops, not Ads.

Correct number: **(888) 954-8644** / `8889548644`  
Wrong number: **(888) 964-8644** / `8889648644` (one digit typo)

## Where 964 was found

Two Call **assets** (still in library; assets have no pause status):

| Asset ID | Phone string | Class |
|----------|--------------|-------|
| `49435983302` | `(888) 964-8644` | wrong |
| `49435983308` | `(888) 964 8644` | wrong (space format) |

**Associations (38 total):**

- **Campaign-level (16):** all already **PAUSED** before this fix — including `VC_US_S_CORE` + `VC_US_S_ROLES`, plus old museum Search campaigns. No Brand / `PM_*` Call association found.
- **Ad group-level (21) — this was serving:** all **ENABLED** on `VC_US_S_*` against asset `49435983302`. CORE: `Hire_VA_PH`, `Offshore_VA_PH`, `Agency_PH`. ROLES: 18 role AGs (Digital Marketing / Social / Admin / Accounting / Bookkeeping / CS / HR / Recruitment / Sales × Hire+Outsource, plus `Admin_City_Test`).
- **Account-level (1):** customer_asset for `49435983302` already **PAUSED**.

No existing **954** Call asset in the account.

**310** `(310) 730-9126` asset `404927491581`: ENABLED on `VC_US_S_CORE` + `VC_US_S_ROLES` campaign Call links. Also ENABLED as account-level customer_asset — **left alone**.

## What we did (API mutates)

Toolkit script: `~/Developer/shoutgeorge-ads/scripts/fix_vc_us_call_assets.py` (`.venv` + gitignored `.env`). No tokens copied into this repo.

| Op | Service | Items | Result |
|----|---------|------:|--------|
| Pause 310 on VC_* campaign Call | `CampaignAssetService.mutate` | 2 | PAUSED `24117249292~404927491581~CALL`, `24117249295~404927491581~CALL` |
| Pause 964 on VC_* ad groups | `AdGroupAssetService.mutate` | 21 | all 21 AG Call links → PAUSED |
| Create 954 Call asset | `AssetService.mutate` | 1 | created asset **`405704361176`** phone `888-954-8644` country US |
| Attach 954 to CORE + ROLES | `CampaignAssetService.mutate` | 2 | ENABLED campaign Call on `VC_US_S_CORE` + `VC_US_S_ROLES` |

Did **not**: re-pause already-paused 964 campaign/account links; touch AU; change RSA/keywords/campaign status; attach 954 to Brand; create 310; pause 310 account-wide.

## Verify (post-mutate Search)

`VC_*` campaign Call assets:

| Campaign | Phone | Asset | Link |
|----------|-------|-------|------|
| `VC_US_S_CORE` | `888-954-8644` | `405704361176` | **ENABLED** |
| `VC_US_S_ROLES` | `888-954-8644` | `405704361176` | **ENABLED** |
| CORE + ROLES | `(888) 964-8644` | `49435983302` | PAUSED |
| CORE + ROLES | `(310) 730-9126` | `404927491581` | PAUSED |

Digit check: live VC_* Call string is **954** not 964 (`8889548644`).

All 21 VC_* ad-group 964 Call links: **PAUSED**. No other ENABLED AG Call on VC_*.

## API hygiene

- Search: 4 tiny CALL-only queries (asset / campaign_asset / ad_group_asset / customer_asset).
- Mutate: 4 calls, 26 items total (2 + 21 + 1 + 2).
- Verify: 2 cheap Searches (VC_* campaign Call + VC_* AG Call).
- No `RESOURCE_EXHAUSTED`. No errors. AU not queried.

Probe/mutate dumps (toolkit, not this repo): `shoutgeorge-ads/output/vc-us-call-asset-probe.json`, `vc-us-call-asset-mutate.json`.

## Honest UI leftover

Ads UI **Assets** library will still **list** the two 964 Call assets (`49435983302`, `49435983308`) — they are not deleted; they just are not serving. Account-level **310** customer_asset is still **ENABLED** (intentional). Old paused museum campaigns still have paused 964 campaign links. Worth a 10-second human glance on CORE/ROLES Assets → Call that the extension shows **888-954-8644** only.

Not committed. No email.
