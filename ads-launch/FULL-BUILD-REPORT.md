# Stage 1 Google Ads + LP — FULL BUILD REPORT (v6)

**For:** ChatGPT audit + George review  
**Generated:** 2026-08-05  
**Package:** `ads-launch/google-ads-editor-import.csv`  
**Builder:** `ads-launch/build_stage1_editor_package.py`  
**LP version:** `lp_version=stage1-v6`  
**Accounts:** USA `496-715-1855` · Australia `573-539-1940`  
**All Ads entities in CSV:** **Paused**  
**Live LP host:** `https://vision-three-alpha.vercel.app`  
**Casting commit on prod:** `8705ff05a92ffd89225294c02eb514f5ec1b445c`

---

## Paste for audit

1. **Primary (short, pasteable):** → **`ads-launch/CHATGPT-DEBRIEF.md`**
2. **Deep dive:** → **`ads-launch/CHATGPT-MEGA-AUDIT.md`**

This file is the short index only.

---

## Executive verdict

Stage 1 stack is **category-routed LPs + 2-campaign Search package per market** (Core + Roles; Brand deferred), evidence-backed from ~2y Editor exports, with honest events. Casting approved. **Not launch-ready** while real lead inbox/webhook, custom domain, GTM Ads mapping, Zoho/CallRail, and **explicit enable approval** remain open. Campaigns stay **Paused**. QA lead delivery is TEMPORARY log-only.

---

## Architecture (locked)

| Campaign | Share | Purpose |
|----------|------:|---------|
| `VC_{US\|AU}_S_CORE` | ~60% | High-intent VA / hire / PH-offshore |
| `VC_{US\|AU}_S_ROLES` | ~40% | Digital · Social · Admin · Controlled (accounting, books, CS, HR, recruitment, sales) |

Brand **not** in launch package.

---

## What changed vs v5

| Gap / prior | v6 fix |
|-------------|--------|
| 22 campaigns (Brand + Core + 9 roles) | **4 campaigns** (2 × 2 markets) |
| Brand in package | Brand **deferred** |
| Budgets Brand/Core/Role split | Core **$75** / Roles **$50** (US); AU A$75 / A$50 |
| `lp_version=stage1-v5` | `stage1-v6` |
| Generic VA keywords under Admin role campaign | Moved into **CORE** (Hire_VA + Offshore) |
| v5 category URLs / employer CTAs / single UTM | **Kept** |

### Earlier fixes retained (v1–v4 → v5)

Double UTM · inert `?role=` · template RSA spam · fake AU phone · consult language · casting · log-only honesty — see DEBRIEF / MEGA.

---

## Deliverables index

| # | File |
|---|------|
| **DEBRIEF** | **`CHATGPT-DEBRIEF.md`** ← paste into ChatGPT first |
| **MEGA** | **`CHATGPT-MEGA-AUDIT.md`** |
| 0 | `DECISIONS.md` · `LAUNCH-SHEET.md` |
| 1–12 | Audit docs `01`–`12` |
| 8 | `google-ads-editor-import.csv` |

---

## Inventory (v6)

| Entity | Count |
|--------|------:|
| Campaigns | 4 |
| Ad groups | 40 |
| Positive keywords | 1568 (Exact 1182 · Phrase 386) |
| RSAs | 78 |
| Campaign negative rows | 764 (191 unique × 4) |
| CSV rows | 2498 |

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

*End of v6 short report — Ads not enabled.*
