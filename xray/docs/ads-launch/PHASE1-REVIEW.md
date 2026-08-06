# Phase 1 enable review manifests

- Generated: 2026-08-06 17:37 UTC
- Purpose: **review-only** enable ladder — not an Enabled import file
- Every keyword Status = **Paused** (do not enable from these CSVs)
- Source of enable order: `PHASED-ACTIVATION.md`

## Tier definitions

| Tier | Meaning |
|------|---------|
| **1A** | Strongest PH/Filipino/offshore long-tail **Exact** (hire / VA / outsource + PH geo). Not bare `philippines` service heads. |
| **1B** | PH-shaped **Phrase**, or slightly broader PH **Exact** (geo + role/service without hire/VA/outsource strength). |
| **2** | Broader category Exact/Phrase **without** PH geo (Roles). |
| **3** | Generic Core heads later (no PH geo). |

## Files

- `phase1-enable-manifest-us.csv` — 784 keywords (Account `496-715-1855`)
- `phase1-enable-manifest-au.csv` — 784 keywords (Account `573-539-1940`)

## Counts

| Tier | US | AU |
|------|----|----|
| 1A | 278 | 278 |
| 1B | 321 | 321 |
| 2 | 146 | 146 |
| 3 | 39 | 39 |
| **Total** | **784** | **784** |

## Operator notes

1. Review 1A first (US before AU), then 1B — still leave Status=Paused until TRAFFIC READY + explicit George Enable approval (Zoho/CRM is parallel, not a traffic gate).
2. Bare Core heads are Tier **3** — later, not first.
3. Generic `philippines` + service heads without hire/VA/outsource are **1B**, not 1A.
4. Import/Post of the Editor package is separate; these manifests do not replace Editor import CSVs.

