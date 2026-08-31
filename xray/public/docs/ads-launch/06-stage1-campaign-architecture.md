# 06 — Stage 1 campaign architecture (v7)

**Accounts:** USA `496-715-1855` · AU `573-539-1940`  
**Package:** `ads-launch/google-ads-editor-import.csv` (v7) · builder `build_stage1_editor_package.py`  
**All entities:** **Paused**  
**Match types:** Exact + Phrase positives only · **no** Broad / PMax / DSA / competitor farm  
**Brand:** **Deferred** — not in this package

---

## Shape (per market) — 2 campaigns

```
VC_{MKT}_S_CORE          (~60% budget)
  ├─ Hire_VA_PH          → /{mkt}   (market employer home)
  └─ Offshore_VA_PH      → /{mkt}   (market employer home)

VC_{MKT}_S_ROLES         (~40% budget)
  ├─ Digital             Digital_Marketing_Hire_PH · Outsource_PH → /digital-marketing
  ├─ Social              Social_Media_Hire_PH · Outsource_PH → /social-media
  ├─ Admin               Administration_EA_PH · Admin_City_Test → /administrative-support
  └─ Controlled          Accounting · Bookkeeping · CS · HR · Recruitment · Sales
                         (Hire + Outsource AGs each → matching category Final URL)
```

**Enable order ≠ AG structure labels.** “Controlled” is package taxonomy only. Activation priority is **PH/Filipino/offshore long-tail first** (see `PHASED-ACTIVATION.md`) — bookkeeping/accounting with PH long-tail can enable in Phase 1; bare Core heads later.

**Why 2/account:** Budget control and ST density — Core captures the historically dense VA/hire/PH-offshore cluster; Roles isolates role intent without 9 separate campaign budgets. Brand deferred until microsite brand conversion is proven.

---

## Settings (all campaigns)

| Field | Spec |
|-------|------|
| Type | Search |
| Status | **Paused** |
| Networks | Google Search only (partners/Display OFF in comment — confirm in Editor) |
| Geo | US or AU · Presence |
| Language | English |
| Bid | Maximize Clicks · Max CPC US `$8` / AU `A$6` |
| Budget | US Core `$75` / Roles `$50` · AU Core `A$75` / Roles `A$50` |
| Tracking template | `{lpurl}` only |
| Final URL suffix | UTMs + `lp_version=stage1-v7` (**once**) |

**Monthly implication (placeholders):** US ≈ $125/day ≈ **$3.8k/mo**; AU ≈ A$125/day ≈ **A$3.8k/mo**. Fits inside a **$10–20k/account** monthly budget story with headroom to raise dailies after inquiry quality is trusted.

---

## Final URLs

| Layer | Final URL |
|-------|-----------|
| Core | `…/{us\|au}` (generic employer home — not admin category) |
| Roles Digital/Social/Admin/Controlled | `…/{us\|au}/{category-slug}` |

Sitelinks → same host microsite only (no WordPress). No Brand generics in this CSV.

---

## Negatives

- **191** unique Broad negatives per campaign  
- Repeated on every campaign because Editor import requires campaign-level rows  
- Job seeker · WFH fluff · DIY how-tos (not bare `how to`) · reviews/pricing · DSA/marketplace catch-alls · platforms · Spanish/LATAM · medical/tech  
- **Not** bare `hire` / `hiring`

---

## Inventory (v6 machine)

| Entity | Count |
|--------|------:|
| Campaigns | 4 |
| Ad groups | 40 |
| Positive keywords | 1,568 |
| RSAs | 78 |
| Campaign negative rows | 764 (191 × 4) |
| Callouts | 24 |
| Structured snippets | 4 |
| Sitelinks | 16 |
| **CSV rows** | **2,498** |
