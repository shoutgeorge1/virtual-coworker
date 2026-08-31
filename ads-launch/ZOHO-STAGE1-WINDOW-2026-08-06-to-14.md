# Zoho Stage 1 window — Sales Enquiries + Job Orders

**Window:** 2026-08-06 00:00 UTC inclusive → 2026-08-15 00:00 UTC exclusive (covers Aug 14 full UTC day).
**Pulled:** 2026-08-14T19:31:44.679403+00:00 (fresh COQL).
**Method:** Zoho CRM API v8 COQL `SELECT` only. No creates/updates/deletes. `ZOHO_CRM_ENABLED` left false/unset. No Google Ads calls in this pull.
**PII:** First_Name + Last_Name + Company included for ChatGPT narrative. Phone numbers omitted. Emails not selected.
**Brisbane lag:** filter is `Created_Time` only — no Modified_Time extension. Label if a row looks backdated.

> **Window-edge note:** One Job Order returns `Created_Time` **2026-08-05T18:51:34** (AU · Customer Support Coordinator · `AU_RSA_brand` + gclid). Included because COQL returned it under the Stage 1 filter / org-time lag. **Not** a Stage 1 `VC_*` win — museum campaign name.

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
