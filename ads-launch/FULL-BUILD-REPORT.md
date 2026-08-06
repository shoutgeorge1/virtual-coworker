# Stage 1 Google Ads + LP — FULL BUILD REPORT (v5)

**For:** ChatGPT audit + George review  
**Generated:** 2026-08-05  
**Package:** `ads-launch/google-ads-editor-import.csv`  
**Builder:** `ads-launch/build_stage1_editor_package.py`  
**LP version:** `lp_version=stage1-v5`  
**Accounts:** USA `496-715-1855` · Australia `573-539-1940`  
**All Ads entities in CSV:** **Paused**  
**Live Ads / WP / deploy / commit:** none

---

## Executive verdict

Local Stage 1 stack is now **category-routed LPs + Brand/Core/Role Search package**, evidence-backed from ~2y Editor exports, with honest events and delivery blockers. **Not launch-ready** while recipients, budgets/CPC, AU phone decision, careers URL, Zoho, and CallRail timing remain open.

---

## What changed vs v4

| Gap | v5 fix |
|-----|--------|
| Final URLs `?role=` inert | `/us\|au/{category-slug}` |
| Brand deferred | Brand + Core campaigns added |
| Double UTM | Final URL suffix only |
| Consult RSA/LP language | Employer CTAs |
| No category LP engine | 9×2 routes + data config |
| No A/B | Stable A/B + QA override |
| Log-only leads by default | 503 unless channel or explicit flag |

---

## Deliverables index

| # | File |
|---|------|
| 1 | `01-current-state-audit.md` |
| 2 | `02-historical-data-audit.md` + `historical-performance-summary.json` |
| 3 | `03-search-term-category-findings.md` |
| 4 | `04-lp-matrix.md` |
| 5 | `05-ab-matrix.md` |
| 6 | `06-stage1-campaign-architecture.md` |
| 7 | `07-phased-activation-recommendation.md` |
| 8 | `google-ads-editor-import.csv` |
| 9 | `09-ads-human-review-matrix.md` |
| 10 | `10-tracking-event-spec.md` |
| 11 | `11-qa-report.md` |
| 12 | `12-blocker-decision-list.md` |

---

## Inventory (v5)

| Entity | Count |
|--------|------:|
| Campaigns | 22 |
| Ad groups | 46 |
| Positive keywords | 1604 (Exact 1218 · Phrase 386) |
| RSAs | 82 |
| Campaign negative rows | 4202 (191 unique × 22) |
| CSV rows | 6198 |

---

## Historical snapshot

| | USA | AU |
|--|----:|---:|
| Cost | $723,838.59 | $457,489.46 |
| Clicks | 87,060 | 49,457 |
| Conversions | 2,597.32 | 1,412.66 |
| All conv | 4,629.39 | 3,505.46 |
| ST raw → deduped | 66,869 → 66,465 | 26,211 → 26,132 |

Prior v4 benchmarks matched within ~0–1%. **Conversions ≠ All conv ≠ job orders.**

---

## Operator next

1. Review LPs + blockers list.  
2. Fill delivery + budgets/CPC + careers URL.  
3. Import CSV **Paused**.  
4. Enable only per `07-phased-activation-recommendation.md` after explicit approval.

*End of v5 report — local work only.*
