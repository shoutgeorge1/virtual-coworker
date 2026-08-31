# USA assets 310 sweep — 2026-08-10

Account `496-715-1855` only. AU untouched. Brand campaigns not re-enabled.
George: no Ads UI. Live public number **(310) 730-9126** / `3107309126`.

Toolkit: `~/Developer/shoutgeorge-ads/scripts/sweep_vc_us_assets_310.py` (`.venv` + gitignored `.env`).

Tonight’s earlier pass already paused 954 on VC_* and re-enabled 310 on VC_* (`CALL-ASSET-310-US-2026-08-10.md`). This run swept leftovers only — no CALL no-ops.

## 1. Call state

### Numbers

| Asset ID | Phone | Class |
|----------|-------|-------|
| `404927491581` | `(310) 730-9126` | **use this** |
| `405704361176` | `888-954-8644` | 888 — already PAUSED on VC_* |
| `49435983302` | `(888) 964-8644` | 888 — already PAUSED (campaign / AG / account) |
| `49435983308` | `(888) 964 8644` | 888 — already PAUSED (museum campaign) |

### Found (Searches 1–3)

| Level | Rows | ENABLED 888 | 310 |
|-------|-----:|:-----------:|-----|
| Campaign Call | 20 | **none** | VC_US_S_CORE + ROLES **ENABLED** |
| Ad group Call | 21 (all VC_*) | **none** (all 964 PAUSED) | none at AG |
| Account Call | 2 | **none** (`49435983302` PAUSED) | `404927491581` **ENABLED** |

No 954 at AG or account (never created there). No Brand / PM_* Call association. Two museum Search campaigns are still **ENABLED** as campaigns (`Search (Exact) Specific Jobs Trial 982`, `US | Search Campaign TCPA vs. MClicks`) — their 888 Call links are **PAUSED**; they fall back to account 310. Did **not** re-enable Brand. Did **not** change campaign status.

### Changed (CALL)

**None.** No leftover ENABLED 888 to pause. VC_* 310 already ENABLED. Account 310 already ENABLED (leftover museum won’t fall back to 888).

### Verify (Search 4 — ENABLED campaign Call only)

| Campaign | Camp status | Phone | Asset | Link |
|----------|-------------|-------|-------|------|
| `VC_US_S_CORE` | ENABLED | (310) 730-9126 | `404927491581` | **ENABLED** |
| `VC_US_S_ROLES` | ENABLED | (310) 730-9126 | `404927491581` | **ENABLED** |

**ENABLED 888 Call anywhere in USA:** none at campaign (verify), none at AG/account (probe). Digit check on live VC_* Call: **`3107309126`**.

888 assets stay in the library as **PAUSED** — not deleted. Ads UI will still list them.

## 2. Other assets (VC_US_* only)

### Sitelinks — found vs changed

Probe: **20** ENABLED sitelinks on `VC_US_S_CORE` + `VC_US_S_ROLES`. All `.app` — **no WordPress / `virtualcoworker.com`**.

**Paused (8)** — wrong How Hiring Works → `/us`, homepage clutter, same-text dupes competing with good microsite links:

| Campaign | Text | Paused URL | Why | Asset |
|----------|------|------------|-----|-------|
| `VC_US_S_CORE` | How Hiring Works | `/us` | wrong dest (not `/how-it-works`) | `404542902091` |
| `VC_US_S_CORE` | US Employer Home | `/us` | homepage clutter vs hub | `404542906159` |
| `VC_US_S_CORE` | Admin Support Hire | `/us/administrative-support` | dupe; kept named `405863416209` | `404542900345` |
| `VC_US_S_CORE` | Tell Us Who You Need | `/us` | dupe; kept `#gate` `404542906141` | `405863498721` |
| `VC_US_S_ROLES` | Tell Us Who You Need | `/us` | dupe; kept `#gate` `404542906141` | `405863498721` |
| `VC_US_S_ROLES` | Digital Marketing Hire | `/us/digital-marketing` | dupe; kept named `405863389170` | `404542906162` |
| `VC_US_S_ROLES` | Bookkeeping Hire | `/us/bookkeeping` | dupe; kept named `405863498733` | `404542906168` |
| `VC_US_S_ROLES` | Social Media Hire | `/us/social-media` | dupe; kept named `405791046253` | `404612776461` |

**Kept ENABLED (12 — 6 per campaign, all `www.virtualcoworker.app`):**

| Campaign | Text | URL | Asset |
|----------|------|-----|-------|
| CORE + ROLES | Tell Us Who You Need | `/us#gate` | `404542906141` |
| CORE + ROLES | How Hiring Works | `/how-it-works?market=us` | `405863498724` |
| CORE + ROLES | Take the VA Quiz | `/us/quiz` | `405863440833` |
| CORE + ROLES | Bookkeeping Hire | `/us/bookkeeping` | `405863498733` |
| CORE | Hire by Role | `/services?market=us` | `405791110294` |
| CORE | Admin Support Hire | `/us/administrative-support` | `405863416209` |
| ROLES | Digital Marketing Hire | `/us/digital-marketing` | `405863389170` |
| ROLES | Social Media Hire | `/us/social-media` | `405791046253` |

Did **not** pause Brand / PM_* / museum sitelinks. Did **not** touch AU.

### Callouts + structured snippet

Already correct on CORE + ROLES (from `_us_asset_review_2026-08-10.json`): all 6 Stage 1 callouts (Vetted Filipino Talent, Employer Hiring Only, Interview Your Shortlist, Recruit Vet & Manage, Not a Gig Marketplace, Dedicated Remote Staff) + Types snippet. **Not added.**

Did **not** add price, promotion, lead form, app, or logo. Did **not** upload images.

## 3. API ops

| Op | Service | Items | Result |
|----|---------|------:|--------|
| Search 1 | `GoogleAdsService.Search` campaign_asset CALL+SITELINK | 1 | inventory |
| Search 2 | `GoogleAdsService.Search` ad_group_asset CALL | 1 | inventory |
| Search 3 | `GoogleAdsService.Search` customer_asset CALL | 1 | inventory |
| Mutate sitelink pause | `CampaignAssetService.mutate` | 8 | PAUSED VC_* junk/dupes |
| Search 4 | `GoogleAdsService.Search` ENABLED campaign CALL | 1 | verify |

**Total: 5 API calls** (4 Search ≤ cap, 1 mutate). No CALL mutates. No `RESOURCE_EXHAUSTED`. AU not queried. No Brand re-enable. No campaign status changes.

Dump (toolkit, not this repo): `shoutgeorge-ads/output/vc-us-assets-310-sweep.json`.

No commit. No email.
