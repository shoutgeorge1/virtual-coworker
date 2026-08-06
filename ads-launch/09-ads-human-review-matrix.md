# 09 — Human-readable Ads review matrix

Use this **before** any enable. CSV: `google-ads-editor-import.csv` · all **Paused**.

---

## Account checklist

| # | Check | Expected |
|---|-------|----------|
| 1 | Campaign count | 22 (11 US + 11 AU) |
| 2 | Brand present | `VC_US_S_BRAND` + `VC_AU_S_BRAND` |
| 3 | Core present | `VC_*_S_CORE_hire_va` |
| 4 | 9 role campaigns / market | digital…sales |
| 5 | Positive match types | Exact + Phrase only |
| 6 | Broad positives | **0** |
| 7 | Status columns | Campaign / AG / Keyword / Ad = **Paused** |
| 8 | Tracking template | `{lpurl}` (no utm in template) |
| 9 | Final URL suffix | utms + `lp_version=stage1-v5` once |
| 10 | Final URLs | category routes or market root for Brand — **no** `?role=` |
| 11 | WP URLs | **none** |
| 12 | Consult / demo language in RSA | **none** |
| 13 | Forbidden claims | no Top 1%, $/hr, 80%, guaranteed |
| 14 | Budgets / Max CPC | still `[APPROVAL_*]` placeholders |
| 15 | Negatives | 191 unique × 22 campaigns; no bare hire/hiring |
| 16 | AU phone assets | none invented in CSV |

---

## Spot-check table (sample)

| Campaign | AG | Final URL | Notes |
|----------|----|-----------|-------|
| VC_US_S_BRAND | Brand | `/us` | Brand Exact |
| VC_US_S_CORE_hire_va | Hire_VA_PH | `/us/administrative-support` | Core hire |
| VC_US_S_ROLE_bookkeeping | Bookkeeping_Hire_PH | `/us/bookkeeping` | Role |
| VC_AU_S_ROLE_social_media | Social_Media_Hire_PH | `/au/social-media` | AU category |
| VC_AU_S_BRAND | Brand_Nav | `/au` | Form-primary LP |

---

## Negative row repetition

Editor CSV repeats the same **191** Broad negatives on **each** of **22** campaigns → **4,202** negative rows. This is intentional Editor import shape, not 4,202 unique concepts.

---

## Enable order (after approvals)

See `07-phased-activation-recommendation.md`. Do not enable from row-count confidence alone.
