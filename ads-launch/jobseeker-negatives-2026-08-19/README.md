# Job-seeker negatives — daily checklist item 9 (19 Aug 2026)

Incremental Editor file. **Does not replace** `google-ads-editor-campaign-negatives-us.csv` / `-au.csv`.

Import: Google Ads Editor → **Keywords, Negative** → **Make multiple changes only**. Phrase only. CORE + ROLES. Not Brand. Not COMP.

File: `google-ads-editor-jobseeker-negatives.csv`  
Comment: `VC_Neg_JobSeekers_Daily_2026-08-19 · Phrase/Exact · do not add competitor brands`

## What this file adds

Same **8 Phrase** terms on all four campaigns (32 rows):

`job` · `jobs` · `career` · `careers` · `salary` · `apply` · `indeed` · `onlinejobs`

| Campaign | Account | Rows | Match |
|---|---|---|---|
| `VC_US_S_CORE` | 496-715-1855 | 8 | Phrase |
| `VC_US_S_ROLES` | 496-715-1855 | 8 | Phrase |
| `VC_AU_S_CORE` | 573-539-1940 | 8 | Phrase |
| `VC_AU_S_ROLES` | 573-539-1940 | 8 | Phrase |

No Extra Phrase/Exact rows. Every leaking search term below already contains one of those Phrase tokens (`virtual assistant jobs` is covered by Phrase `jobs`).

## Already Broad in the Stage 1 files (leave those CSVs alone)

On **all four** CORE/ROLES campaigns, the Stage 1 campaign-negatives CSVs already have these as **Broad** (not Phrase/Exact):

`job`, `jobs`, `career`, `careers`, `salary`, `apply`, `indeed`, `onlinejobs`

Plus Broad close variants that this file does **not** re-add: `online jobs`, `online job`, `job board` is not a Stage 1 root (only `job listings` / `job opening` / `virtual assistant jobs` etc.), `wfh job`, `remote job`, `remote jobs`, `onlinejobs.ph`, `onlinejobs ph`, `onlinejobsph`.

US also has a separate Phrase cohort `VC_Neg_JobSeekers_Live` (WFH / “work as” junk, 2026-08-06). That list does **not** include these eight roots as Phrase.

Live instruction is Phrase or Exact. Broad in the old file is why job-seeker queries kept leaking.

## Leaking search terms used (do not paste these as extra negatives)

Mined from `_last7_search_terms.json`, `_today_search_terms.json`, and `_tmp_search_terms_2026-08-08-to-14.json`.

**Paid US leaks** (covered by Phrase `job` / `jobs` / `careers`):

| Search term | Cost | Clicks | Campaigns |
|---|---|---|---|
| virtual assistant jobs | $44.38 | 14 | CORE + ROLES |
| virtual assistant jobs remote | $18.08 | 6 | CORE + ROLES |
| virtual assistant job board | $8.48 | 2 | ROLES |
| va jobs | $8.40 | 2 | ROLES |
| virtual assistant careers | $8.12 | 2 | ROLES |
| digital assistant remote jobs | $4.86 | 2 | CORE |
| virtual assistant job | $4.74 | 2 | CORE + ROLES |
| remote job philippines | $4.70 | 2 | CORE |

**Zero-cost US impressions** (also covered): `find a virtual assistant job`, `freelance virtual assistant jobs`, `online job virtual assistant`, `online jobs va`, `remote assistant jobs`, `remote job virtual assistant`, `remote virtual assistant jobs`, `virtual assistant jobs near me`, `virtual assistant work careers`, `online social media manager jobs`, `social media assistant jobs`, `administrative assistant jobs remote`, `virtual assistant apply`, `virtual assistant apply now`, `virtual assistant job remote`, `where can i apply to be a virtual assistant`, `appointment setter jobs remote`, `i need a va careers`, `how to apply in va`, `outsourced doers apply online`.

AU Aug 8–14 dump: **0** job-seeker leaks. Same 8 Phrase terms still go on AU CORE + ROLES so match type is consistent.

No `indeed`, `onlinejobs`, or `salary` queries in these dumps. They are still in the Phrase set.

## Do not dump competitor brands

Leave competitor names in the search-term report for the competitor campaign. Do **not** add to this file:

24x7 · outsourcing angel · belay · myoutdesk · wing · virtualstaff · rippling · (or similar)

Do not add Brand or COMP campaigns here.
