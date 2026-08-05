# Stage 1 Google Ads launch sheet (paused import)

**Status:** Import-ready structure · all entities **Paused** · no live mutations performed.  
**Accounts:** USA `496-715-1855` · AU `573-539-1940` (MCC Accept done — verify Admin in-account).  
**Import file:** `google-ads-editor-import.csv`

---

## Factual note (Editor export — structure only)

| Market | Enabled remnant campaign | **Enabled ad Final URL** | try.* ad |
|--------|--------------------------|--------------------------|----------|
| USA | `PM_US_RSA_Brand` | `https://virtualcoworker.com/` (WP) | `try…/us` exists but **Paused** (Approved) |
| AU | `PM_AU_RSA_Brand` | `https://virtualcoworker.com.au/` (WP) | `try…/apac` **Paused + Disapproved**; separate Custom LP campaign **Paused** (try ad Approved) |

**Unknown until Admin UI:** whether remnant campaigns are spending. Do not infer delivery from Editor structure alone.

---

## Campaigns in this package (per market)

| Campaign | Purpose | Launch |
|----------|---------|--------|
| `VC_{US\|AU}_S_BRAND` | Brand protect | Yes (paused until checklist) |
| `VC_{US\|AU}_S_CORE_hire_va` | High-intent employer hire | Yes (paused until checklist) |
| `VC_{US\|AU}_S_ROLE_held_for_evidence` | Role themes | **Held** — comment only; no keywords/ads |

Settings (confirm in Editor after import):

- Search only · Search partners **OFF** · Display expansion **OFF**
- Presence geo (US / AU) · English
- Bid: Maximize Clicks · Max CPC = `[APPROVAL_MAX_CPC]`
- Daily budget = `[APPROVAL_DAILY_BUDGET_USD|AUD]`
- Final URL: provisional `https://vision-three-alpha.vercel.app/{us|au}` until custom paid host approved
- Final URL suffix: UTMs + `lp_version=stage1-v1`
- One RSA / one ad group · Exact (+ limited Phrase on CORE hire terms)
- Sitelinks: **none to WP** in this package — add LP-section sitelinks only after LP anchors confirmed
- Conversion goals: Stage 1 observe `employer_form_valid_submit` only after server accept — **do not** optimize bidding to contaminated legacy conversions

Negatives: curated jobseeker/info set in CSV — **not** a wholesale historical import.

---

## Import steps (Editor)

1. Confirm USA + AU visible under MCC; verify Admin inside each account.
2. Download USA + AU into clean Editor (ShoutGeorge login).
3. **Recommendation:** pause legacy `PM_*` / museum Search before enabling v1 (George decision).
4. Import `google-ads-editor-import.csv` into each account (split by `VC_US_*` / `VC_AU_*` or import then delete other market’s rows).
5. Replace `[APPROVAL_*]` budget/CPC placeholders.
6. Confirm Final URL host (vision deploy vs custom domain).
7. Confirm networks/geo/presence.
8. Post **Paused** → review in UI → enable only after launch-control checklist green.

---

## Campaign-specific conversion goal note

| Path | Ads treatment Stage 1 |
|------|------------------------|
| `employer_form_valid_submit` (after server accept) | Observe / primary-eligible form path — wire in GTM later; **no hard-coded AW labels in repo** |
| `phone_click` | Diagnostic / secondary |
| Gate / job-seeker / spam rejects | Diagnostic only — never primary |
| Zoho / CallRail / offline | Optional later — **do not block** Stage 1 |

---

## Experiments (docs note only)

Quiz + modal gate variants are **not** implemented. Baseline = inline gate on LP. Revisit after Stage 1 diagnostics.
