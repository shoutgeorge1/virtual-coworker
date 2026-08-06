# Stage 1 Google Ads launch sheet (paused import)

**Status:** Import-ready · all entities **Paused** · no live mutations.  
**Package version:** stage1-v3 (remediated)  
**Accounts:** USA `496-715-1855` · AU `573-539-1940`.  
**Import file:** `ads-launch/google-ads-editor-import.csv`  
**Full audit report:** `ads-launch/FULL-BUILD-REPORT.md`  
**Rebuild script:** `ads-launch/build_stage1_editor_package.py`

---

## Strategy (locked for this package)

| Decision | Spec |
|----------|------|
| Brand | **Deferred** — not in this CSV |
| Intent | Long-tail employer hire / outsource / Filipino / Philippines / VA / offshore |
| Roles only | Digital marketing · Social media · Accounting · Bookkeeping · Administration · Customer service · HR · Recruitment · Sales |
| Themes | Each role: **Hire_PH** + **Outsource_PH** (Admin: Hire + EA + city test) |
| Excludes | Medical staffing · Technology staffing · Spanish-language |
| Match | Exact + Phrase only · **no** Broad / PMax / DSA / Demand Gen |
| Bid | Maximize Clicks · Max CPC = `[APPROVAL_MAX_CPC]` |
| Networks | Google Search · partners OFF · Display expansion OFF (confirm in Editor) |
| Destinations | `https://vision-three-alpha.vercel.app/{us\|au}?role=…` — **not** WordPress |
| Creatives | Full RSA fill (15H / 4D) · role-unique angles · DKI on Hire/EA B · no invented pricing |

---

## Campaigns in this package

### United States — 9 role campaigns (all Paused)

- `VC_US_S_ROLE_digital_marketing` — Hire_PH + Outsource_PH
- `VC_US_S_ROLE_social_media`
- `VC_US_S_ROLE_accounting`
- `VC_US_S_ROLE_bookkeeping`
- `VC_US_S_ROLE_administration` ← Hire_PH (general VA) + EA_PH + Admin_City_Test
- `VC_US_S_ROLE_customer_service`
- `VC_US_S_ROLE_hr`
- `VC_US_S_ROLE_recruitment`
- `VC_US_S_ROLE_sales`

### Australia — parallel 9 (all Paused)

Same campaign names with `VC_AU_*`. AU creatives use Australian / SMEs / organisation / specialise where natural — not a US clone with country swap.

**Not included:** `VC_*_S_BRAND` · old CORE-only shell · empty ROLE held stubs.

---

## Placeholders you must fill before enable

| Field | Placeholder |
|-------|-------------|
| US daily budget (each campaign) | `[APPROVAL_DAILY_BUDGET_USD]` |
| AU daily budget (each campaign) | `[APPROVAL_DAILY_BUDGET_AUD]` |
| Max CPC ceiling | `[APPROVAL_MAX_CPC]` |
| Final URL host | vision-three-alpha until custom domain on Vercel |

---

## Import steps (Editor)

1. Download fresh USA + AU into Editor (ShoutGeorge).  
2. Optional but recommended: pause live legacy `PM_US_RSA_Brand` / `PM_AU_RSA_Brand` in Ads UI (you click).  
3. Import `google-ads-editor-import.csv` (filter to `VC_US_*` or `VC_AU_*` per account).  
4. Replace `[APPROVAL_*]` budget/CPC values.  
5. Confirm Search partners off · Display expansion off · Presence geo · English.  
6. Confirm Final URLs = microsite (no WP sitelinks).  
7. Post **Paused** → spot-check in UI.  
8. Enable only after Launch Control gates are green — start US roles, keep AU quiet until US looks sane.

---

## Conversion note (Stage 1)

| Path | Treatment |
|------|-----------|
| `employer_form_valid_submit` (after server accept) | Observe / primary-eligible later — **do not** bid on contaminated legacy conversions |
| `phone_click` | Diagnostic / secondary |
| Job-seeker / spam rejects | Never primary |
| Zoho / CallRail | Optional — do not block Stage 1 |

---

## Counts (package v3)

1186 positive keywords (Exact+Phrase) · 74 RSAs · 18 campaigns · 38 ad groups · 113 unique curated negatives per campaign · callouts + structured snippets + microsite sitelinks · `lp_version=stage1-v3`.
