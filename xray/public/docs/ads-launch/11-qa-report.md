# 11 — QA report (v6 · RSA×3)

**Date:** 2026-08-05 · Vision casting on prod · No Ads enable · Package rebuilt to 2-campaign architecture + 3 RSAs/main AG

---

## Commands + exact results

| Check | Command | Result |
|-------|---------|--------|
| Editor package builder | `python3 ads-launch/build_stage1_editor_package.py` | **PASS** — QA OK; **4** campaigns; **2536** rows; **116** RSAs; `lp_version=stage1-v6` |
| Historical analyzer | `python3 ads-launch/analyze_historical_performance.py` | **PASS** (prior) — JSON written |

Vision typecheck/test/build not re-run this pass (Ads CSV/docs + debrief; microsite polish tracked separately).

---

## Package validation (v6 · RSA×3)

| Item | Result |
|------|--------|
| Campaigns | `VC_US_S_CORE`, `VC_US_S_ROLES`, `VC_AU_S_CORE`, `VC_AU_S_ROLES` |
| Budgets | US 75/50 · AU 75/50 · Max CPC 8/6 |
| Core share | ~60% daily |
| Positive KWs | 1568 Exact+Phrase |
| RSAs | **116** — 38 main AGs × 3 + 2 city × 1; full 15/4, no blanks |
| Unique negatives | 191 × 4 |
| Final URLs | Category paths only; no `?role=`; no WP; no Brand generics |
| Double UTM | Tracking template `{lpurl}` only |
| Consult language | Builder QA rejects |
| Brand keywords | Absent (deferred) |
| All statuses | Paused |

---

## Not run (by design / blockers)

- Google Ads Editor import / enable
- Real lead email delivery for paid
- CallRail / Zoho live tests

---

## Residual QA risks

1. Careers `/ph` is a Stage 1 default.  
2. Lead delivery TEMPORARY log-only on prod — replace before paid.  
3. Budgets/CPC placeholders — need explicit George enable approval.  
4. Legacy `PM_*` Brand may still bleed outside this package.  
5. Controlled-tier HR/recruitment thin ST.
