# Phase 1 enable review manifests

- Generated: 2026-08-08 20:11 UTC
- Purpose: **review-only** enable ladder — not an Enabled import file
- Every keyword Status = **Paused** (do not enable from these CSVs)
- Source of enable order: `PHASED-ACTIVATION.md`

## Tier definitions

| Tier | Meaning |
|------|---------|
| **1A** | Strongest PH/Filipino/offshore long-tail **Exact** (hire / VA / outsource + PH geo). Not bare `philippines` service heads. |
| **1B** | Broader PH **Exact** (geo + role/service without hire/VA/outsource strength). |
| **2** | Broader category **Exact** **without** PH geo (Roles). |
| **3** | Generic Core **Exact** heads later (no PH geo). |
| **PHRASE_HOLD** | All **Phrase** — live USA is Exact-only; keep Paused (do not enable with 1A/1B). |
| **LIVE_PAUSED** | George paused live Exact junk/general terms (2026-08-07) — keep **Paused**; do not enable. See `VC-KEYWORDS-PAUSED-LIVE.md`. |

## Files

- `phase1-enable-manifest-us.csv` — 784 keywords (Account `496-715-1855`)
- `phase1-enable-manifest-au.csv` — 784 keywords (Account `573-539-1940`)

## Counts

| Tier | US | AU |
|------|----|----|
| 1A | 129 | 129 |
| 1B | 107 | 107 |
| 2 | 83 | 83 |
| 3 | 23 | 23 |
| PHRASE_HOLD | 173 | 173 |
| LIVE_PAUSED | 269 | 269 |
| **Total** | **784** | **784** |

## Operator notes

1. Review 1A first (US before AU), then 1B — still leave Status=Paused until TRAFFIC READY + explicit George Enable approval (Zoho/CRM is parallel, not a traffic gate).
2. Bare Core heads are Tier **3** — later, not first.
3. Generic `philippines` + service heads without hire/VA/outsource are **1B**, not 1A.
4. Import/Post of the Editor package is separate; these manifests do not replace Editor import CSVs.
5. Live job-seeker Phrase cohort `VC_Neg_JobSeekers_Live` (job-seeker / WFH junk from live US search terms (2026-08-06)) is in the US Editor CSV on `VC_US_S_CORE` / `VC_US_S_ROLES` only — see `VC-NEG-JOBSEEKERS-LIVE.md`. Bare Broad `workers` is intentionally absent.
6. Live-paused positives (`VC_Keywords_Paused_Live`, tier **LIVE_PAUSED**) stay Paused — George paused live USA Exact junk/general/job-seeker-y terms; synced from Editor DB ape_4967151855 (Get recent changes). Phrase stays paused (Exact-only bidding). See `VC-KEYWORDS-PAUSED-LIVE.md`. George is not doing negatives yet.
7. Tier **PHRASE_HOLD** = all Phrase — live USA bids Exact-only; do not enable Phrase with 1A/1B.

