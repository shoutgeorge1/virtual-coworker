# Virtual Coworker Search — Operator Debrief (2026-08-09)

**Purpose:** Self-contained brief for ChatGPT conversation today. George is on a break — intelligent strategy talk only, not execution work. Most live truth lives on the dashboards; this file is so ChatGPT can talk smart without browsing.

**Snapshot source:** `xray/data/executive-snapshot.json` · generated **2026-08-09T11:28 UTC** (LAST_7_DAYS window; focus day **2026-08-08** — UTC “today” not in rows yet). Search-term export **skipped by design** (API call budget used for US+AU campaign metrics only).

**Repo:** `/Users/george/Developer/virtual-coworker`

---

## 1. What this is

- **Product:** Virtual Coworker — employer-side staffing for Philippines / Filipino remote workers (dedicated seat model, not a marketplace gig board).
- **Pilot:** Google Search, US + AU, clean `VC_*` campaign system built as a parallel Stage 1 package (Editor CSV → Import → Post → Enable).
- **Live bidding mode:** **Maximize Clicks** (seasoning / learning). Not Max Conversions yet.
- **Intent north star (2026-08-09):** employers shopping for a **Philippines VA / staffing agency · firm · company · outsourcing** provider — not job seekers, and not ambiguous “hire/recruit” head terms alone.
- **Brand:** deferred / paused. SEO owns brand for now. Do not re-litigate Brand as Stage 1 priority.

---

## 2. Accounts & URLs

| Item | Value |
|------|-------|
| MCC | `119-318-9031` (Shout George) |
| USA child | `496-715-1855` |
| AU child | `573-539-1940` |
| Live site | https://www.virtualcoworker.app |
| US hub | https://www.virtualcoworker.app/us |
| AU hub | https://www.virtualcoworker.app/au |
| Careers / job-seeker exit | `/ph` |
| Operator dashboards | https://vc-xray.vercel.app |
| Executive | https://vc-xray.vercel.app/executive |
| Checklist / Launch Control | https://vc-xray.vercel.app/launch-control |
| Keyword strategy | https://vc-xray.vercel.app/keyword-strategy |
| Site tests (scoreboard blank) | https://vc-xray.vercel.app/experiments |
| Corporate WP (untouched) | virtualcoworker.com · virtualcoworker.com.au |
| US phone (site + Call asset primary) | **888-954-8644** |
| AU phone (site live) | **1300 886 740** |
| 310 number | Still in US account; may show for some LA traffic — not the microsite primary |

---

## 3. Live campaign reality

### US (`VC_US_*`) — live Max Clicks

| Campaign | Status (as of snapshot) | Role |
|----------|-------------------------|------|
| `VC_US_S_CORE` | **ENABLED** | Volume engine → Final URL `/us` |
| `VC_US_S_ROLES` | **ENABLED** | Role LPs → `/us/{category}` |
| Brand | **Paused / deferred** | Do not re-enable; expensive (~$1k/lead order of magnitude historically); SEO owns brand |

### AU Stage 1 (`VC_AU_*`)

- Stage 1 package exists (`VC_AU_S_CORE` + `VC_AU_S_ROLES`).
- **Last 7 days Stage 1 spend: ~$0** (snapshot `totals_stage1_last_7_days`).
- Checklist notes AU stood up (phone live; campaigns waiting on traffic) — **do not confuse “stood up” with “driving the AU bill.”**

### AU legacy (`PM_AU_*`) — what actually spent

Snapshot LAST_7_DAYS AU totals ≈ **$1,150 · 127 clicks · 1,009 impressions** — **almost entirely legacy `PM_AU_*`**, now showing **PAUSED** in the pull (Paused mid-window still appears in LAST_7_DAYS).

| Campaign (legacy) | Cohort | 7d cost (USD in pull) | 7d clicks |
|-------------------|--------|----------------------:|----------:|
| `PM_AU_RSA_Generic_Pain-Point Intent_Custom LP` | legacy | ~$478 | 97 |
| `PM_AU_DSA_Generic_Catch-all_Custom LP` | legacy | ~$415 | 2 (! CPC ~$208) |
| `PM_AU_RSA_Brand` | legacy_brand | ~$241 | 17 |
| `PM_AU_RSA_Competitors_Custom LP` | legacy | ~$15 | 9 |
| Other small legacy / brand LP | — | small | small |

**Honesty:** If someone says “AU is spending,” ask **which campaigns**. Recent spend was museum `PM_AU_*`, not Stage 1 `VC_AU_*`.

---

## 4. Budgets / bidding / match types

| Market | Daily budgets (package / live target) | Bid strategy | Max CPC caps (package) |
|--------|----------------------------------------|--------------|------------------------|
| US | CORE **$75** + ROLES **$50** ≈ **~$125/day** | Maximize Clicks | CORE **$12** · ROLES **$10** |
| AU Stage 1 | CORE **A$75** + ROLES **A$50** | Maximize Clicks | **A$6** both |

- **Positives:** Exact + Phrase only. **Zero Broad positives** by design.
- **Live USA practice:** Exact-only bidding emphasis; Phrase often held Paused (`PHRASE_HOLD` / Exact-only ops note). Package still contains Phrase rows for later.
- **Negatives:** Campaign-level curated Broad (+ US job-seeker Phrase cohort). **Never** attach account shared / `PM_*` mega negative dumps to `VC_*`.
- **Networks:** Google Search. No PMax / DSA / Broad+ for Stage 1.
- **Monthly pace story:** ~$3.8k US + A$3.8k AU at those dailies — inside a larger $10–20k/account budget narrative (room to scale). George-decidable.

---

## 5. Performance snapshot (LAST_7_DAYS)

**Pulled:** 2026-08-09 · API calls used: 1 of max 2 (AU-only refresh; US kept from prior pull). **Phone wins not scored as KPIs in this snapshot yet.**

### US Stage 1 (`VC_US_*`)

| Window | Impr | Clicks | CTR | Cost | Avg CPC |
|--------|-----:|-------:|----:|-----:|--------:|
| Last 7 days | 874 | 116 | 13.27% | **$297.64** | $2.57 |
| Focus day 2026-08-08 | 134 | 14 | 10.45% | $42.30 | $3.02 |

| Campaign | 7d impr | 7d clicks | 7d CTR | 7d cost | 7d CPC |
|----------|--------:|----------:|-------:|--------:|-------:|
| `VC_US_S_CORE` | 473 | 78 | 16.49% | $165.19 | $2.12 |
| `VC_US_S_ROLES` | 401 | 38 | 9.48% | $132.46 | $3.49 |

**Read:** CORE = volume + cheaper clicks. ROLES = more expensive CPC — useful for role LP tests, not the main dial yet. Dates in US pull: 2026-08-06 … 08 (short window in this export).

### AU account (legacy-dominated)

| Cohort | Impr | Clicks | CTR | Cost | Avg CPC |
|--------|-----:|-------:|----:|-----:|--------:|
| AU account LAST_7_DAYS (all rows in pull) | 1009 | 127 | 12.59% | **~$1,150** | ~$9.06 |
| Stage 1 `VC_AU_*` | 0 | 0 | — | **$0** | — |
| Legacy `PM_AU_*` | 1009 | 127 | 12.59% | **~$1,150** | ~$9.06 |

---

## 6. Keyword strategy truth

### What George wants (spine)

Highest intent = **agency / firm / company / outsourcing** language for PH VA / remote staffing:

- `philippines virtual assistant agency`
- `philippines outsourcing agency`
- `remote staffing agency` / `agencies`
- `virtual assistant firm` / `company`
- Supporting (messier): plain hire / Filipino VA — can mix employer + job-seeker

Role themes (ROLES): bookkeeping, accounting, CSR, admin/EA, digital marketing, social — Final URLs to category LPs.

### What’s in the Stage 1 package vs add-on

| Layer | Reality |
|-------|---------|
| Main Editor package | Large Exact+Phrase set (~1,568 positives historically; LAUNCH-SHEET now cites ~1,628 incl. agency-intent adds). Built around hire/role/PH history + curated negs. |
| Agency-intent add-on | `ads-launch/google-ads-editor-agency-intent-keywords-add.csv` — **Exact, Keyword Status=Paused**, Campaign/Ad Group Status blank (live-US-safe). Targets `Hire_VA_PH` + `Offshore_VA_PH` on `VC_*_S_CORE` for US + AU. ~76 keyword rows. |
| Ops plan George discussed | Agency-intent was **underweighted** live; he’s adding **Exact + Phrase**, including via a **duplicate ad group** pattern so Phrase can sit cleanly. Paste list exists for Editor work. **Do not invent that Phrase is already live Enabled** unless George confirms from Ads UI. |

### Match-type stance

1. Exact first  
2. Phrase after quality / when George enables  
3. Broad positives — never for this pilot  

Low volume on high-intent Exact is **acceptable**. Quality > volume.

---

## 7. Search terms / quality stance

- Executive surface = **curated buyer signals only** — no junk ST dump on the dashboard.
- Job-seeker / WFH junk: campaign Phrase cohort `VC_Neg_JobSeekers_Live` (US CORE + ROLES). Paste/list files under `ads-launch/` (e.g. sniper + job-seeker negatives).
- Sniper list `VC_US_S_🚫_Sniper` attached manually by George to US CORE + ROLES (competitors, botty Exact, etc.).
- **`va workers ph`:** watch / pause candidate — odd shorthand, not a clean win if spend climbs. History: flipped several times (mistaken job-seeker → Broad `workers` wrong; employer shorthand; then Exact killed after ~50% Washington bot signal). **Do not celebrate it.** Bare Broad negative `workers` was removed on purpose (would overblock employers).
- Daily hygiene: search terms, ad copy, budget pacing, keywords + negatives.
- This snapshot did **not** pull fresh search-term rows (API budget).

---

## 8. Landing pages & CRO state

| Page | Notes |
|------|-------|
| `/us` | CORE Final URL — carries most measurable US clicks/spend (~78 clicks / $165 in 7d attribution used on Executive) |
| Role LPs | Live: admin, bookkeeping, accounting, CSR, digital marketing, social, etc. ROLES ~38 clicks / 7d — **not split per URL** in this snapshot |
| `/au` | Live hub + 1300; Stage 1 not the spend driver |
| Employer vs job-seeker gate | On market hubs (“I’m hiring…” / “I’m looking for a job”) |
| Careers exit | `/ph` |
| LP A/B | Copy A vs B links work on the live site (different hero/copy). **Site tests scoreboard not wired** (GTM/GA4) — Checklist step 34 |
| Role imagery | AI portraits live on vision LPs; Ads image upload deferred (Search RSAs don’t need them yet) |
| Host | Production Final URLs = `www.virtualcoworker.app` only (not WP, not vision preview) |

Ad copy themes that ops believes are working (not an Ads asset-ranking export): Hire Filipino/PH VA · dedicated seat · interview shortlist · staffing partner for SMBs (not a job board).

---

## 9. Tracking / conversions / measurement gaps

**Guiding light until Zoho offline qualify:** phone. Stay on Max Clicks meantime. Forms useful but spam/bot risk — not the bidding driver.

### Priority order (measurement)

1. **Website calls 60+ seconds** (US + AU) — Google “calls to a phone number on the website” + forwarding number. **Not** a `tel:` tap. High priority.
2. **AU:** ad-call conversion wins + website tags (GTM/GA4 parity on `/au`).
3. **Then Zoho** “qualified” → Google Ads offline / import.
4. **Later:** Site tests scoreboard wiring.

### Known conversion / stack truths

| Item | Status |
|------|--------|
| US GTM/GA4 | Live containers exist (`GTM-M92DX9BJ` → `G-2V3V0BS6JW` cited in conversion plan) |
| AU website tags | Still a checklist open |
| `VC_US_Phone_Call_From_Ads` | Planned/created path in Ads UI docs — **don’t invent conversion IDs** |
| Website call duration (US+AU) | **High priority unfinished** |
| Form → thank-you | Secondary / observation; durable delivery Resend → us@ / apac@ (+ George CC); GitHub Issues backup |
| Calendly on thank-you | Wired (US Cheyenne / AU APAC) — **not** a second Primary for same inquiry |
| Zoho | Access yes; Recruit vs CRM discovery deferred; **no live write until path locked**; Zoho later for quality signal |
| CallRail | ~1–2 months — not Stage 1 required |
| Old Zoho/Zapier account conversions | Museum — **do not** wire onto `VC_*` as Primaries |
| Ads conversion firing flag | Observe-only until new actions tested (`NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false` historically) |
| Site tests measurement | **Not wired** |

**Hard rule for advisors:** do not invent conversion action IDs. Name them when creating in Ads UI.

---

## 10. Checklist priority order

### Done (selected)

- US Search live · Brand off  
- AU phone on site (`1300 886 740`)  
- Ads package archived / Editor package exists  
- Sniper + job-seeker negative hygiene in progress (US)  
- Stakeholder emails sent (Brand paused + phone tracking) 2026-08-07  

### Next (priority)

1. Website calls **60+ seconds** (US + AU)  
2. Australia — ad-call wins + website tags  
3. Zoho qualified → Ads  
4. Soft: simplify 888 phone tree (waiting on VC phones/IT + Cheyenne)  
5. Later: Site tests scoreboard (step 34)  

### Daily (until settled)

Search terms · Ad copy/combos · Budget pacing · Keywords + negatives  

---

## 11. Known landmines

1. **`Unkown` / blank ad groups + Broad dual-write** — Account-importing `Keyword` + `Campaign negative` rows together dual-wrote blank/`Unkown` AGs packed with **Enabled Broad positives** (confirmed AU Editor DB 2026-08-08). Fix: campaign negatives via **Keywords, Negative → Make multiple changes** CSV — **not** Account Import with the main package. Delete junk `Unkown` AGs if they reappear.
2. **Legacy AU spend** — `$1.1k+/7d` was `PM_AU_*`, including ugly DSA CPC. Don’t attribute that to Stage 1 `VC_AU_*`.
3. **Do not re-enable Brand** — deferred; expensive; SEO owns it. Only rebuild later if George asks. Flag if a competitor uses “Virtual Coworker” in ads (policy).
4. **Import ≠ Post ≠ Enable** — Import = local Editor draft; Post = upload (can stay Paused); Enable = separate George approval.
5. **API mutate forbidden** — Google Ads API = read-only / 1–2 cheap probes max. Past burn: agents launched ~8 campaigns via API and burned developer-token quota. Builds = Editor CSV only.
6. **Bare Broad `workers` negative** — do not restore; overblocks employer shorthand.
7. **`va workers ph`** — watch/pause, not a victory lap.
8. **One inquiry ≠ two Primaries** — form + Calendly + Zoho offline must not all Primary the same event.
9. **Isolation** — `VC_*` is a clean parallel system. Don’t binge-delete museum `PM_*` / shared lists / old conversions as “cleanup.”

---

## 12. How ChatGPT should advise George today

**Mode:** Conversation / strategy. He is taking a break. Do not turn the chat into a work ticket factory.

**Do:**

- Talk strategy: intent quality, Max Clicks seasoning, Exact vs Phrase, AU legacy vs Stage 1, phone-first measurement, CRO hypotheses.
- Be honest about **low-volume high-intent** — sparse Exact agency traffic can still be the right bet.
- Prefer **Google Ads Editor** for any inventory change advice.
- Treat Brand as **deferred / paused** — don’t center the conversation on it.
- Distinguish **US live VC_*** vs **AU Stage 1 ~$0** vs **AU legacy spend**.
- Treat `va workers ph` and weird shorthand as **watch/pause**, not proof of product-market fit.
- Remind: phone 60s > form spam theater; Zoho is later.

**Do not:**

- Invent conversion IDs, spend figures, or “these Exact adds are converting” without Ads evidence.
- Tell him (or agents) to mutate / enable / bulk-change via Google Ads API.
- Push Brand re-enable, PMax, Broad positives, or Max Conversions before phone + clean conversion actions exist.
- Cheerlead CTR without asking whether traffic was employer-quality.
- Confuse dashboard “done” checkboxes with paid outcomes.

---

## 13. Open questions / things George may want to debate

1. **Agency-intent Exact (and Phrase) enable timing** — import Paused first vs enable a small Exact spine now while Max Clicks seasons?
2. **Duplicate ad group for Phrase** — cleanest structure so Exact stays Exact-only live; worth the Editor clutter?
3. **AU Stage 1 go-live** — wait for website-call + AU tags, or trickle `VC_AU_*` sooner now that legacy is paused?
4. **What “success” means this week** — connected 60s calls vs click volume vs form fills (forms are noisy)?
5. **ROLES budget share** — keep ~40% while CPC is higher, or lean harder into CORE agency spine?
6. **888 phone tree** — still waiting on VC; does that block call-quality reading?
7. **Zoho module truth** — Recruit vs customized CRM; no Leads assumption — when is discovery worth an hour?
8. **Site A/B** — ship creative tests before measurement wiring, or wait so learning isn’t blind?
9. **How aggressive on competitor Exact negatives** — sniper list vs over-blocking research queries?
10. **When (if ever) to leave Max Clicks** — only after verified campaign-specific call/form actions and enough volume?

---

## Quick reference for ChatGPT

```
US live: VC_US_S_CORE + VC_US_S_ROLES · Max Clicks · ~$125/day · Brand OFF
US 7d: ~$298 · 116 clicks · CORE cheaper/higher CTR · ROLES pricier
AU Stage 1: ~$0 · legacy PM_AU_* was ~$1150 / 127 clicks / 7d (now paused in pull)
Spine: agency/firm/company/outsourcing PH VA — Exact add-on CSV Paused; Phrase via dup AG = George ops plan
Watch: va workers ph · job-seeker negs · Unkown AG Broad dual-write
Next: website calls 60s → AU tracking → Zoho later · Site tests unwired
Rules: Editor only · API read-only · Brand deferred · don’t invent conversion IDs
Dash: https://vc-xray.vercel.app · Site: https://www.virtualcoworker.app
```

---

*End of debrief · 2026-08-09 · file: `ads-launch/CHATGPT-OPERATOR-DEBRIEF-2026-08-09.md`*
