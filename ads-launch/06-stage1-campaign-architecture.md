# 06 — Stage 1 campaign architecture

**Accounts:** USA `496-715-1855` · AU `573-539-1940`  
**Package:** `ads-launch/google-ads-editor-import.csv` (v5) · builder `build_stage1_editor_package.py`  
**All entities:** **Paused**  
**Match types:** Exact + Phrase positives only · **no** Broad / PMax / DSA / competitor farm

---

## Shape (per market)

```
VC_{MKT}_S_BRAND
  ├─ Brand
  └─ Brand_Nav
VC_{MKT}_S_CORE_hire_va
  ├─ Hire_VA_PH
  └─ Offshore_VA_PH
VC_{MKT}_S_ROLE_digital_marketing
  ├─ Digital_Marketing_Hire_PH
  └─ Digital_Marketing_Outsource_PH
VC_{MKT}_S_ROLE_social_media          (Hire + Outsource)
VC_{MKT}_S_ROLE_accounting
VC_{MKT}_S_ROLE_bookkeeping
VC_{MKT}_S_ROLE_administration        (+ EA + City test)
VC_{MKT}_S_ROLE_customer_service
VC_{MKT}_S_ROLE_hr                    ← controlled lower volume
VC_{MKT}_S_ROLE_recruitment           ← controlled lower volume
VC_{MKT}_S_ROLE_sales
```

---

## Settings (all campaigns)

| Field | Spec |
|-------|------|
| Type | Search |
| Status | **Paused** |
| Networks | Google Search only (partners/Display OFF in comment — confirm in Editor) |
| Geo | US or AU · Presence |
| Language | English |
| Bid | Maximize Clicks · Max CPC `[APPROVAL_MAX_CPC]` |
| Budget | `[APPROVAL_DAILY_BUDGET_USD]` / `[APPROVAL_DAILY_BUDGET_AUD]` |
| Tracking template | `{lpurl}` only |
| Final URL suffix | UTMs + `lp_version=stage1-v5` (**once**) |

---

## Final URLs

| Layer | Final URL |
|-------|-----------|
| Brand | `…/{us\|au}` |
| Core | `…/{us\|au}/administrative-support` |
| Role | `…/{us\|au}/{category-slug}` |

Sitelinks → same host microsite only (no WordPress).

---

## Negatives

- **191** unique Broad negatives per campaign  
- Repeated on every campaign because Editor import requires campaign-level rows  
- Job seeker · WFH fluff · DIY how-tos (not bare `how to`) · reviews/pricing · DSA/marketplace catch-alls · platforms · Spanish/LATAM · medical/tech  
- **Not** bare `hire` / `hiring`

---

## Inventory (v5 machine)

| Entity | Count |
|--------|------:|
| Campaigns | 22 |
| Ad groups | 46 |
| Positive keywords | 1,604 |
| RSAs | 82 |
| Campaign negative rows | 4,202 (191 × 22) |
| Callouts | 132 |
| Structured snippets | 22 |
| Sitelinks | 88 |
| **CSV rows** | **6,198** |
