# Stage 1 Google Ads + LP — FULL BUILD REPORT (v7 · Core→market home)

**For:** ChatGPT audit + George review  
**Generated:** 2026-08-05  
**Package:** `ads-launch/google-ads-editor-import.csv`  
**Builder:** `ads-launch/build_stage1_editor_package.py`  
**LP version:** `lp_version=stage1-v7`  
**Accounts:** USA `496-715-1855` · Australia `573-539-1940`  
**All Ads entities in CSV:** **Paused**  
**Live LP host:** `https://vision-three-alpha.vercel.app`  
**Launch Control:** `https://vc-xray.vercel.app/launch-control`  
**Casting commit on prod:** `8705ff05a92ffd89225294c02eb514f5ec1b445c`  
**Paid status:** **NOT READY FOR PAID TRAFFIC** (no durable lead delivery)

---

## Paste for audit

1. **Primary (complete package — paste this):** → **`ads-launch/CHATGPT-DEBRIEF.md`**
2. **Deep companion:** → **`ads-launch/CHATGPT-MEGA-AUDIT.md`**

This file is the short index only.

---

## Executive verdict

Stage 1 stack is **three microsites** (`/us` · `/au` · `/ph`) + **2-campaign Search package per market** (Core + Roles; Brand deferred), **3 unique full RSAs per main AG**. **Core Final URLs = market home** (`/us`/`/au`); Roles = category slugs. Honest conversion contract: durable delivery only. WP-link audit in CI. **NOT READY FOR PAID TRAFFIC** until real lead inbox/webhook, domains, GTM mapping, and **explicit enable approval**. Campaigns stay **Paused**. Log-only = blocked mode (`conversion_eligible: false`).

---

## Architecture (locked)

| Campaign | Share | Purpose | Final URL |
|----------|------:|---------|-----------|
| `VC_{US\|AU}_S_CORE` | ~60% | High-intent VA / hire / PH-offshore | `/{us\|au}` |
| `VC_{US\|AU}_S_ROLES` | ~40% | Digital · Social · Admin · Controlled | `/{us\|au}/{slug}` |

Brand **not** in launch package. RSA: **3 per main AG** (city-test 1).

---

## What changed vs prior v6 (2 RSA)

| Gap | Fix |
|-----|-----|
| 2 RSAs/main AG | **3 unique full RSAs (15H/4D)** — hire / role or PH-offshore / proof-speed |
| City-test | Stays **1 RSA** |
| Package RSA count | 78 → **116** |
| CSV rows | 2498 → **2536** |

### Retained from v6 architecture / earlier

2 campaigns/account · Brand deferred · Core $75 / Roles $50 · category URLs · employer CTAs · single UTM · casting · log-only honesty.

---

## Deliverables index

| # | File |
|---|------|
| **DEBRIEF** | **`CHATGPT-DEBRIEF.md`** ← paste into ChatGPT (whole package) |
| **MEGA** | **`CHATGPT-MEGA-AUDIT.md`** |
| 0 | `DECISIONS.md` · `LAUNCH-SHEET.md` · **`PHASED-ACTIVATION.md`** (enable order: PH long-tail first) |
| 1–12 | Audit docs `01`–`12` |
| 8 | `google-ads-editor-import.csv` |

---

## Inventory (v6 · RSA×3)

| Entity | Count |
|--------|------:|
| Campaigns | 4 |
| Ad groups | 40 |
| Positive keywords | 1568 (Exact 1182 · Phrase 386) |
| RSAs | **116** (38×3 main + 2×1 city) |
| Campaign negative rows | 764 (191 unique × 4) |
| CSV rows | **2536** |

Budgets/CPC: US Core $75 / Roles $50 · AU Core A$75 / Roles A$50 · Max CPC US $8 / AU A$6.  
Monthly at placeholders ≈ **$3.8k US + A$3.8k AU** (inside $10–20k/account story).

---

## Historical snapshot

| | USA | AU |
|--|----:|---:|
| Cost | $723,838.59 | $457,489.46 |
| Clicks | 87,060 | 49,457 |
| Conversions | 2,597.32 | 1,412.66 |
| All conv | 4,629.39 | 3,505.46 |
| ST raw → deduped | 66,869 → 66,465 | 26,211 → 26,132 |

**Conversions ≠ All conv ≠ job orders.**

---

## Operator next

1. Paste `CHATGPT-DEBRIEF.md` into ChatGPT.  
2. Replace log-only with real delivery; optional custom domain.  
3. Import CSV **Paused**.  
4. Enable only per `07-phased-activation-recommendation.md` after explicit approval.

*End of v6 · RSA×3 short report — Ads not enabled.*
