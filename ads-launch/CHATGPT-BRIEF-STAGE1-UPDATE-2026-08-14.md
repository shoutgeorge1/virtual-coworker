# ChatGPT brief — Stage 1 update (Zoho + sales numbers + RSA/ops)

_Compiled 2026-08-14T19:33:28.346760+00:00 · repo facts only · no email draft · Zoho read-only · no Ads mutate in this compile_

---

## 1. ChatGPT one-liner intent

George will draft the email himself. Use this package as **facts only**: Stage 1 sales/ops numbers + what RSA/ads work shipped this week vs today + the full Zoho Sales Enquiry / Job Order window dump. Do not invent that `.app` or `VC_*` attribution landed in Zoho. Do not draft spin.

---

## 2. Sales / Stage 1 numbers block

### CRM activity during the paid flight — vs quietest prior 9d

**Monitoring baseline only — no demonstrated lift yet** (SE −4%, JO −31%). Not evidence ads caused an increase or decline. Concurrent Zoho CRM while Stage 1 ads ran. Click-ID often missing (site / GMB / phone / manual). **0 of 51** Stage 1 Sales Enquiries have `utm_gclid`.

| Metric | Baseline Jul 1–9 | Stage 1 Aug 6–14 | Δ |
|---|---:|---:|---:|
| Sales Enquiries | **53** (US 26 · AU 27) | **51** (US 23 · AU 25) | **−4%** |
| Job Orders | **26** (US 12 · AU 14) | **18** (US 8 · AU 9) | **−31%** |
| Discovery scheduled | **0** | **4** | **new** |

**Baseline chosen:** quietest recent comparable 9-day window before Stage 1 (`2026-07-01` → `2026-07-09`). Lowest SE among scanned May–Aug windows. Immediate prior Jul 28–Aug 5 was higher (80 SE, junk-heavy). Active-CRM Dec 2025–Aug 5 average (~74 SE / 28 JO per 9d) is hotter — not used as the floor. Empty pre-Oct 2025 months excluded.

**How to say it:** No demonstrated CRM lift during the paid flight yet; Discovery bookings rose; Ads still cannot see this as click-attributed CPL. Cheyenne 4/2 remains the paid-ops story.

---

### Early US sales-ops handoff (Cheyenne · Sat Aug 8 – Mon Aug 10)

| Metric | Value |
|---|---|
| Enquiries | **4** |
| Sales calls booked | **2** |
| Junk (job seeker) | 1 |
| Not a fit | 1 (Project-based — not a fit for ongoing hire) |
| Spend (VC_US_S_CORE + ROLES, same window) | **$394.79** |
| Cost / enquiry | **$98.70** |
| Cost / booked call | **$197.40** |
| Clicks / CPC | 136 clicks · ~$2.9 CPC |
| Caveat | Early / small sample — do not treat as steady-state CPL. Job-seeker junk never counts as a win. |

### Ads performance (executive snapshot · pulled 2026-08-14 · Stage 1 Core+Roles)

| Market | Window | Impr | Clicks | CTR | Spend | Avg CPC | Ads conversions |
|---|---|---:|---:|---:|---:|---:|---:|
| US | last 7d | 4362 | 465 | 10.66% | $1,256.34 | $2.7 | 1.0 |
| US | focus day 2026-08-14 UTC | 498 | 48 | 9.64% | $164.44 | $3.43 | 1.0 |
| AU | last 7d Stage 1 Core+Roles (`totals_stage1_last_7_days` — AUD) | 1679 | 217 | 12.92% | A$769.28 | A$3.55 | — |
| AU | focus day 2026-08-14 | 334 | 41 | 12.28% | A$130.39 | A$3.18 | — |

### Budgets / bidding (locked ops)

- **US:** Core **$150**/day + Roles **$100**/day (= **$250**/day). Operator CPC caps noted: CORE $15 / ROLES $12.
- **AU:** Core **A$75**/day + Roles **A$50**/day (= **A$125**/day). Caps noted: CORE A$10 / ROLES A$8.
- **AU enquiries:** still **waiting on sales report** (Cheyenne Aug 10 handoff was US-only). Do not invent zero AU leads.

### Agency-era JO CPA (context, not Stage 1)

- Old-account spend was large (1 Aug 2024 – ~Aug 2026). Do **not** combine US USD + AU AUD.
- Ads “Zoho JO Submitted via Zapier” ≈ **67 US + 36 AU** → roughly **US $10,819** and **AU A$12,727** per reported JO if those uploads are real — **unverified**, museum path, **not** Stage 1 `VC_*`.
- Live CRM has **782** Job Orders all-time in same years — Ads JO number is a thin slice.

### Tracking / GTM / AU (one line)

- **`.app` GTM/GA4 live** (US + AU Production tags per executive note: AU GTM-5T6KPVSF / G-7X1K9V2LFE). Form email/webhook is the live delivery path; **`ZOHO_CRM_ENABLED` still false** — `.app` does **not** write Sales Enquiries. Brand deferred / Brand paused.

---

## 3. Zoho full window dump

Companion standalone: `ads-launch/ZOHO-STAGE1-WINDOW-2026-08-06-to-14.md`

Raw JSON (gitignored): `.local/zoho/probe-stage1-chatgpt-dump-2026-08-14.json`

## A. Window + method

| Item | Value |
|---|---|
| Filter | `Created_Time >= '2026-08-06T00:00:00+00:00' AND Created_Time < '2026-08-15T00:00:00+00:00'` |
| Modules | Leads (Sales Enquiries), Job_Orders, Calls count, Tasks count |
| API calls this pull | 4 |
| Stopped | None |
| Read-only | **YES** |

- Sales Enquiries: **51**
- Job Orders: **18**
- Calls with Call_Start_Time in window: **31** (no gclid field on Calls module)
- Tasks Created_Time in window: **59** (not all Discovery)

## B. Sales Enquiries (Leads) — every record

| # | Created_Time | Sub_TS | Region | Status | Source | Form | First | Last | Company | Owner | Created_By | utm_source | utm_medium | utm_campaign | utm_term | utm_content | Campaign_Name | gclid? | Website | Referrer/Referring | landing | Discovery_Call |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-06T03:26:04 | — | AU | Job Order Submitted | Website | Job Order Form | testing sync | fina | test crm sync | Wallace | McCartan | — | — | — | — | — | — | no | crmsync.com | — | other_host | — |
| 2 | 2026-08-06T03:34:43 | — | AU | Job Order Submitted | Website | Job Order Form | ZoFlowX sync | test | ZoflowX test | Wallace | McCartan | — | — | — | — | — | — | no | zoflowx.com | — | other_host | — |
| 3 | 2026-08-06T03:47:11 | — | AU | Job Order Submitted | Website | Job Order Form | zoflowx sync | test 2 | test | Wallace | McCartan | — | — | — | — | — | — | no | test.com | — | other_host | — |
| 4 | 2026-08-06T03:52:48 | — | AU | Job Order Submitted | Website | Job Order Form | zoflowx sync | test | testingggg | Wallace | McCartan | — | — | — | — | — | — | no | testingggg.com | — | other_host | — |
| 5 | 2026-08-06T04:04:23 | — | AU | Job Order Submitted | Website | Job Order Form | recruit status | number test | test6 | Wallace | McCartan | — | — | — | — | — | — | no | test6.com | — | other_host | — |
| 6 | 2026-08-06T05:08:13 | — | AU | Job Order Submitted | Website | Job Order Form | final testing | final testing | finaltesting | Wallace | McCartan | — | — | — | — | — | — | no | finaltesting.com | — | other_host | — |
| 7 | 2026-08-06T05:11:26 | — | AU | Job Order Submitted | Website | Job Order Form | final test 2 | final test 2 | final | Wallace | McCartan | — | — | — | — | — | — | no | finaltest.com | — | other_host | — |
| 8 | 2026-08-06T05:16:10 | — | AU | Job Order Submitted | Website | Job Order Form | test 12 | test 12 | test 12 | Wallace | McCartan | — | — | — | — | — | — | no | test12.com | — | other_host | — |
| 9 | 2026-08-06T05:21:42 | — | AU | Job Order Submitted | Website | Job Order Form | test201 | tet201 | test201 | Wallace | McCartan | — | — | — | — | — | — | no | test201.com | — | other_host | — |
| 10 | 2026-08-06T05:27:57 | — | AU | Job Order Submitted | Website | Job Order Form | Inboxist | Final Test | inboxist final | Wallace | McCartan | — | — | — | — | — | — | no | inboxistfinal.com | — | other_host | — |
| 11 | 2026-08-06T16:59:03 | — | USA | Junk Lead | Website | — | Julissa | Mejia | CloudClinic Health | Gichana | Marketing (Lois) | (direct) | (none) | (direct) | — | — | — | no | — | — | blank | — |
| 12 | 2026-08-06T18:53:23 | — | USA | Not Ready - 1 Month | Website | — | Jessica | Gardner | Sage Terrace Properties | Gichana | Marketing (Lois) | (direct) | (none) | (direct) | — | — | — | no | — | — | blank | — |
| 13 | 2026-08-07T10:44:15 | — | USA | Not Ready - 1 Month | Website | — | Austin | Dawood | HiStandards | Gichana | Marketing (Lois) | — | — | — | — | — | — | no | — | — | blank | — |
| 14 | 2026-08-07T11:34:14 | — | USA | Job Order Submitted | Website | Job Order Form | Hong | Suh | 7ohm | Gichana | Marketing (Lois) | google | organic | organic: google | — | — | — | no | — | — | blank | — |
| 15 | 2026-08-07T15:20:49 | — | USA | Job Order Submitted | Website | Job Order Form | Dan | Ross | Cavmir | Gichana | Gichana | — | — | — | — | — | — | no | CAVMIR.COM | — | other_host | — |
| 16 | 2026-08-07T20:33:42 | — | AU | Information Brochure Sent | Website | — | Luke | Sullivan | Livansson | Wallace | Marketing (Lois) | — | — | — | — | — | — | no | — | — | blank | — |
| 17 | 2026-08-08T21:35:54 | — | — | Junk Lead | Website | — | cloudiya | abdurajan | Teleperformance | Gichana | Marketing (Lois) | facebook.com | referral | referral: facebook.com | — | — | — | no | — | — | blank | — |
| 18 | 2026-08-08T23:23:37 | — | AU | Junk Lead | Website | — | Jerson | Sore | Restoration Growth | Wallace | Marketing (Lois) | — | — | — | — | — | — | no | — | — | blank | — |
| 19 | 2026-08-09T18:20:53 | — | USA | Decided Against / Not a Fit | Website | — | Pratik | Risbud | Kato | Gichana | Marketing (Lois) | (direct) | (none) | (direct) | — | — | — | no | — | — | blank | — |
| 20 | 2026-08-09T21:09:34 | — | AU | Decided Against / Not a Fit | Website | — | Stephen | Porter | Treesafe Australia | Wallace | Marketing (Lois) | — | — | — | — | — | — | no | — | — | blank | — |
| 21 | 2026-08-09T22:45:39 | — | USA | Information Brochure Sent | Website | — | Steven | Matsumura | Matsumura Properties LLC | Gichana | Marketing (Lois) | google | organic | organic: google | — | — | — | no | — | — | blank | — |
| 22 | 2026-08-10T01:22:05 | — | AU | No Shows | Website | — | Thomas | Burnside | CoBlueprint | Wallace | Marketing (Lois) | — | — | — | — | — | — | no | — | — | blank | — |
| 23 | 2026-08-10T06:50:13 | — | USA | Junk Lead | Website | — | Irish | Badayos | VA | Gichana | Marketing (Lois) | facebook.com | referral | referral: facebook.com | — | — | — | no | — | — | blank | — |
| 24 | 2026-08-10T07:42:41 | — | USA | Information Brochure Sent | Website | — | Katherine | Drawsand | Route Runners Logistics | Gichana | Marketing (Lois) | — | — | — | — | — | — | no | — | — | blank | — |
| 25 | 2026-08-10T13:31:19 | — | USA | Information Brochure Sent | Website | — | Erika | Ramos | ECOM LLC | Gichana | Marketing (Lois) | bing | organic | organic: bing | — | — | — | no | — | — | blank | — |
| 26 | 2026-08-10T19:26:52 | — | AU | Job Order Submitted | — | Job Order Form | Nikolai | Caraig | Nina Test | Wallace | Caraig | — | — | — | — | — | — | no | — | — | blank | — |
| 27 | 2026-08-10T19:33:03 | — | AU | Job Order Submitted | — | Job Order Form | Nikolai | Caraig | test | Wallace | Caraig | — | — | — | — | — | — | no | — | — | blank | — |
| 28 | 2026-08-10T19:47:06 | — | AU | Junk Lead | — | — | Marvin | Agustin | augusten | Wallace | Caraig | — | — | — | — | — | — | no | — | — | blank | — |
| 29 | 2026-08-10T20:44:37 | — | AU | Sales Call Follow Up 1 | Website | — | Damian | Grima | Innerspace | Wallace | Marketing (Lois) | — | — | — | — | — | — | no | — | — | blank | — |
| 30 | 2026-08-11T00:32:23 | — | USA | Unresponsive Clients | Website | — | Daquan | Booker | Real Home solutions | Gichana | Marketing (Lois) | google | organic | organic: google | — | — | — | no | — | — | blank | — |
| 31 | 2026-08-11T04:55:17 | — | AU | Information Brochure Sent | Website | — | William | Fellowes | The Outback Distilling Co. | Wallace | Marketing (Lois) | chatgpt.com | — | — | — | — | — | no | [email] | — | other_host | — |
| 32 | 2026-08-11T11:17:22 | — | USA | Discovery Scheduled | Website | — | Carly | Mednick | Monday Talent | Gichana | Marketing (Lois) | google | organic | organic: google | — | — | — | no | — | — | blank | — |
| 33 | 2026-08-11T16:47:04 | — | AU | Job Order Submitted | Website | Job Order Form | Thomas | Redden | Naparoo | Wallace | Marketing (Lois) | chatgpt.com | — | — | — | — | — | no | — | — | blank | — |
| 34 | 2026-08-11T21:45:25 | — | AU | Discovery Scheduled | Website | — | Jayden | Mccormack | Physio to You | Wallace | Marketing (Lois) | — | — | — | — | — | — | no | — | — | blank | — |
| 35 | 2026-08-11T23:00:44 | — | AU | Attempted to Contact 1 (Auto) | Website | — | Tania | Devoti | Obzervr | Wallace | Marketing (Lois) | — | — | — | — | — | — | no | — | — | blank | — |
| 36 | 2026-08-12T01:44:07 | — | AU | Decided Against / Not a Fit | Website | — | Sophie | Abela | NA | Wallace | Marketing (Lois) | — | — | — | — | — | — | no | — | — | blank | — |
| 37 | 2026-08-12T13:22:30 | — | USA | Decided Against / Not a Fit | Google | — | Kevin | Braun | Kevin Braun | Gichana | Gichana | — | — | — | — | — | — | no | — | — | blank | — |
| 38 | 2026-08-12T14:22:09 | — | USA | Discovery Scheduled | Website | — | Larry | Pham | Self | Gichana | Marketing (Lois) | google | organic | organic: google | — | — | — | no | — | — | blank | — |
| 39 | 2026-08-12T16:16:30 | — | USA | Information Brochure Sent | Website | Job Order Form | Miatta | Thomas | Wholistic Services, Inc. | Gichana | Gichana | (direct) | (none) | (direct) | — | — | — | no | — | — | blank | — |
| 40 | 2026-08-13T01:36:58 | — | — | Junk Lead | Website | — | Rica Vivien | Sudaria | N/A | Gichana | Marketing (Lois) | (direct) | (none) | (direct) | — | — | — | no | — | — | blank | — |
| 41 | 2026-08-13T05:33:05 | — | USA | Decided Against / Not a Fit | Forbes | — | Walter | Clements | Clement | Gichana | Marketing (Lois) | — | — | — | — | — | — | no | — | — | blank | — |
| 42 | 2026-08-13T10:14:49 | — | USA | Junk Lead | Google | — | Renz | Rodney Ramido | — | Gichana | Gichana | — | — | — | — | — | — | no | — | — | blank | — |
| 43 | 2026-08-13T10:20:47 | — | USA | Not Ready - 1 Month | Referral Partner | — | John | Azar | Pick Fifteen Capital | Gichana | Gichana | — | — | — | — | — | — | no | — | — | blank | — |
| 44 | 2026-08-13T13:15:52 | — | USA | Information Brochure Sent | Phone | — | Eli | Beyder | Property Management | Gichana | Gichana | — | — | — | — | — | — | no | — | — | blank | — |
| 45 | 2026-08-13T17:59:02 | — | USA | Junk Lead | Website | — | Renel Ervic | Macalam | VA | Gichana | Marketing (Lois) | facebook.com | referral | referral: facebook.com | — | — | — | no | — | — | blank | — |
| 46 | 2026-08-13T22:22:52 | — | AU | Discovery Scheduled | Cold Call | — | Matt | Forminston | Matt Formston AM Keynote Speaker / Author / Multi-Sport Worl | Wallace | Wallace | — | — | — | — | — | — | no | https://www.mattformston.com | — | other_host | — |
| 47 | 2026-08-13T22:49:20 | — | AU | New Enquiry (Auto) | Phone | — | Glenn | Peri | Matike Consultancy | Wallace | Wallace | — | — | — | — | — | — | no | — | — | blank | — |
| 48 | 2026-08-14T05:14:34 | — | USA | Information Brochure Sent | Website | — | Leslie | Taylor | Oak Hills Counseling Center | Gichana | Marketing (Lois) | (direct) | (none) | (direct) | — | — | — | no | — | — | blank | — |
| 49 | 2026-08-14T06:34:00 | — | — | Junk Lead | Website | — | MAYBELLE | BRAZA | Department of Education | Gichana | Marketing (Lois) | l.facebook.com | referral | referral: l.facebook.com | — | — | — | no | — | — | blank | — |
| 50 | 2026-08-14T09:05:19 | — | USA | Junk Lead | Website | — | Vilmar | Licudan | — | Gichana | Gichana | — | — | — | — | — | — | no | — | — | blank | — |
| 51 | 2026-08-14T12:22:37 | — | USA | Job Order Submitted | Website | Job Order Form | Justin | Nguyen | Accounting Insight Inc | Gichana | Pinzon | — | — | — | — | — | — | no | https://www.accountinginsight.net/our-team | — | other_host | — |

## C. Job Orders — every record

| # | Created_Time | Region | Stage | Name | Company | First | Last | Owner | Created_By | Client_Name (SE lookup) | UTM_Source | UTM_Medium | UTM_Campaign | UTM_Term | UTM_Content | gclid? | test? |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-05T18:51:34 | AU | Endorsed Candidates | Customer Support Coordinator | Safeco | — | — | McCartan | McCartan | Chantel Pavlic | googleads | cpc | AU_RSA_brand | virtual coworker | — | YES | — |
| 2 | 2026-08-06T08:35:03 | USA | Pending Feedback | Owner | Blessed Foods | — | — | McCartan | McCartan | Leonora Douglas | google | organic | organic: google | — | — | no | — |
| 3 | 2026-08-07T08:26:31 | USA | Endorsed Candidates | Marketing Project Manager | Real Advantage Title | — | — | McCartan | McCartan | Kim Pratt | google | cpc | US_DSA_catchall | — | — | YES | — |
| 4 | 2026-08-07T15:27:16 | USA | Sourcing | Owner | Cavmir | — | — | McCartan | McCartan | Dan Ross | — | — | — | — | — | no | — |
| 5 | 2026-08-09T16:48:04 | AU | Sourcing | Teagan Grace | Fire Service Plus | — | — | McCartan | Repompo | Teagan Grace | — | — | — | — | — | no | — |
| 6 | 2026-08-10T11:44:38 | USA | Endorsed Candidates | Owner | 7ohm | — | — | McCartan | McCartan | Hong Suh | google | organic | organic: google | — | — | no | — |
| 7 | 2026-08-10T13:29:58 | — | Ultimatum Email | zoflowx august 11 | zoflowx august 11 | — | — | McCartan | McCartan | — | — | — | — | — | — | no | TEST? |
| 8 | 2026-08-10T21:51:37 | USA | Job Order Submitted | Owner | 7ohm | — | — | McCartan | McCartan | — | — | — | — | — | — | no | — |
| 9 | 2026-08-10T21:52:36 | AU | Sourcing | Head of IT | Industrial Fittings Sales Pty Ltd | — | — | McCartan | Repompo | Sonny Dyer | (direct) | (none) | (direct) | — | — | no | — |
| 10 | 2026-08-12T15:42:10 | AU | Sourcing | Owner | JB Beauty | — | — | McCartan | McCartan | — | — | — | — | — | — | no | — |
| 11 | 2026-08-12T16:20:53 | USA | Endorsed Candidates | Chief Administrative Officer | Wholistic Services, Inc. | — | — | McCartan | McCartan | — | — | — | — | — | — | no | — |
| 12 | 2026-08-12T16:36:12 | AU | Endorsed Candidates | Administrative Assistant - Naparoo | Naparoo | — | — | McCartan | McCartan | Thomas Redden | chatgpt.com | — | — | — | — | no | — |
| 13 | 2026-08-12T21:14:34 | AU | Sourcing | Teagan Grace | Fire Service Plus | — | — | McCartan | Repompo | Teagan Grace | — | — | — | — | — | no | — |
| 14 | 2026-08-12T23:14:32 | AU | Endorsed Candidates | operations manager | The Outback Distilling Co. | — | — | McCartan | McCartan | — | — | — | — | — | — | no | — |
| 15 | 2026-08-12T23:52:50 | AU | Sourcing | agent assign test | agent assign test | 1st name | 2nd name | McCartan | McCartan | — | — | — | — | — | — | no | TEST? |
| 16 | 2026-08-13T19:34:53 | AU | Job Order Submitted | crm to recruit recruit test | crm to recruit recruit test | 1st | 2nd | McCartan | McCartan | — | — | — | — | — | — | no | TEST? |
| 17 | 2026-08-14T12:23:53 | USA | Job Order Submitted | Owner | Accounting Insight Inc | Justin | Nguyen | McCartan | McCartan | — | — | — | — | — | — | no | — |
| 18 | 2026-08-14T12:23:59 | USA | Sourcing | Justin Nguyen | Accounting Insight Inc | — | — | McCartan | McCartan | Justin Nguyen | — | — | — | — | — | no | — |

## D. Calls / Discovery

- **Calls** in window (Call_Start_Time): **31**. Calls module has no utm_gclid / campaign fields in schema — cannot stamp Google/paid from Calls alone.
- **Discovery Scheduled** Sales Enquiries: **4**
  - 2026-08-13T22:22:52 · AU · Matt Forminston · Matt Formston AM Keynote Speaker | Author | Multi-Sport Worl · source=Cold Call · utm_source=— · gclid=no · discovery_date=—
  - 2026-08-12T14:22:09 · USA · Larry Pham · Self · source=Website · utm_source=google · gclid=no · discovery_date=—
  - 2026-08-11T21:45:25 · AU · Jayden Mccormack · Physio to You · source=Website · utm_source=— · gclid=no · discovery_date=—
  - 2026-08-11T11:17:22 · USA · Carly Mednick · Monday Talent · source=Website · utm_source=google · gclid=no · discovery_date=—
- Tasks created in window: **59** (not filtered to Discovery; cheap count only).

## E. Rollups

### Region × Lead_Source × has_gclid × has_VC_campaign × looks_like_app

| Region | Lead_Source | gclid | VC_campaign | .app | n |
|---|---|---|---|---|---:|
| AU | Website | no_gclid | no_VC | not_app | 20 |
| USA | Website | no_gclid | no_VC | not_app | 18 |
| (blank) | Website | no_gclid | no_VC | not_app | 3 |
| AU | (blank) | no_gclid | no_VC | not_app | 3 |
| USA | Google | no_gclid | no_VC | not_app | 2 |
| AU | Cold Call | no_gclid | no_VC | not_app | 1 |
| AU | Phone | no_gclid | no_VC | not_app | 1 |
| USA | Forbes | no_gclid | no_VC | not_app | 1 |
| USA | Phone | no_gclid | no_VC | not_app | 1 |
| USA | Referral Partner | no_gclid | no_VC | not_app | 1 |

### Paid-ish hint rows (any of: gclid, google source, cpc medium, campaign name ads/DSA/RSA/VC_)

| Type | Created | Region | Name/Company | Status/Stage | Source/UTM | Hints |
|---|---|---|---|---|---|---|
| SE | 2026-08-13T10:14:49 | USA | Renz Rodney Ramido / | Junk Lead | src=Google; utm=—/—; camp=— | google_source |
| SE | 2026-08-12T14:22:09 | USA | Larry Pham / Self | Discovery Scheduled | src=Website; utm=google/organic; camp=organic: google | google_source |
| SE | 2026-08-12T13:22:30 | USA | Kevin Braun / Kevin Braun | Decided Against / Not a Fit | src=Google; utm=—/—; camp=— | google_source |
| SE | 2026-08-11T11:17:22 | USA | Carly Mednick / Monday Talent | Discovery Scheduled | src=Website; utm=google/organic; camp=organic: google | google_source |
| SE | 2026-08-11T00:32:23 | USA | Daquan Booker / Real Home solutions | Unresponsive Clients | src=Website; utm=google/organic; camp=organic: google | google_source |
| SE | 2026-08-09T22:45:39 | USA | Steven Matsumura / Matsumura Properties LLC | Information Brochure Sent | src=Website; utm=google/organic; camp=organic: google | google_source |
| SE | 2026-08-07T11:34:14 | USA | Hong Suh / 7ohm | Job Order Submitted | src=Website; utm=google/organic; camp=organic: google | google_source |
| JO | 2026-08-10T11:44:38 | USA | Owner / 7ohm | Endorsed Candidates | utm=google/organic; camp=organic: google | google_source |
| JO | 2026-08-07T08:26:31 | USA | Marketing Project Manager / Real Advantage Title | Endorsed Candidates | utm=google/cpc; camp=US_DSA_catchall | gclid, google_source, cpc_medium, campaign_name_hint |
| JO | 2026-08-06T08:35:03 | USA | Owner / Blessed Foods | Pending Feedback | utm=google/organic; camp=organic: google | google_source |
| JO | 2026-08-05T18:51:34 | AU | Customer Support Coordinator / Safeco | Endorsed Candidates | utm=googleads/cpc; camp=AU_RSA_brand | gclid, google_source, cpc_medium, campaign_name_hint |

### CAN vs CANNOT support “George paid Search attribution”

| Verdict | Definition | Count (Sales Enquiries) |
|---|---|---:|
| **CAN** | Has `utm_gclid` (and ideally google/VC campaign stamps) | 0 |
| **WEAK maybe** | No gclid, but Lead_Source=Google or utm_source google/googleads (could be organic or paid; not proof) | 7 |
| **CANNOT** | No gclid; no strong paid stamp tying to VC_* / .app | 51 |

**Job Orders with gclid:** 2 (these may be recoverable historical paid clicks — check UTM_Campaign; still not proof of Stage 1 VC_* unless campaign matches).

JO gclid detail:
- 2026-08-07T08:26:31 · USA · Marketing Project Manager · utm=google/cpc/US_DSA_catchall · stage=Endorsed Candidates · test=False
- 2026-08-05T18:51:34 · AU · Customer Support Coordinator · utm=googleads/cpc/AU_RSA_brand · stage=Endorsed Candidates · test=False

## F. Honest one-liner for ChatGPT system

> None of the Zoho Sales Enquiries in this window have utm_gclid / VC_* / .app; George still wants the full list for narrative options. Two Job Orders in-window carry UTM_Gclid (not proven Stage 1 VC_*). `.app` form → Zoho write is still off (`ZOHO_CRM_ENABLED` false).

---

## 4. Ops update: RSA + ads work this week / today

**Accuracy rule:** Editor CSV = built package. Live = only where a doc/post log says Post/Enable/API update happened. Do not invent UI Posts George did not log.

### Today — 2026-08-14 (confirmed in repo)

- **RSA challenger copy POSTED via Google Ads API** (George-authorized 2026-08-14). Action = **`update_paused` only**. Evidence: `ads-launch/_rsa_challenger_post.json` @ `2026-08-14T19:30:07Z`.
  - **29** ads copy-updated · **29** left Paused · **0** enabled · **0** failed.
  - US jobs: **17** · AU jobs: **12**.
  - US: Agency_PH, Offshore_VA_PH, Staffing_Agency_PH, VA_Agency_Firm_PH, Virtual_Staff_PH, Administration_EA_PH, Accounting/Bookkeeping/CS/Marketing/HR/Recruitment/Sales/Social (+ some Outsource), Appointment_Setter_Hire_PH.
  - AU: Agency_PH, Hire_VA_PH, Offshore_VA_PH, Administration_EA_PH, Accounting/Bookkeeping/CS/Marketing/Sales/Social (+ some Outsource).
  - Brand untouched. Enable only if Ad Strength = Excellent.
- **Zoho Stage 1 window re-read** (this brief) — COQL read-only.
- **X-ray / Executive / RSA review** data baked today under `xray/`.
- **Attribution recovery** package from Aug 13 still on disk: `ads-launch/ATTRIBUTION-RECOVERY-2026-08-13/`.

### This week — Editor packages (Aug 9–12)

| Work | When | Files | Intended | Live (docs only) |
|---|---|---|---|---|
| Emotional RSA add US | 08-09 | `google-ads-editor-rsa-add-emotional-us.csv` | 24 Paused | Editor package |
| Semantic Exact AGs | 08-09 | semantic-adgroups-add + pause-dupes | 4 AGs Paused | Those AGs appear in today’s RSA post targets → exist live |
| Human RSA pause+add ROLES | 08-12 | pause-weak + rsa-add-human-us | 19+19 Paused | Editor Import/Post playbook |
| Admin RSA rewrite | 08-12 | rsa-add-admin-us (folded into human-add) | 2 Paused | Prefer human-add to avoid double import |
| Winner-comp RSA | 08-12 | winner-comp pause+add | 4 pause + 10 add Paused | Editor package |
| AU human RSA draft | 08-10 | `RSA-HUMAN-AU-2026-08-10.md` | Draft | Today’s API update_paused also hit AU challengers |
| Sitelinks | 08-10 | sitelink-add-us/au | CORE+ROLES | **US verified; AU missing — re-import AU** |
| Call assets / phone | 08-10 | CALL-ASSET-* + 888 restore | Public US **888-964-8644** | 310 swap superseded (DECISIONS lock) |
| Sniper negatives | earlier | `VC_US_S_Sniper_Negatives.*` | Campaign list | George attached to CORE+ROLES |
| Brand defense planning | 08-13 | BRAND-US-DEFENSE-AUDIT | Planning only | **Brand deferred — no Post/Enable** |
| Zoho + attribution read | 08-13 | ZOHO-CRM-READ + ATTRIBUTION-RECOVERY | Read-only | Done |

### Pending

- Enable RSA challengers only if Excellent (all still Paused in post log).
- AU sitelink re-import.
- `.app` → Zoho write still off.
- Zoho offline import: NOT READY (0 Stage 1 SE gclid).
- Brand deferred. AU enquiry counts from ops: waiting.

---

## 5. Attribution honesty line

> **None of the Zoho Sales Enquiries in 2026-08-06→14 have `utm_gclid` / `VC_*` / `.app`.** Full SE list kept for narrative. **2 Job Orders** carry `UTM_Gclid` with museum campaigns `US_DSA_catchall` / `AU_RSA_brand` — **not** Stage 1 `VC_*`. One JO `Created_Time` **2026-08-05** is a window-edge/org-time lag row — label clearly.

**Halo volume (concurrent CRM, not paid CAC):** Stage 1 SE **51** / JO **18** vs quietest prior 9d (Jul 1–9) SE **53** / JO **26** → SE **−4%** · JO **−31%**. Discovery scheduled **4** vs **0**. Frame as CRM activity during the paid flight with click-IDs usually blank — not click-attributed CPL.

---

## 6. Suggested fact bullet — put sales on notice (read-only Zoho API)

Not an email draft. Fact George can paste:

- Cursor/George has **read-only Zoho CRM API** (COQL / modules.READ) on the live Virtual Coworker org for attribution truth.
- **Nothing is being written** to Zoho from this work (`ZOHO_CRM_ENABLED` stays false). No `.app` form → Sales Enquiry create yet.
- Sales should know: Stage 1 paid Search on `.app` is **not** auto-logging gclid’d enquiries in Zoho; current SE rows still look like WordPress / Zapier / human entry.
- Paid-click proof on a deal needs `utm_gclid` (and ideally campaign) on the CRM row — missing on new Stage 1 Sales Enquiries.

---

## File index

| File | What |
|---|---|
| `ads-launch/CHATGPT-BRIEF-STAGE1-UPDATE-2026-08-14.md` | This package |
| `ads-launch/ZOHO-STAGE1-WINDOW-2026-08-06-to-14.md` | Zoho-only dump |
| `xray/data/zoho-stage1-halo.json` | CRM monitoring baseline vs Stage 1 counts (Executive) |
| `.local/zoho/probe-stage1-chatgpt-dump-2026-08-14.json` | Raw sanitized pull |
| `ads-launch/_rsa_challenger_post.json` | Today’s RSA API update_paused log |
| `xray/data/executive-snapshot.json` | Spend / CTR / early CPL |

