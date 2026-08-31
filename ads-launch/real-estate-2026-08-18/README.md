# US real-estate VA Editor package — 18 Aug 2026

Label: `VC_REAL_ESTATE_TEST_2026-08-18`
Account: USA `496-715-1855` only. Do not import into Australia.
Campaign: `VC_US_S_ROLES` (do not create a new campaign).
Final URL: `https://www.virtualcoworker.app/us/real-estate`
Bidding / budget / geo: unchanged. Campaign Status, Budget, and Bid Strategy columns are blank.

API mutations were not used. Access is Basic, but the permanent Editor-only rule still applies.

## Already on the campaign (do not duplicate)

`VC_US_S_ROLES` already has these shared negative lists Enabled:

- `VC_US_S_🚫_Sniper`
- `VC_US_S_🥊_Competitors`
- `VC_US_S_🚫_JobSeekers`

Do not attach copies at ad-group level.

## Import order

1. Google Ads Editor → USA account → **Account → Import from file** → `01-adgroups-keywords-rsas-us.csv`
2. Review: 3 new ad groups Enabled, keywords, 2 RSAs each, job-seeker Exact negatives, label `VC_REAL_ESTATE_TEST_2026-08-18`.
3. **Post**. Wait until all 3 ad groups show Eligible (or Eligible limited) and RSAs are serving.
4. Import `02-cross-negatives-us.csv` (Phrase cross-negatives). Post.
5. Import `03-pause-original-broad-hire-va-ph-us.csv`. This pauses **only** Broad `virtual assistant for real estate investors` in `VC_US_S_CORE` / `Hire_VA_PH`. Post.

Do not import `optional-overlap-pauses-george-review-us.csv` unless George approves. That file would pause overlapping Exact/Phrase terms still living in `Hire_VA_PH` and `Offshore_VA_PH`.

## Rollback

Import `99-rollback-us.csv`: pauses the three new ad groups and re-enables the original Broad keyword in `Hire_VA_PH`. Does not delete ads, keywords, or the landing page.

## What this package does not do

- Does not change Maximize Clicks, $150/$100 budgets, $30 CPC ceiling, US Presence, or conversion goals
- Does not reactivate paused ad groups
- Does not pause `virtual assistant agency in usa` (still Enabled Exact+Phrase in Hire_VA_PH; job-seeker conversion)
- Does not pause the same Broad keyword inside `Hire_VA_PH_offer_LP` (George call)
- Does not add US/USA/remote/hire/hiring/assistant/virtual assistant as negatives
- Does not touch Australia or Brand
