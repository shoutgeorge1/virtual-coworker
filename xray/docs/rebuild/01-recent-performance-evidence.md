# 01 — Recent performance evidence + missing-data request

**Certainty rule:** This file separates Verified / Inference / Unknown. No invented CTR, CPC, CPA, or lead counts.

---

## A. What we have (Verified)

| Source | Path | What it proves | What it does **not** prove |
|--------|------|----------------|----------------------------|
| Editor USA export | `audit-data/editor-exports/virtual-coworker-usa.csv` | Structure: 50 camps · 419 AGs · 4085 KWs · 1 Enabled Search (`PM_US_RSA_Brand`, budget field 100, bid Max Conv) · 5 Enabled brand KWs · **Enabled RSA Final URL = `https://virtualcoworker.com/` (WP)**; try.`/us` RSA exists but **Paused** | Clicks, cost, CTR, CPC, conversions, lead quality |
| Editor AU export | `audit-data/editor-exports/virtual-coworker-australia.csv` | Structure: 62 camps · 675 AGs · 3620 KWs · 1 Enabled Search (`PM_AU_RSA_Brand`, budget field 30, bid Max Conv) · 5 Enabled brand KWs · **Enabled RSA Final URL = `https://virtualcoworker.com.au/` (WP, Approved limited)**; try.`/apac` RSA on that campaign is **Paused + Disapproved**; `PM_AU_RSA_Brand_Custom LP` (try.*) is **Paused** | Same — no performance |
| Editor audit | `audit-data/editor-account-audit.md` | Campaign-type museum (PMax/DG/Display leftovers), negative sprawl, URL spray | Spend or ROAS |
| Final URL inventory | `audit-data/final-urls-inventory.{json,csv}` | **6,297** Final URL field refs; homepage+`/services/*` ≈ **82%** of refs; `try`+`lp-*` ≈ **2.2%** | Traffic share (refs ≠ impressions/clicks) |
| LP probes | `audit-data/landing-page-probes.json` + `landing-page-funnel-audit.md` | Live stack/form/GTM/dual-door facts; dead `lp-*`; try thank-you 404 | Ads conversion firing |
| Access / pilot docs | `docs/ads-handoff-status.md`, `docs/access-requirements.md`, `docs/pilot-scope.md` | MCC Accept done; verify Admin in-account; pilot architecture intent | Live account state / Admin verify |

### Enabled remnant (structure only)

| Account | Campaign | Bid (export) | Budget field | Keywords (Enabled) | **Enabled** ad Final URL | Other ad on same AG |
|---------|----------|--------------|--------------|--------------------|--------------------------|---------------------|
| USA `496-715-1855` | `PM_US_RSA_Brand` | Maximize conversions | 100.00 | `virtual coworker` Exact; `virtual coworker usa` Exact; `virtual coworker staffing` Exact; `virtual coworker reviews` Phrase; `virtual coworker pricing` Phrase | `https://virtualcoworker.com/` (Enabled, Approved) | `https://try.virtualcoworker.com/us` (**Paused**, Approved) |
| AU `573-539-1940` | `PM_AU_RSA_Brand` | Maximize conversions | 30.00 | `virtual coworker` Exact; `virtual coworker australia` Exact; `virtual coworker staffing` Exact; `virtual coworker reviews` Phrase; `virtual coworker pricing` Phrase | `https://virtualcoworker.com.au/` (Enabled, Approved limited) | `https://try.virtualcoworker.com/apac` (**Paused**, Disapproved) |

**Verified:** Enabled brand RSAs point at **WordPress**, not try.*. Sitelinks on those brand campaigns still point at WP `/services/*`, pricing, about, blog.  
**Inference:** Agency optimized for Max Conv on an untrusted/contaminated conversion surface; try.* was attempted but is not the enabled Final URL.  
**Unknown:** Whether those remnant campaigns are still spending, or what conversion actions they optimize toward. Structure ≠ live delivery.

### Conversion / tracking crumbs (public HTML only)

| Surface | GTM | Form | AW- in HTML | Employer gate |
|---------|-----|------|-------------|---------------|
| `try…/us` · `try…/apac` | `GTM-KSMWT6QM` | Formspree + Calendly | **Not found** | Employer-lean; no `.ph` dual-door on LP |
| US WP | `GTM-TTKNKT` | GF on `/contact-us/` only | **Not found** | Dual-door to `.ph` |
| AU WP | `GTM-KNDLKVW` | GF on `/contact-us/` only | **Not found** | Dual-door to `.ph` |

---

## B. Performance exports — MISSING

No cost / campaign / keyword / search-term / LP / conversion **performance** exports exist under `audit-data/` or `docs/`.

**Do not invent metrics.** Until the checklist below is filled, early diagnostics cannot be historical — only forward-looking after launch.

---

## C. Exact export checklist (VC / Braden / George with Ads Admin)

Run in **Google Ads UI** (browser) after MCC Admin is accepted. Prefer UI download → CSV. **Do not burn Ads API quota** for these dumps.

### Shared defaults for every report

| Field | Value |
|-------|-------|
| Date range | Last **90 days** + separate **Last 30 days** copy |
| Segment | None first; then optional **Device** and **Day** for Campaign report only |
| Filter | Include all campaigns; note Status column |
| Format | CSV (Google Ads download) |
| Filename prefix | `vc-{market}-{report}-{YYYYMMDD}-d{30|90}.csv` |
| Markets | USA `496-715-1855` · AU `573-539-1940` separately |

### 1. Campaign performance

| | |
|--|--|
| **Report** | Campaigns |
| **Columns** | Campaign · Campaign type · Status · Bid strategy type · Budget · Impr. · Clicks · CTR · Avg. CPC · Cost · Conv. · Cost/conv. · Conv. rate · Conv. value · View-through conv. · Search impr. share (if available) |
| **Decision supported** | What still spends; Max Conv vs Max Clicks history; which types to ignore in rebuild |
| **Filename** | `vc-usa-campaign-20260805-d90.csv` / `vc-au-…` |

### 2. Ad group performance

| | |
|--|--|
| **Report** | Ad groups |
| **Columns** | Campaign · Ad group · Status · Impr. · Clicks · CTR · Avg. CPC · Cost · Conv. · Cost/conv. |
| **Decision supported** | Which themes ever earned clicks (structure archaeology → traffic reality) |
| **Filename** | `vc-{market}-adgroup-…-d90.csv` |

### 3. Keyword performance (Search)

| | |
|--|--|
| **Report** | Keywords |
| **Columns** | Campaign · Ad group · Keyword · Match type · Status · Quality Score · Impr. · Clicks · CTR · Avg. CPC · Cost · Conv. · Cost/conv. · Final URL |
| **Filters** | Campaign type = Search |
| **Decision supported** | Seed Exact launch set with proven clickers; kill job-seeker positives |
| **Filename** | `vc-{market}-keyword-…-d90.csv` |

### 4. Search terms

| | |
|--|--|
| **Report** | Search terms |
| **Columns** | Search term · Match type · Added/Excluded · Campaign · Ad group · Impr. · Clicks · CTR · Avg. CPC · Cost · Conv. · Cost/conv. |
| **Decision supported** | Negative launch list refinement; employer vs job-seeker reality |
| **Filename** | `vc-{market}-searchterms-…-d90.csv` |

### 5. Landing page / Final URL

| | |
|--|--|
| **Report** | Landing pages (or Final URL under Ads → Insights) |
| **Columns** | Final URL · Campaign · Impr. · Clicks · CTR · Avg. CPC · Cost · Conv. · Bounce / engagement if available |
| **Decision supported** | Confirm spray to WP vs try.*; prove homepage waste |
| **Filename** | `vc-{market}-landingpages-…-d90.csv` |

### 6. Conversion actions

| | |
|--|--|
| **Report** | Conversions (Goals / Summary) + Conversion actions settings export if available |
| **Columns** | Conversion action · Category · Source · Counting · Include in Conversions · All conv. · Value · Last 30/90 |
| **Decision supported** | Which actions Max Conv was optimizing; what to exclude from “Conversions” at Stage 1 |
| **Filename** | `vc-{market}-conversions-…-d90.csv` |

### 7. Change history (light)

| | |
|--|--|
| **Report** | Change history |
| **Range** | Last 90 days |
| **Decision supported** | Who flipped bids/budgets/URLs recently |
| **Filename** | `vc-{market}-changehistory-…-d90.csv` |

### Optional (nice, not blocking blueprint)

- Auction insights (brand + core campaigns if they have volume)  
- Call details / CallRail export if numbers already tracked  
- GA4: Landing page + session engagement for `try.*` and WP hire paths (last 90d), filtered to Paid Search if tagged  

**Drop files into:** `audit-data/performance/` (create folder when received).

---

## D. Decisions these exports unlock

1. Whether remnant brand Max Conv is wasting spend → pause vs rebuild-in-place  
2. Historical CPC band for CPC guardrail on Max Clicks (Stage 1) — **only if volume exists**  
3. Which Exact themes earned employer-looking clicks (not just Editor duplicates)  
4. Which conversion actions must be removed from primary “Conversions” before any smart bidding  
5. Whether try.* ever converted in Ads vs WP contact form  

---

## E. Current operating posture (until exports arrive)

| Stance | Rationale |
|--------|-----------|
| Treat conversion signal as **untrusted** | Max Conv on remnant + no public AW- + WP dual-door + Formspree thank-you gap |
| Plan Stage 1 as **Maximize Clicks** + Exact/Phrase Search only | Matches strategic ladder; no CPC ceiling claimed without data |
| Do not inherit campaign architecture | Structure = museum; rebuild clean |
| Keep mining Editor for **negatives + RSA copy ideas only** | Useful archaeology; not performance ranking |
