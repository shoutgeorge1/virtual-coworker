# VC_Neg_JobSeekers_Live

Logical list name for a **separate** job-seeker / WFH junk cohort from live USA search terms (**2026-08-06**).

## What this is

- **Name:** `VC_Neg_JobSeekers_Live`
- **Topic:** job-seeker / WFH junk from live US search terms (2026-08-06)
- **Match:** Phrase (quoted keyword text in Editor CSV)
- **Campaigns:** `VC_US_S_CORE` and `VC_US_S_ROLES` only
- **Shape:** campaign-level negatives with a distinctive Comment (proven Editor import path)
- **Not:** Stage1 curated Broad blob, and **not** account shared / `PM_*` mega lists

Editor does not get a Shared Library list row here — the builder keeps the proven `Criterion Type = Campaign negative` CSV shape and labels the cohort in Comment so it stands out from curated Stage1 negatives.

## Spot in Editor

1. Import `ads-launch/google-ads-editor-import-us.csv` into USA (`496-715-1855`).
2. Open Keywords (or campaign negatives view).
3. Filter / search Comment for `VC_Neg_JobSeekers_Live`.

## Phrase terms

| Live search term (evidence) | Negative (Phrase) |
|----------------------------|-------------------|
| customer service work from home | `"customer service work from home"` |
| virtual assistant work from home | `"virtual assistant work from home"` |
| customer support representative work from home | `"customer support representative work from home"` |
| work from home customer service representative | `"work from home customer service representative"` |
| work from home virtual assistant | `"work from home virtual assistant"` |
| work from home social media manager | `"work from home social media manager"` |
| customer service representative wfh | `"customer service representative wfh"` |
| work as customer service from home | `"work as customer service from home"` |
| work from home customer service | `"work from home customer service"` |
| work from home representative | `"work from home representative"` |
| (pattern) work as … | `"work as"` |

## Explicitly not negated

- **`va workers ph`** — employer shorthand. Do **not** Broad-neg bare `workers`.
- Hire / Filipino / staffing-agency buyer terms.
- Ambiguous “remote …” role queries (watch list only).

## Source

One read-only GAQL `search_term_view` pull for `segments.date = 2026-08-06`, `campaign.name LIKE 'VC_US_%'`, customer `4967151855`. No Ads API mutations.
