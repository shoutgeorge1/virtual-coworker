# 01 — Current-state audit (pre/post Stage 1 v5)

**Date:** 2026-08-05 · **Branch:** `vision-demo` · **Scope:** local only  
**No Ads API · No live enable · No WordPress edits · No commit/push/deploy**

---

## Verdict

Before this pass, the microsite was a **generic `/us` + `/au` hire LP** with employer gate + lead API, but **no category routes**, **inert `?role=`**, **no A/B**, **consult language**, **double UTMs in the Editor CSV**, and **Final URLs that did not match a category experience**. Historical Editor performance CSVs were already present and previously mined into v4 keywords — those evidence keywords are retained; architecture + LP + tracking honesty are what this pass fixes.

**Not launch-ready.** Blockers remain (delivery recipients, AU phone, Zoho, budgets/CPC, CallRail, careers URL, proof).

---

## Git / workspace (inspect)

| Item | Finding |
|------|---------|
| Branch | `vision-demo` (clean at start except `__pycache__`) |
| Unrelated dirty work | None staged/unstaged at start — preserved |
| Prior Ads package | v4 role-first Search, brand deferred, `?role=` Final URLs |
| Performance exports | Present under `audit-data/performance/` (UTF-16) |

---

## Suspected problems — verified

| Suspicion | Evidence | Status after v5 |
|-----------|----------|-----------------|
| Generic Final URLs | CSV pointed at `/us?role=…` | **Fixed** → `/us\|au/{category}` |
| `?role=` inert | LeadGate ignored query; no redirect | **Fixed** → middleware 308 → category route + form preselect |
| Single hero / no A/B | One hero image per market page | **Fixed** → variants A/B headlines/heroes/CTAs |
| Double UTMs | Tracking template `{lpurl}?utm…` **and** Final URL suffix `utm…` | **Fixed** → template `{lpurl}` only; suffix carries UTMs |
| Inflated / dangerous negatives | Bare `how to` previously blocked converting hire query (already fixed in v4) | **Retained** careful list; bare `hire`/`hiring` still not negatived |
| Consultation / SaaS language | “Request a hiring consult”, “Book a Hiring Consult”, `/consult` pages | **Fixed** → employer CTAs; `/consult` redirects to `#gate` |
| AU fake phone | `[AU_BUSINESS_PHONE]` placeholder shown | **Fixed** → no phone UI when unset; form primary |
| Lead success without delivery | API accepted log-only by default | **Fixed** → 503 unless channel configured or `ALLOW_LOG_ONLY_LEADS=true` |
| Event naming honesty | `employer_form_valid_submit` / `phone_click` | **Fixed** → `employer_inquiry_submitted` / `phone_cta_clicked` |

---

## What was useful and retained

- Employer vs job-seeker gate pattern
- Honeypot + min completion time + dedupe primary fire
- v4 search-term-derived Exact/Phrase keywords + curated negatives
- Market CSS / brand assets / Clutch·Google·Forbes badge treatment (badges as badges, not invented testimonials)
- Thank-you route pattern
- Launch Control / xray mirror path for Editor CSV

---

## Structure after this pass

```
vision/
  /us · /au                          generic market LPs + A/B
  /us/{category} · /au/{category}    9 categories each
  middleware role→category redirect
  data-driven categories + variants
ads-launch/
  google-ads-editor-import.csv       v5 Paused package
  build_stage1_editor_package.py
  analyze_historical_performance.py
  01–12 deliverables
```
