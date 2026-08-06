# Ads launch — Stage 1 v6 (local)

**ChatGPT paste (start here):** [`CHATGPT-DEBRIEF.md`](./CHATGPT-DEBRIEF.md)  
Deep audit: [`CHATGPT-MEGA-AUDIT.md`](./CHATGPT-MEGA-AUDIT.md)  
Short index: [`FULL-BUILD-REPORT.md`](./FULL-BUILD-REPORT.md)

**Architecture:** 2 campaigns × 2 markets (`CORE` + `ROLES`) · Brand deferred · all **Paused**.

| # | Deliverable |
|---|-------------|
| DEBRIEF | [CHATGPT-DEBRIEF.md](./CHATGPT-DEBRIEF.md) |
| MEGA | [CHATGPT-MEGA-AUDIT.md](./CHATGPT-MEGA-AUDIT.md) |
| 0 | [DECISIONS.md](./DECISIONS.md) · [LAUNCH-SHEET.md](./LAUNCH-SHEET.md) · [PHASED-ACTIVATION.md](./PHASED-ACTIVATION.md) |
| 1 | [01-current-state-audit.md](./01-current-state-audit.md) |
| 2 | [02-historical-data-audit.md](./02-historical-data-audit.md) · [historical-performance-summary.json](./historical-performance-summary.json) |
| 3 | [03-search-term-category-findings.md](./03-search-term-category-findings.md) |
| 4 | [04-lp-matrix.md](./04-lp-matrix.md) |
| 5 | [05-ab-matrix.md](./05-ab-matrix.md) |
| 6 | [06-stage1-campaign-architecture.md](./06-stage1-campaign-architecture.md) |
| 7 | [PHASED-ACTIVATION.md](./PHASED-ACTIVATION.md) · [07-phased-activation-recommendation.md](./07-phased-activation-recommendation.md) |
| 8 | [google-ads-editor-import.csv](./google-ads-editor-import.csv) |
| 9 | [09-ads-human-review-matrix.md](./09-ads-human-review-matrix.md) |
| 10 | [10-tracking-event-spec.md](./10-tracking-event-spec.md) |
| 11 | [11-qa-report.md](./11-qa-report.md) |
| 12 | [12-blocker-decision-list.md](./12-blocker-decision-list.md) |

Rebuild CSV: `python3 ads-launch/build_stage1_editor_package.py`  
X-ray Ads package page only: `python3 ads-launch/build_xray_ads_overview.py` → `xray/ads-package.html`  
Re-audit history: `python3 ads-launch/analyze_historical_performance.py`
