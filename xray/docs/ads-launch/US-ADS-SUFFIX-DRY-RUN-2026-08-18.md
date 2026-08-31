# US Ads Final URL suffix — dry-run (no API mutation)

**Date:** 18 August 2026  
**Account:** US `496-715-1855`  
**AU:** not changed.

## Why

Live Ads still append `lp_version=stage1-v7`. Site code stamps `baseline_v1_2026_08`. The URL param will always drift. Least-drift option: **remove `lp_version` from the Ads suffix** and use the site event parameter as the only version.

UTMs and ValueTrack stay:

`utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}&utm_device={device}`

Google still appends `gclid` / `gbraid` / `wbraid` on the click. The site captures those plus `lp_version` from code.

## Diff (campaign-level)

| Campaign | Today (live inspect 18 Aug) | Proposed |
| --- | --- | --- |
| `VC_US_S_CORE` | `…&utm_device={device}&lp_version=stage1-v7` | `…&utm_device={device}` |
| `VC_US_S_ROLES` | same | same |

No keyword, RSA, bid, budget, or status change in this file.

## How to apply (Editor only — do not use the Ads API)

1. Open Google Ads Editor for US account `496-715-1855`.
2. Get recent changes.
3. **Account → Import → From file**  
   File: `ads-launch/google-ads-editor-us-suffix-drop-lp-version.csv`
4. Review: only Final URL suffix on the two `VC_US_*` campaigns. **Campaign status must stay Enabled.** If Editor marks them Paused, discard the import.
5. Post to account when the suffix diff is the only change.

Do **not** import `google-ads-editor-import-us.csv` for this. That package is still Paused-by-default.

## API

No Ads API mutate. No dry-run mutate call was made.

## After Post

Confirm a new click lands on `/us?utm_source=google&…&utm_device=…` **without** `lp_version=stage1-v7`.  
GA4 `lp_view.lp_version` should be `baseline_v1_2026_08`.
