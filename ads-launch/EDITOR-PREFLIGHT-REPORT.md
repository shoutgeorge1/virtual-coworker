# Editor preflight report

- Generated: 2026-08-06 12:53 UTC
- LP version (suffix): `stage1-v7` (unchanged)
- Package hygiene: Editor ValueTrack + campaign CPC cap + US/AU split

## Verdict

- **SAFE TO IMPORT FOR REVIEW** (local QA passed)
- **IMPORT/POST/ENABLE NOT PERFORMED**
- Import = draft on your computer. Post = upload to Google (still Paused).
- Enable is a separate explicit decision after launch gates are green.

## Files

| File | Use |
|------|-----|
| `google-ads-editor-import-us.csv` (1236 rows) | **Preferred** — import into USA `496-715-1855` only |
| `google-ads-editor-import-au.csv` (1236 rows) | **Preferred** — import into AU `573-539-1940` only |
| `google-ads-editor-import.csv` / `-multi-account.csv` (2472 rows) | Manager multi-account only — every row has Account |

## Counts

- Campaigns: 4 (all Paused)
- Ad groups: 40
- Positive keywords: 1568
- RSAs: 116
- Active campaign negatives: 700 rows (175 unique × 4 campaigns)
- Commercial holdouts (not imported): 16

## Budgets + bid caps (campaign only)

- `VC_US_S_CORE` · Account `496-715-1855` · Budget 75/day · Maximum CPC bid limit 8 · Maximize Clicks · Paused
- `VC_US_S_ROLES` · Account `496-715-1855` · Budget 50/day · Maximum CPC bid limit 8 · Maximize Clicks · Paused
- `VC_AU_S_CORE` · Account `573-539-1940` · Budget 75/day · Maximum CPC bid limit 6 · Maximize Clicks · Paused
- `VC_AU_S_ROLES` · Account `573-539-1940` · Budget 50/day · Maximum CPC bid limit 6 · Maximize Clicks · Paused

## Tracking

- Tracking template (campaign): `{lpurl}`
- Final URL suffix (campaign): `utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}&utm_device={device}&lp_version=stage1-v7`
- No `{_campaign}` / `{_adgroup}` custom params

## Negative holdouts (not in CSV)

Held out so cost/review/comparison employer research is not blocked pre-launch:

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

## Operator path

1. Download fresh USA + AU accounts into Editor.
2. Import **US split** into USA → Check changes → leave Paused.
3. Import **AU split** into AU → Check changes → leave Paused.
4. Post only after review (still Paused). Enable is separate.

