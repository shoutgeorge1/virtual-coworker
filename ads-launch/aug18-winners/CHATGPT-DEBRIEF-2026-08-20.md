# Virtual Coworker — Aug 18 conversion forensic debrief (planner brief)

**For:** ChatGPT (disconnected planner).  
**From:** Cursor workers. Forensic pull already done. Do not ask ChatGPT to run APIs, Editor, Gmail, Zoho writes, or Ads mutations.  
**Date of brief:** 2026-08-20 (updated same day with George’s measurement correction + quality-gate proposal).  
**Workspace:** `~/Developer/virtual-coworker` (local Mac).  
**Do not commit / deploy / open Chrome from this document.** George pastes this into ChatGPT for planning only.

**Quality rule (operating logic, now binding):** Zoho human outcome outranks Google Ads conversion tags, CTR, ad strength, GA4 “conversions,” and landing-page opinions. Junk Lead and Decided Against / Not a Fit are not winners. A path that looks strong in Ads can be junk in CRM. Treat Ads counts as a measurement event, not a person.

**Measurement rule (George, 20 Aug — binding):** Form submitted + call booked = **one human, two funnel steps, stronger if they booked.** That is **not** automatic duplicate tracking. Only flag duplication if the **same** action fires repeatedly with no distinct user action. Best path: **ad click → employer form → booked call.** A booked call is a strong employer outcome **only after** Zoho says employer (not junk / job-seeker / test / unknown). Do **not** activate offline uploads. Do **not** switch to Maximize Conversions. Score AU and US separately. Neither market is ready if biddable actions still mix junk.

**PII rule:** This brief uses Zoho record IDs, hashed gclid tokens already in the redacted extract, and company tokens (first letter + length). No emails, phones, raw GCLIDs, or private notes.

---

## 0. Operator today (George’s one job)

Checklist (`xray/launch-control.html` → live Checklist) already says:

1. Google Ads Editor → **Australia** account `573-539-1940`.
2. Get recent changes.
3. Import only `ads-launch/aug18-winners/02-au-recruitment-junk-reversible.csv`.
4. Review: **two rows**, both `Recruitment_Hire_PH` — pause Exact `australia virtual assistant`; Exact negative `virtual assistant hiring in australia`.
5. Campaign stays **Enabled**.
6. Post **that file only**. Stop.

Leave the two good keywords alone: US `virtual assistant agency in usa` (Exact + Phrase in `Hire_VA_PH`) and AU `hire a social media manager` (Phrase in `Social_Media_Hire_PH`). File `03-au-smm-exact-enable.csv` waits. Do not touch US in this pass. Do not switch bidding. Do not turn on uploads.

Local scoreboard (do not rewrite from this brief): `xray/aug18-conversions.html`.

---

## 1. Situation and operating-logic change

Virtual Coworker Stage 1 Search (`VC_US_*`, `VC_AU_*`) has been live since early August 2026. On Ads calendar **18 August 2026** the accounts looked loud: **2.0 US + 4.0 AU conversions** (click date, from the 19 Aug executive snapshot). That used to be enough to call a path a “winner” and protect or scale it.

That logic is now wrong.

Workers pulled Zoho CRM (read-only COQL), GA4 Data API, landing-page git, an existing Ads snapshot, and a later quality-gate extra COQL. Live Google Ads API on 20 Aug **failed** (`invalid_grant`). The controlling score is **five paid gclid people** in the 17–19 Aug PT window:

| Quality | Count | Meaning |
|---|---|---|
| `employer_probable` | 2 | Freeze these paths |
| `employer_not_a_fit` | 1 | Reconstruct only. Do not expand. |
| `spam_or_junk` | 2 | Ads-strong, CRM-junk. Do not freeze. |

**2 probable employers. Not 6 Ads conversions. Not 531 GA4 conversions.**

What this changes for planning:

- Do not rank keywords, RSAs, or LPs by CTR, impression share, or Ads conversion count.
- Do not treat “hiring” language as job-seeker by default. CRM decides.
- Do not treat a Broad real-estate click that produced a human form as a role to scale. Sales marked it Not a Fit.
- Do not roll `/us` back to the page version that happened to be live at convert time. That page is already superseded; rolling back is a product regression, not a reconstruction.
- Freeze is a **registry file**, not an Ads label (label was requested, not applied).
- Do not treat form + booked call as fake double-counting. None of these five booked a call (`Discovery_Call_Date` empty on all five). AU’s 4 vs 2 is a **different** problem: extra tags on one submit, not a form→Calendly path.

Owners (do not swap): Cheyenne Gichana = US. Holly Wallace = APAC / Australia. Caitlin is on maternity leave. Week = Monday–Sunday, 7 days.

---

## 2. Exact APIs, date ranges, timezones, success vs failure

### 2.1 What workers ran (20 Aug 2026)

| System | API / method | Window | Timezone | Result |
|---|---|---|---|---|
| Zoho CRM | v8 COQL `SELECT` — **1 call** | `2026-08-17T00:00:00-07:00` → `2026-08-21T00:00:00-07:00` (end exclusive) | Filter: America/Los_Angeles `Created_Time`. Record stamps are CRM local (treated as PT in the extract). | **Succeeded.** 29 leads in window. 5 with `utm_gclid`. Redacted extract: `xray/data/aug18-forensic-zoho.json` (generated 2026-08-20T10:41:47Z). |
| Zoho CRM extra | v8 COQL — **1 call** | Same window, paid gclid rows only | PT | **Succeeded.** File: `.local/zoho/quality-gate-extra-coql.json`. All 5: `Qualification_Status` empty, `Discovery_Call_Date` empty. Blueprint drift on US not-a-fit: `Lead_Status` = Decided Against / Not a Fit, `Blueprint_Lead_Status` = Junk Lead. Do not trust blueprint alone. |
| Google Ads (live, 20 Aug) | Intended read-only search / inspect | n/a | US account: America/Los_Angeles. AU account: Australia/Sydney. | **Failed.** Refresh token `invalid_grant`. Interactive reauth required in `~/Developer/shoutgeorge-ads`. **No API mutate attempted.** No retry loop. |
| Google Ads (existing snapshot) | Campaign metrics already on disk | Pull 2026-08-19T19:27:19Z. Campaign date range `2026-08-03` → `2026-08-19`. Frozen last-7 compare week **2026-08-10 → 2026-08-16**. | Account timezones as above. | **Succeeded earlier (19 Aug).** File: `xray/data/executive-snapshot.json`. **2 API calls** (US + AU), at the cap. Do not re-pull without George authorizing more. |
| Google Ads conversion actions | Read-only list (19 Aug) | Snapshot 2026-08-19T20:10:25Z | n/a | **Succeeded earlier.** File: `.local/ads/conv-actions-2026-08-19.json`. US customer `4967151855` (38 actions). AU customer `5735391940` (29 actions). |
| RSA / search-term review | Existing file, not a 20 Aug pull | Earlier launch / last-2 windows (predates some Aug 17–19 conversions) | n/a | Used as supporting inspect only: `ads-launch/_rsa_challenger_review.json`. Recruitment group already flagged job-seeker leakage. RSA review **excluded** `australia virtual assistant hiring` (word order A). File 02 negatives **`virtual assistant hiring in australia`** (word order B). They are not the same string. |
| 18 Aug US keyword inspect | Existing file | 2026-08-18 | n/a | `ads-launch/research/us-real-estate-account-inspect-2026-08-18.json` — confirms Exact+Phrase on `virtual assistant agency in usa` and Broad on `virtual assistant for real estate investors` in `Hire_VA_PH`. |
| GA4 Data API | `ga4_data_api` — 5 calls per property | `2026-08-17` → `2026-08-20` (property-local dates). Focus day 2026-08-18. | Property-local (US and AU properties separately). | **Succeeded.** File: `xray/data/aug18-forensic-ga4.json` (generated 2026-08-20T10:41:46Z). US property `549075481` / `G-2V3V0BS6JW`. AU property `549811743` / `G-7X1K9V2LFE`. |
| Landing-page git | Local git | Baseline `e03d1dd` = `baseline_v1_2026_08` shipped **2026-08-18 04:22 PT**. Stage1-v8 family through that commit. | PT | **Succeeded.** Two US paid forms at 02:19 and 04:06 PT hit **stage1-v8** (before baseline). AU SMM at 04:11 PT 19 Aug hit **baseline_v1_2026_08**. |
| Quality-gate proposal | Local write, read-only design | Same paid window | PT | `ads-launch/aug18-winners/ZOHO-QUALITY-GATE-PROPOSAL.md` + `.json`. Classification + future upload rules. **Uploads stay OFF.** No Zoho writes. No Ads setting changes. |
| Older US reconstruction | Contrast only | Ads last-7 complete days **10–16 Aug 2026** (snapshot generated 17 Aug). | Account TZ | `xray/docs/ads-launch/us-employer-conversion-reconstruction-2026-08-18.md`. **Not Aug 18 truth.** One unresolved US Ads conversion, likely 14 Aug. No keyword, no GCLID in CRM, action unnamed. |

### 2.2 Accounts

| Market | Ads customer | Stage 1 campaigns | Bidding on campaign objects (19 Aug snapshot) |
|---|---|---|---|
| US | `496-715-1855` | `VC_US_S_CORE` (`24117249292`), `VC_US_S_ROLES` | `TARGET_SPEND` (Maximize Clicks) |
| AU | `573-539-1940` | `VC_AU_S_CORE`, `VC_AU_S_ROLES` (`24117949196`) | `TARGET_SPEND` (Maximize Clicks) |

Snapshot narrative line (`conversions_note`) still says “US CORE/ROLES on Maximize Conversions.” That contradicts the campaign objects (`TARGET_SPEND`). Treat **TARGET_SPEND / Maximize Clicks as the snapshot’s campaign field**. Do not recommend switching to Maximize Conversions.

Operator budgets in the same snapshot (19 Aug): US **$250/day** (Core $150 + Roles $100). AU **A$125/day** (Core A$75 + Roles A$50). AU `cost_usd` in the JSON is **AUD** (account currency), not USD.

### 2.3 Timezone trap (AU Ads day ≠ PT calendar day)

- Zoho filter and US Ads day: **America/Los_Angeles** (PDT in August, UTC−7).
- AU Ads day: **Australia/Sydney** (AEST, UTC+10). AU 18 Aug Ads day overlaps **17 Aug PT afternoon/evening**.
- Both AU junk records created 17 Aug PT fall on **AU Ads calendar 18 Aug**:
  - AU-A17-02 `2026-08-17T15:28:22` PT → 08:28 AEST 18 Aug.
  - AU-A17-01 `2026-08-17T20:25:24` PT → 13:25 AEST 18 Aug.
- AU SMM AU-A19-01 `2026-08-19T04:11:28` PT → 21:11 AEST 19 Aug, matching AU by-date **1.0 conversion on 19 Aug**.

### 2.4 Zoho fields used (1 COQL call, then 1 extra)

First pull: `id, Created_Time, Region, Lead_Status, Lead_Source, Form_Source, Company, Job_Position_Required, utm_source, utm_medium, utm_campaign, utm_term, Campaign_Name, Website, Referrer, Referring_URL, Created_By, utm_gclid, Other_Client_Profile_Information`.

Extra pull (quality gate): `Qualification_Status`, `Discovery_Call_Date`, `Blueprint_Lead_Status` on the 5 paid rows.

Window quality counts (all leads, paid and unpaid): employer_progressed 11, employer_probable 8, spam_or_junk 6, employer_not_a_fit 2, unknown 1, internal_test 1. By region: AU 14, USA 14, blank 1. **Only the 5 gclid rows are the paid ledger.** Do not add organic/direct/ChatGPT/Zendesk rows to Ads path scores.

---

## 3. Full conversion ledger — one row per paid human journey

Source of truth: `xray/data/aug18-winning-paths.json` + `ads-launch/aug18-winners/winning-path-registry.json` (same content) joined to `xray/data/aug18-forensic-zoho.json`. No private note text. No raw GCLID. Extra COQL: no Discovery date, no Qualification_Status on any of these five.

### US-A18-01 — probable employer — **PROTECT**

| Field | Value |
|---|---|
| Ledger ID | US-A18-01 |
| Market | US |
| Zoho record ID | `6724032000029876002` |
| Created PT | 2026-08-18 04:06:18 |
| Search term | `virtual assistant agency in usa` |
| Keyword | `virtual assistant agency in usa` |
| Match | Exact **and** Phrase both Enabled in `Hire_VA_PH` (18 Aug inspect). **Click match type not in notes.** Ads API could not reconfirm 20 Aug. |
| Campaign | `VC_US_S_CORE` / `24117249292` |
| Ad group | `Hire_VA_PH` / `198704755323` (matches `utm_content`) |
| RSA IDs eligible | `820036923766`, `820036923769` (which RSA served is **unconfirmed**) |
| Final URL | `https://www.virtualcoworker.app/us` |
| LP version | `stage1-v8` |
| LP git | **pre-`e03d1dd`**. Baseline shipped 2026-08-18 04:22 PT. This lead is 16 minutes earlier. |
| Role requested | Administrative / virtual assistant |
| Category | administrative-support |
| Company present? | **No** |
| Company size | 1-10 |
| Form source | form |
| UTMs | google / cpc / 24117249292 / term = keyword |
| gclid | present (hash `a34d6cc7d7fb` — not the raw ID) |
| Referrer host | www.virtualcoworker.app |
| Zoho status | Attempted to Contact 2 (Auto) |
| Booked call? | **No** (`Discovery_Call_Date` empty) |
| Quality | `employer_probable` |
| Protect? | **Yes** |
| Why | Paid gclid form on `/us`. Employer-shaped role. Sales still working it. Not junk. Form without a booked call is still a real first step. |

### US-A18-02 — not a fit — **do not protect, do not expand**

| Field | Value |
|---|---|
| Ledger ID | US-A18-02 |
| Market | US |
| Zoho record ID | `6724032000029875002` |
| Created PT | 2026-08-18 02:19:01 |
| Search term | `virtual assistant for real estate investors` |
| Keyword | `virtual assistant for real estate investors` |
| Match | **BROAD** |
| Campaign | `VC_US_S_CORE` / `24117249292` |
| Ad group | `Hire_VA_PH` / `198704755323` |
| Final URL | `https://www.virtualcoworker.app/us` |
| LP version | `stage1-v8` |
| Role requested | Other / not sure |
| Company present? | **No** |
| Company size | 1-10 |
| Form source | form |
| UTMs | google / cpc / 24117249292 / term = keyword |
| gclid | present (hash `b359e1596d15`) |
| Zoho status | Decided Against / Not a Fit |
| Blueprint status | Junk Lead (disagrees with Lead_Status — do not trust blueprint alone) |
| Booked call? | **No** |
| Quality | `employer_not_a_fit` |
| Protect? | **No** |
| Why | Human path existed. Sales marked not a fit. Reconstruct only. Cheyenne 19 Aug: investor/wholesaler RE VA is often a poor fit. |

### AU-A17-01 — junk — **do not protect**

| Field | Value |
|---|---|
| Ledger ID | AU-A17-01 |
| Market | AU |
| Zoho record ID | `6724032000029868001` |
| Created PT | 2026-08-17 20:25:24 |
| Ads calendar | 17 Aug PT evening = **18 Aug AEST**. Inside AU Ads Aug 18 conversion day. |
| Search term reported | `virtual assistant hiring in australia` (Ads search term; RSA review already excluded a **different word order**: `australia virtual assistant hiring`) |
| Keyword | `australia virtual assistant` |
| Match relationship | Operator brief: exact close variant. **Ads API not live 20 Aug to reconfirm.** |
| Campaign | `VC_AU_S_ROLES` / `24117949196` |
| Ad group | `Recruitment_Hire_PH` / `199115615677` |
| Final URL | `https://www.virtualcoworker.app/au/recruitment` |
| LP version | `stage1-v8` |
| Role requested | Recruitment support |
| Company present? | **No** |
| Company size | 1-10 |
| Category | recruitment |
| Form source | form |
| UTMs | google / cpc / 24117949196 / term = `australia virtual assistant` |
| gclid | present (hash `d2e42ebca155`) |
| Zoho status | Junk Lead |
| Booked call? | **No** |
| Quality | `spam_or_junk` |
| Protect? | **No** |
| Why | Ads-strong, CRM-junk. Form defaulted to Recruitment support. No company. Do not freeze. |

### AU-A17-02 — junk — **do not protect**

| Field | Value |
|---|---|
| Ledger ID | AU-A17-02 |
| Market | AU |
| Zoho record ID | `6724032000029820005` |
| Created PT | 2026-08-17 15:28:22 |
| Ads calendar | Also **18 Aug AEST** (15:28 PT 17 Aug = 08:28 AEST 18 Aug). |
| Search term | **Not separately recorded** in the registry. Do not invent one. Keyword only. |
| Keyword | `australia virtual assistant` |
| Campaign | `VC_AU_S_ROLES` / `24117949196` |
| Ad group | `Recruitment_Hire_PH` / `199115615677` |
| Final URL | `https://www.virtualcoworker.app/au/recruitment` |
| LP version | `stage1-v8` |
| Role requested | Recruitment support |
| Company present? | **No** |
| Company size | 11-50 |
| Category | recruitment |
| gclid | present (hash `aa2706eebfa5`) |
| Zoho status | Junk Lead |
| Booked call? | **No** |
| Quality | `spam_or_junk` |
| Protect? | **No** |
| Why | Second junk on the same keyword → recruitment page. |

### AU-A19-01 — probable employer — **PROTECT**

| Field | Value |
|---|---|
| Ledger ID | AU-A19-01 |
| Market | AU |
| Zoho record ID | `6724032000029986002` |
| Created PT | 2026-08-19 04:11:28 |
| Ads calendar | 19 Aug AEST (and AU by-date 19 Aug = 1.0 conversion). |
| Search term | `hire a social media manager` |
| Keyword | `hire a social media manager` |
| Match | Phrase (`p`) |
| Device | Computer (`c`) |
| Campaign | `VC_AU_S_ROLES` / `24117949196` |
| Ad group | `Social_Media_Hire_PH` / `199115614717` |
| RSA IDs (do not edit) | `820329868079`, `820329868202` |
| Final URL | `https://www.virtualcoworker.app/au/social-media` |
| LP version | `baseline_v1_2026_08` |
| LP commit | `e03d1dd` |
| Role requested | Social media support |
| Category | social-media |
| Company present? | **Yes** (token `H…5` only) |
| Company size | 1-10 |
| Form source | form |
| UTMs | google / cpc / 24117949196 / term = keyword |
| gclid | present (hash `1658bd61244b`) |
| Zoho status | Information Brochure Sent |
| Booked call? | **No** (`Discovery_Call_Date` empty) |
| Quality | `employer_probable` |
| Protect? | **Yes** |
| Why | Paid gclid. Role matches page. Company present. Holly working it (brochure). Query → role ad group → role LP aligned. Form without a booked call is still the clean structural win. |

**That is the entire paid-person ledger. Five rows. Do not add the other 24 Zoho rows in the window** (organic Google, direct, ChatGPT, Zendesk, referral, job-order forms without gclid, API test). Those are real people in some cases; they are not paid-path evidence.

---

## 4. Paths investigated

Two paths were the original investigation targets. Two more paid paths appeared in the same Zoho pull. All four are below. Only two are frozen.

### 4.1 AU recruitment (original target) — Ads winner, CRM junk

**Path:** generic VA + country keyword `australia virtual assistant` in `VC_AU_S_ROLES` / `Recruitment_Hire_PH` → Final URL `/au/recruitment` → two Junk Lead records (`6724032000029868001`, `6724032000029820005`).

**Why Ads liked it (pre-Zoho):**

- RSA review on `Recruitment_Hire_PH`: launch CTR **17.9%** (123 impr / 22 clicks / A$83.53) with **0.0 Ads conversions in that review window**. Status was “leave — insufficient evidence.” Replacement hint already said: watch job-seeker leakage (`australia virtual assistant hiring`). Negatives were out of scope in that RSA pass.
- Search terms already **EXCLUDED** in that review: `australia virtual assistant hiring` (6/4, A$14.49), `australia va hiring` (9/3, A$11.02). Still **NONE** (not excluded): `australia virtual assistant` (3/1), `australia va agency` (3/1).
- AU account **18 Aug** (Sydney day): **4.0 Ads conversions**, 167 impr, 40 clicks, A$127.46, CTR 23.95%. That is the Ads-loud day.

**AU 4 Ads vs 2 junk Zoho people — refined reading (do not call this “fake form+call”):**

| Reading | Apply here? |
|---|---|
| **(a) Form + Calendly / booked call** = one human, two legitimate funnel steps | **No.** Extra COQL: `Discovery_Call_Date` empty. Status is Junk Lead, not Discovery Scheduled. They did not book a call. |
| **(b) Form + thank-you + qualify + close on the same submit** = possible extra tags, one action family | **Likely.** 4 Ads events vs 2 junk humans, no booked call. Best available explanation. |
| Four employers | **No.** |

**Honesty about proof:** Ads OAuth was down on 20 Aug. Workers could **not** name which conversion **action names** fired for the AU 4.0. The stack (thank-you / qualify / close) is inferred from the 19 Aug action inventory + the 4-vs-2 gap. Do not treat that inference as a live action-by-day report. Do not change conversion settings to “fix” it in this pass.

**Why Zoho killed the path:** both records Junk Lead, role “Recruitment support,” no company. See §5.

**Action taken (Editor CSV only, not Posted):** file `02-au-recruitment-junk-reversible.csv` — pause Exact `australia virtual assistant`; Exact negative `virtual assistant hiring in australia` on that ad group only. Campaign stays Enabled. `Social_Media_Hire_PH` not touched.

### 4.2 US real estate (original target) — human path, not a winner

**Path:** Broad `virtual assistant for real estate investors` in `VC_US_S_CORE` / `Hire_VA_PH` → `/us` (generic, not `/us/real-estate`) → Zoho `6724032000029875002` → Decided Against / Not a Fit.

Landed on generic `/us` at 02:19 PT 18 Aug, stage1-v8. Role on the form: “Other / not sure.” No company. Size 1-10. No booked call.

**Cheyenne 19 Aug (sales context, not a quote of private notes):** investor/wholesaler real-estate VA is often a **poor fit** for this offer.

**Reconstruct only. Do not expand.** Do not post `ads-launch/real-estate-2026-08-18/` (a prior Editor package that would add investor AGs, Exact/Phrase/Broad copies, and later pause the original Broad). Do not treat `/us/real-estate` GA4 sessions as this conversion — this click’s Final URL was `/us`. Do not pause the Broad yet (n=1). Do not build a role group from one Not a Fit.

18 Aug inspect also showed the same Broad Enabled in `Hire_VA_PH_offer_LP`. The converting form’s `utm_content` is `198704755323` (`Hire_VA_PH`). Offer-LP is **not** a confirmed converting path. Live status on 20 Aug could not be reconfirmed (Ads OAuth down).

### 4.3 US agency (found in the same pull) — probable winner — **FROZEN**

**Path:** `virtual assistant agency in usa` (search term = keyword) in `Hire_VA_PH` → `/us` → Zoho `6724032000029876002` → Attempted to Contact 2 (Auto) → `employer_probable`.

This was **not** one of the two originally named investigation targets. It is the US paid employer-shaped row. Exact + Phrase both Enabled. Click match type unknown. No company on the form; role is still employer-shaped (Administrative / virtual assistant). Sales still working it. No booked call yet — still protect the path. The missing call makes it a weaker funnel, not a fake lead.

**Freeze:** do not pause, rematch, negative-block (anything containing `agency in usa`), move, edit RSA, change Final URL, substantially edit `/us`, or change bidding on this group during the freeze.

`/us` is now live as `baseline_v1_2026_08` (`e03d1dd`). **Do not roll back to stage1-v8** even though that was the converting page.

### 4.4 AU social media (found in the same pull) — probable winner — **FROZEN**

**Path:** Phrase `hire a social media manager` in `Social_Media_Hire_PH` → `/au/social-media` → Zoho `6724032000029986002` → Information Brochure Sent → `employer_probable`. Company present. Role matches page. Holly working it. No booked call yet.

This is the clean structural win: **role query + role ad group + role landing page**.

RSA review on this group (earlier window) had almost no volume (14 impr / 1 click / A$3.70, 0 conv) and had **not** yet seen this 19 Aug conversion. Phrase keyword existed with 2 impr / 0 clicks in that review. Do not use the old RSA-review “leave / low volume” status to unfreeze it now.

File `03-au-smm-exact-enable.csv` would add/enable Exact of the converting Phrase, keep Phrase, same Final URL, no RSA edits. **It waits.** Do not import it in the same pass as file 02.

---

## 5. Why AU recruitment looked like a winner in Ads and was junk in Zoho

Stack the two pictures. Do not reconcile them by inventing “they were job seekers” unless CRM said so. CRM said **Junk Lead**. Twice.

### What Ads saw

- High CTR on a recruitment-themed ad group (RSA review 17.9% launch CTR).
- AU 18 Aug account day: 4.0 conversions, 23.95% CTR — the loudest AU Stage 1 conversion day in the snapshot.
- Keyword `australia virtual assistant` can close-variant to generic “hiring in Australia” queries (operator brief; not reconfirmed live 20 Aug).
- Landing page `/au/recruitment` is a real employer-looking page (recruiting/TA RSA copy: “Hire Recruitment Assistant,” “For Australian employers…”). CTR and message-match can look excellent while the **people** are junk.

### What the form did (structural, not a guess about the humans)

`/au/recruitment` is a role landing page. The role chip / `formLabel` for that category is **“Recruitment support”** (`vision/config/guided-match.ts`, `vision/config/categories.ts`). Both junk records stored `Job_Position_Required` = “Recruitment support.” That is the **page default**, not independent proof that two employers asked for TA/recruiting staff.

### What CRM recorded

| Record | Role on form | Company | Size | Status | Booked call |
|---|---|---|---|---|---|
| `6724032000029868001` | Recruitment support | No | 1-10 | Junk Lead | No |
| `6724032000029820005` | Recruitment support | No | 11-50 | Junk Lead | No |

No company on either. Sales (Holly’s market) marked both junk.

### What not to conclude

- **Do not assume “hiring” = job seeker.** The reported search term `virtual assistant hiring in australia` is generic. It can be an employer or a candidate. The **CRM** decided junk. That is the score.
- **Do not assume the recruitment LP is broken** and rewrite it. The failure is **query → wrong role bucket → defaulted role field → junk people**. File 02 pauses the generic keyword and negatives the demonstrated junk term. It does not edit the LP.
- **Do not copy this structure:** generic VA + country + hiring language → recruitment LP. That is the anti-pattern (§9).
- **Do not treat 4 Ads conversions as 4 people.** Two junk humans.
- **Do not treat those 4 as form + booked call.** They did not book. If the extra Ads counts are real, they are reading **(b)** (same-submit extra tags), not reading **(a)** (legitimate two-step funnel).
- **Do not “fix” measurement by turning on Maximize Conversions or offline uploads.** Observe. Clean later with approval.

RSA review had already excluded `australia virtual assistant hiring` (word order A). The demonstrated junk search term in the registry is `virtual assistant hiring in australia` (word order B). File 02 negatives **B** as Exact. Do not assume A and B are covered by one negative unless match type / close-variant behavior is reconfirmed after Ads reauth.

---

## 6. US real estate — reconstruct only

This is a complete reconstruction of **one** paid journey. It is not a role thesis.

1. Query / keyword: `virtual assistant for real estate investors` (Broad).
2. Ad group: `Hire_VA_PH` (generic hire-VA, not a real-estate group).
3. Final URL: `https://www.virtualcoworker.app/us` — **not** `/us/real-estate`.
4. LP: stage1-v8, 02:19 PT 18 Aug (before baseline ship).
5. Form role: Other / not sure. No company. Size 1-10.
6. Zoho: `6724032000029875002`, Decided Against / Not a Fit.
7. Sales context (Cheyenne, 19 Aug): investor/wholesaler RE VA is often a poor fit.
8. No booked call.

**Do not:** expand real estate; post the 18 Aug real-estate Editor package; move this keyword to `/us/real-estate`; treat GA4 `/us/real-estate` sessions (2 sessions / 23 “conversions” on 18 Aug — those “conversions” are page_view/engagement, not forms) as this lead; pause the Broad on n=1; freeze it as a winner.

**Do:** leave the Broad Enabled for now; keep it out of the protect list; if a second paid RE row appears, re-score from Zoho status, not from Ads.

---

## 7. Confirmed / probable / unconfirmed — what is frozen

Workers are using **probable**, not “confirmed closed-won.” Neither protected row is a job order or a placement. Neither booked a discovery call. “Confirmed” in the requested label name is aspirational. The freeze is still correct: do not disturb the only two paid employer-shaped paths.

### Frozen (probable winners)

| ID | Path | Evidence | Freeze mechanism |
|---|---|---|---|
| PROTECT-US-AGENCY | `Hire_VA_PH` · `virtual assistant agency in usa` Exact+Phrase · `/us` | Zoho `6724032000029876002` employer_probable, sales working | Registry + `01-do-not-touch.md`. Ads label **not** applied. |
| PROTECT-AU-SMM | `Social_Media_Hire_PH` · `hire a social media manager` Phrase · `/au/social-media` | Zoho `6724032000029986002` employer_probable, brochure sent, company present | Same. |

Live LPs for both: `baseline_v1_2026_08` (`e03d1dd`). Do not roll `/us` back. Do not substantially edit `/us` or `/au/social-media`. Do not edit enabled RSAs in `Hire_VA_PH` or AU social `820329868079` / `820329868202`.

### Not frozen

| Path | Why |
|---|---|
| `Recruitment_Hire_PH` / `australia virtual assistant` → `/au/recruitment` | Two Junk Leads. Ads 4.0 is not four people and is not form+call. |
| Broad `virtual assistant for real estate investors` → `/us` | One human, Not a Fit. |

### Unconfirmed / not in this ledger

- The **14 Aug** US Ads 1.0 conversion (`us-employer-conversion-reconstruction-2026-08-18.md`): campaign `VC_US_S_CORE`, likely 14 Aug, action unnamed, no ad group/keyword/search term, Final URL not proven, **0 GCLID in that week’s CRM census**, GA4 `employer_inquiry_submitted` = 0 for 6–17 Aug. Classification **unresolved**. Not a reason to touch `/us`. Not Aug 18 truth.
- Organic/direct/ChatGPT US and AU employers in the same Zoho window (Discovery Scheduled, Job Order Submitted, etc.). Real sales work. **Not paid-path winners.** Window Discovery Scheduled rows that exist are **organic/direct, no gclid** — do not mix them into paid booked-call counts.
- Which Exact vs Phrase served US-A18-01.
- Which Hire_VA_PH RSA served US-A18-01.
- AU-A17-02 search term (only keyword known).
- Live 20 Aug Enabled/Paused state of every keyword (OAuth down). Freeze is “do not change,” not “we re-read live inventory today.”
- **Which Ads action names** made the US 2.0 and AU 4.0. Not proven live. US 2.0 matches 2 Zoho people 1:1 (so those two fires are consistent with one event per person). AU 4.0 vs 2 people is the unresolved stack.

---

## 8. Protect label `PROTECT_CONFIRMED_WINNER_AUG18` was **not** applied

Requested. Not applied.

**Blocker:** Google Ads OAuth refresh token `invalid_grant`. Interactive reauth is required in the personal MCC toolkit (`~/Developer/shoutgeorge-ads`, gitignored `.env`). Workers did **not** attempt an Ads mutate. They did not retry.

**The freeze is the registry**, not an in-account label:

- `ads-launch/aug18-winners/winning-path-registry.json`
- `ads-launch/aug18-winners/01-do-not-touch.md`
- `xray/data/aug18-winning-paths.json` (X-ray copy)

Applying the label later requires: (1) George reauth, (2) George approval to mutate labels only, (3) still no campaign/ad/keyword create-update-enable-pause via API. Editor remains the write path.

Until then, any agent that “cleans up” Hire_VA_PH or Social_Media_Hire_PH is violating the freeze even if the UI shows no protect label.

---

## 9. Transferable structural reasons (not headline-level asset winners)

Do **not** promote individual RSA headlines from the converting ads as “winners.” RSA review asset labels were NOT_APPLICABLE; conversion-attributed assets were empty in that file. The transferable facts are **path structure**:

1. **Role-specific query + role ad group + role landing page** (AU social media). This is the cleanest paid employer path in the window.
2. **Employer shopping language:** `agency`, `hire a [role]` — not generic `virtual assistant` + country + `hiring`.
3. **Company present** on the better AU lead; **missing** on both junk rows and the Not a Fit. Not a law, but a quality correlate. Cheyenne has already asked for company-name required on forms. Do **not** rebuild `/us` in this pass to add it.
4. **Anti-pattern:** generic VA + country + hiring → recruitment LP → form defaults to “Recruitment support” → junk/no-company records. Do not copy that structure to US or to other role pages.
5. **Generic `/us` can still produce an employer-probable lead** when the **query** is agency/employer. That does not make `/us` a scored LP winner and does not justify rolling it back to stage1-v8.
6. **Broad industry query on a generic hire group** can produce a human who is not a fit (US RE). Volume ≠ quality.
7. **Form then booked call is the stronger paid outcome** — once Zoho says employer. None of the five paid rows reached that second step. Do not wait for a booked call before freezing a probable-employer form path. Do not treat a later booked call on a junk/job-seeker row as an employer conversion.

---

## 10. Spend-only areas (19 Aug snapshot) — numbers

Source: `xray/data/executive-snapshot.json` generated 2026-08-19T19:27:25Z. Campaign `last_7_days` = frozen week **10–16 Aug 2026** (matches `compare_7v7.last_7`). Impression-share lines in `operator.insights` use the same week.

These areas spent. They did **not** produce the two probable Aug 17–19 employers (those sit on CORE hire-VA + AU ROLES SMM, and the AU 18 Aug Ads conversions on ROLES were junk people).

| Area | Spend (frozen week 10–16) | Clicks | Impr | CTR | Avg CPC | Ads conv in that week | Search IS / lost rank / lost budget |
|---|---|---|---|---|---|---|---|
| `VC_US_S_CORE` | **$874.66** (~$875) | 342 | 2680 | 12.76% | $2.56 | **1.0** (the older unresolved ~14 Aug row — not Aug 18) | IS 29.9% · lost rank 37.8% · lost budget 32.2% |
| `VC_US_S_ROLES` | **$565.07** | 151 | 1838 | 8.22% | $3.74 | **0** (no conversions field) | IS 22.3% · lost rank 56.1% · lost budget 21.6% |
| `VC_AU_S_CORE` | **A$536.75** (~A$537) | 161 | 1049 | 15.35% | A$3.33 | **0** | IS 33.6% · lost rank 39.5% · lost budget 27.0% |
| `VC_AU_S_ROLES` | **A$347.44** | 89 | 876 | 10.16% | A$3.90 | **0 in frozen week** (no conversions field). Aug 18–19 conversions sit **outside** this week. | IS 27.0% · lost rank 49.1% · lost budget 24.0% |

**US Stage 1 last 7 (10–16):** $1,439.73 · 493 clicks · $2.92 CPC · 1.0 Ads conversion.  
**AU Stage 1 last 7 (10–16):** A$884.20 · 250 clicks · A$3.54 CPC.

**Aug 18 by-date (click date, account TZ) — the loud day:**

| Market | Impr | Clicks | CTR | Spend | Ads conv | People (Zoho gclid) |
|---|---|---|---|---|---|---|
| US | 594 | 64 | 10.77% | $161.98 | **2.0** | **2** (1 probable + 1 not-a-fit). 1:1. Not a duplication problem. |
| AU | 167 | 40 | 23.95% | A$127.46 | **4.0** | **2 junk**. Not four people. Not form+call. Likely reading (b): extra tags on the same submit. Action names **not proven** (OAuth down). |

**Aug 19 by-date:** US $43.67 / 15 clicks / 0 conv listed. AU A$48.91 / 13 clicks / **1.0** conv (aligns with AU-A19-01). AU ROLES focus-day object: 7 clicks, A$28.35, **1.0** conversion.

Closest structural model for the spend-only areas (not an instruction to rebuild them this pass): keep the US agency keyword; do not chase RE Broad; AU SMM = role query → role LP; AU CORE should learn employer/agency language, not generic VA → recruitment.

Lost IS (rank) is the bigger auction hole vs budget on Roles especially. That is **not** a reason to raise budgets or switch to Maximize Conversions.

---

## 11. What was implemented (Editor CSV only — not Posted)

Nothing was written to Google Ads via API. No LP code edit. No bid, budget, RSA, or Final URL change on protected paths. No Zoho writes. Offline uploads stay **OFF**.

| Date | Change | Why | Derived from | Revert |
|---|---|---|---|---|
| 2026-08-20 | Registry freeze of US agency + AU SMM | Human CRM probable employers | Zoho `6724032000029876002`, `6724032000029986002` | Delete / ignore registry |
| 2026-08-20 | Editor CSV **file 02**: pause `australia virtual assistant` Exact in `Recruitment_Hire_PH`; Exact negative `virtual assistant hiring in australia` on that ad group | Two Junk Leads; demonstrated junk search term | AU-A17-01 / AU-A17-02 | Set keyword Enabled; remove negative |
| 2026-08-20 | Editor CSV **file 03**: Exact `hire a social media manager` Enabled in `Social_Media_Hire_PH` | Controlled Exact of converting Phrase | AU-A19-01 | Pause the Exact; leave Phrase |
| 2026-08-20 | X-ray page `xray/aug18-conversions.html` + Checklist “Do this today” | Operator scoreboard | — | Unpublish if needed |
| 2026-08-20 | `ZOHO-QUALITY-GATE-PROPOSAL.md` + `.json` | Classification + Max Conv readiness. Report only. | Extra COQL + conv-action inventory | Ignore the proposal |

**Import order (Australia account `573-539-1940` only), when George chooses to Post:**

1. Editor → Australia → Get recent changes.
2. Import `ads-launch/aug18-winners/02-au-recruitment-junk-reversible.csv` as Keywords / Keywords, Negative.
3. Review: **two rows**, both `Recruitment_Hire_PH`. Campaign status must stay **Enabled**.
4. Post **that file only**.
5. **Stop.** File 03 waits.

Do not import the big Stage 1 packages. Do not touch US in this pass. File 02 comments use label `VC_AUG18_LEARN_2026-08-20`. File 03 comment: keep Phrase; same Final URL `/au/social-media`; do not edit RSAs.

**Not implemented (needs George approval):**

- Ads label `PROTECT_CONFIRMED_WINNER_AUG18` (needs reauth).
- Pause Broad `virtual assistant for real estate investors`.
- Budget move AU CORE → AU social / US agency.
- Maximize Conversions — **neither market ready** (§12.3).
- Conversion-action Primary cleanup (US GA4 page_view etc. firing as conversions).
- Offline conversion uploads (proposal only; gate stays OFF).
- Company-name required on forms (Cheyenne already asked; do not rebuild `/us` in this pass).
- Posting file 03.
- Creating `VC_Inquiry_Class` in Zoho (proposal only; no writes).

---

## 12. Conversion measurement

### 12.1 George’s rule (binding)

| Rule | Meaning |
|---|---|
| Form + booked call | **One human, two funnel steps.** Stronger if they booked. **Not** automatic duplicate tracking. |
| When to flag duplication | Only if the **same** action fires repeatedly with **no** distinct user action. |
| Best path | Ad click → employer form → booked call. |
| Booked call as employer outcome | Only **after** Zoho classifies the record as employer. Junk / job-seeker / test / unknown + a booked call is **not** an employer conversion. |
| Offline uploads | **OFF.** Do not activate. |
| Maximize Conversions | **No.** Score AU and US separately. Neither is ready while biddable actions mix junk. |

### 12.2 The three numbers (do not mix)

| System | Number | What it actually is |
|---|---|---|
| Ads 18 Aug click date | **2 US + 4 AU = 6** | Conversion-action fires. |
| US 2.0 vs Zoho | **2 people** | 1 probable + 1 not-a-fit. **1:1.** Not a duplication problem. Neither booked a call. |
| AU 4.0 vs Zoho | **2 junk people** | **Not four people.** **Not reading (a)** (form + Calendly). **Likely reading (b)** (form + thank-you + qualify + close on the same submit). Action names **unproven** — Ads OAuth down. |
| Zoho paid people 17–19 PT | **5** | 2 probable + 1 not-a-fit + 2 junk. **0 booked calls.** **Controlling number.** |
| US GA4 18 Aug “conversions” | **531** | `page_view` 202 + `user_engagement` 136 + `session_start` 83 + `first_visit` 58 + `scroll` 50 + `form_start` 2. Those events are marked as conversions on the US property. **Not 531 people.** |
| US GA4 18 Aug real form signal | **`form_start` = 2** | Aligns with two US paid forms. |
| AU GA4 18 Aug conversions | **0** | Same event types exist (`form_start` = 2) but are **not** marked as conversions on the AU property. |

US GA4 18 Aug: 82 sessions / 67 users / 100% engagement rate (because engagement events are the “conversion” definition). Do not use that engagement rate as LP quality.

### 12.3 Ads conversion-action inventory (19 Aug read-only) + Max Conv readiness

US names include (among 38): `VC_US_Thank_You`, `VC_US_Phone_Click_Website`, `VC_US_Phone_Call_From_Ads`, `VC_US_Phone_Call_From_Website`, `VC_US_Calendly_Booked`, plus GA4-linked `VC US — virtualcoworker.app (web) page_view`, `session_start`, `user_engagement`, `first_visit`, `scroll`, `form_start`, `qualify_lead`, `close_convert_lead`, and older `virtualcoworker.com - GA4 (web) page_view`. Zoho upload actions exist (`Zoho Discovery Scheduled US`, `Zoho JO Submitted US`, Original + Standard OCI) — all sampled upload rows have `include_in_conversions_metric: false` and `primary_for_goal: false`. **Leave them Secondary. Do not start uploads.**

AU names include: `VC_AU_Thank_You`, phone click / call / 1300, Calendly, plus Zoho Discovery/JO uploads (also `include_in_conversions_metric: false` on the sampled upload rows). One hidden UA leftover (`Job order form filled out`) still shows `primary_for_goal: true` / `include_in_conversions_metric: true` in the 19 Aug file — leftover, not a reason to mutate now.

**Currently Primary (`primary_for_goal` true) — do not mutate:**

- **US Enabled:** `VC_US_Thank_You`, `VC_US_Calendly_Booked`, `VC_US_Phone_Call_From_Ads`, `VC_US_Phone_Call_From_Website`, `VC_US_Phone_Click_Website`. Leftover in Conversions column: hidden `eBook Download`.
- **AU Enabled:** `VC_AU_Thank_You`, `VC_AU_Calendly_Booked`, `VC_AU_Phone_Call_From_Ads`, `VC_AU_Phone_Click_Website`, `Call (1300 886 740)`. Leftovers: hidden UA goals (Chat, Submission ×2, Job order form, Lead Form Submit Completion, Transactions).

These website Primaries fire on any form or booking. They do **not** wait for Zoho class. That is why they mix employer + junk.

**Maximize Conversions — evaluate separately. Do not switch. Neither is ready.**

| Meter (paid gclid, 17–20 Aug PT) | US (Cheyenne) | AU (Holly) |
|---|---|---|
| Human inquiries | 2 | 3 |
| Qualified employers | 0 | 0 |
| Probable employers | 1 | 1 |
| Not a fit / junk | 1 not-a-fit | 2 junk |
| Booked employer calls | 0 | 0 |
| Ready for Maximize Conversions? | **No.** Two people. One good form, no booked call. Not a bidding sample. | **No.** Ads 4 on 18 Aug were junk people, not employers. Opposite of ready. Australia is **not** first. |

**Safe to bid on now:** none of the website Primary stack.  
**Unsafe:** Thank_You, Calendly (until after employer class), phone click, GA4 page_view / engagement / session_start, hidden UA leftovers, qualify/close on the same submit.  
**Future (uploads still OFF):** Zoho-gated Qualified Employer + booked call or Job Order — only after n is real and George says uploads on.

Preserve separate configured values `VC_*_Thank_You` and `VC_*_Calendly_Booked`. Do not collapse them into one “conversion” in planning talk. They are two steps of one person when both fire from real actions.

**Do not change conversion settings in this pass.**

**Recommended future Primary (planning only, George approval later):** bid only after a **Zoho-gated** employer outcome exists (Qualified Employer + booked call or Job Order). Until then stay Maximize Clicks. Website thank-you can stay a counted first step; it must not become the Maximize Conversions target while it still fires on junk. Phone click stays **Secondary** when that cleanup happens. GA4 `page_view` / `session_start` / `user_engagement` / `first_visit` / `scroll` must **never** be Primary. Job seekers never count — even with a booked call.

### 12.4 Quality-gate proposal (report only — writes OFF)

Source: `ads-launch/aug18-winners/ZOHO-QUALITY-GATE-PROPOSAL.md`.

Zoho cannot classify every inquiry reliably today. `Lead_Status = Resume` is **0 all-time**. There is no working job-seeker field. `Qualification_Status` unused. Junk Lead may mix spam and seekers. No ad-group field (`utm_content` is the proxy).

Proposed later (do not write now): picklist `VC_Inquiry_Class` on Sales Enquiries — Qualified Employer / Probable Employer / Job Seeker / Spam / Internal Test / Unknown. Do **not** overload `Lead_Status` (that is sales cadence).

**Future upload eligibility (OFF):** all of: class = Qualified Employer, `utm_gclid` present, outcome = Discovery Scheduled or Job Order Submitted **after** employer class. Never upload Job Seeker (even with a booked call), Spam, Internal Test, Unknown, or Probable.

A job seeker who beats the website form still enters Zoho. Sales must mark them Job Seeker. That row must never become a qualified-employer conversion sent back to Google Ads.

---

## 13. Uncertainties / what Ads API could not reconfirm live (20 Aug)

Because OAuth was revoked, workers could not live-confirm:

- Click match type for US-A18-01 (Exact vs Phrase).
- Which RSA served either US form.
- Whether `australia virtual assistant` → `virtual assistant hiring in australia` is still classified as exact close variant.
- Current Enabled/Paused/negative inventory (file 02 not Posted; 18 Aug inspect may be stale).
- Whether `Hire_VA_PH_offer_LP` still has duplicate agency + RE keywords Enabled.
- **Which Ads conversion action names fired for the 2+4 on 18 Aug** (thank-you vs qualify vs close vs phone vs Calendly). This is the honesty line on AU 4.0: reading (b) is the best explanation, not a named-action proof.
- Impression/click/cost at keyword grain for 18 Aug.
- Whether the 14 Aug US 1.0 and the 18 Aug US 2.0 share any action.

RSA review conversion columns for these converting keywords were **0** because that file’s windows mostly predate the 17–19 Aug CRM people. Do not treat RSA-review 0 conv as contradiction of Zoho.

AU-A17-02 search term is unknown. Company names are tokens only. Quality labels are worker-applied from Zoho status + structure, not a sales-written “employer_probable” field.

What workers **could** prove without Ads: five paid Zoho people, their statuses, empty Discovery dates, empty Qualification_Status, and the 4-vs-2 / 2-vs-2 count gaps from the 19 Aug Ads snapshot.

---

## 14. Recommendations that require George approval

Workers must not do these without an explicit OK in a later conversation:

1. **Reauth Google Ads OAuth** in `shoutgeorge-ads`, then optionally apply label `PROTECT_CONFIRMED_WINNER_AUG18` (label-only; still no API inventory mutate).
2. **Post file 02** in Google Ads Editor (Australia only). This is the one cleanup that is already built and reversible. Checklist already lists it as today’s job.
3. **Post file 03** (AU SMM Exact) — after 02 posts clean, not in the same breath.
4. **Pause** Broad `virtual assistant for real estate investors` — not yet; n=1 Not a Fit.
5. **Budget move** from AU CORE toward AU social, or toward US agency — not yet; n=2 probable employers.
6. **Maximize Conversions** — no. Neither market. Actions mix junk.
7. **Offline uploads** — no. Proposal only.
8. **Conversion Primary cleanup** — later; do not do it in this pass. When done: do not punish form+call as “duplicates”; demote page_view/engagement; keep phone Secondary; never bid on actions that fire on junk.
9. **Company-name required** on forms — Cheyenne already asked; do not rebuild `/us` to do it in this freeze.
10. **Any `/us` or `/au/social-media` rewrite**, RSA edit, match-type change, or negative that could block `agency in usa` or `hire a social media manager`.
11. **Post** `ads-launch/real-estate-2026-08-18/` or any RE expansion.
12. **Create `VC_Inquiry_Class` in Zoho** — proposal only; no writes.

Planner may sequence these. Planner may not instruct workers to execute 4–12 as if they were already approved.

---

## 15. Monitoring plan

**Score = new Zoho gclid rows + Lead_Status (+ booked-call date if filled). Not Ads conversion count. Not GA4 conversions.**

1. **After file 02 Posts (if George Posts):** confirm `Recruitment_Hire_PH` has `australia virtual assistant` Paused, Exact negative present, **campaign still Enabled**, `Social_Media_Hire_PH` untouched, US untouched.
2. **Paid-person watch (17 Aug PT onward, then rolling):** any new `utm_gclid` + `utm_medium=cpc` row. Log ledger_id, record ID, keyword, LP, status, company yes/no, booked-call yes/no, quality. Add to the registry only if quality is employer_probable or better **and** George agrees to freeze.
3. **Protected-path health:** US-A18-01 (`6724032000029876002`) and AU-A19-01 (`6724032000029986002`). Status progression (contacted → brochure/discovery → JO) is success. A later booked call on these two would make them **stronger**, not “duplicate.” New junk/not-a-fit on those **exact queries** would weaken the freeze — re-score, don’t silently unfreeze.
4. **Recruitment leak:** if another junk lands on `/au/recruitment` from a **new** generic VA+country term, propose an Exact negative (George approval). Do not pause the whole recruitment ad group on this sample.
5. **RE Broad:** leave Enabled. If a second paid RE row appears, score from Zoho. Two Not-a-Fits would make a pause discussable. One employer_progressed would reopen expansion — still George approval, still no surprise Post of the old RE package.
6. **Measurement hygiene (observe only):** US GA4 will keep reporting hundreds of “conversions.” Ignore them. Watch `form_start`, Zoho forms, and `Discovery_Call_Date`. After Ads reauth, a cheap read-only conversion-action report (George-authorized call budget) can name which actions made the 2+4. Do not paginate the account. Do not treat form+Calendly as a bug if both fire from real user actions.
7. **Do not** pull Ads API in a loop, raise `GOOGLE_ADS_ACCESS_LEVEL`, or treat `RESOURCE_EXHAUSTED` as retryable.
8. **Executive page:** stay a neutral US/AU scoreboard. Do not put “watch / may be paid / organic is actually ads” copy on Executive.

---

## 16. Do not tell George to do (hard list for the planner)

ChatGPT must **not** instruct George or workers to:

1. **Lecture or prioritize Brand.** Brand is deferred. Whatever is still Enabled in the Ads UI is obvious to George. Do not probe Brand spend. Do not put Brand on the checklist.
2. **Mutate Google Ads via API** (create/update/enable/pause campaigns, ad groups, ads, keywords, budgets, bids, labels except the later approved protect-label after reauth). No “cleanup.” No pagination of full inventory. Cap 1–2 read-only calls unless George authorizes more. On `RESOURCE_EXHAUSTED`, stop.
3. **Use Cursor Cloud / move the agent to Cloud.** Work stays on this Mac. Cloud cannot see `.env`, Editor, Gmail, or local Ads toolkit.
4. **Recommend, switch to, or push Grok** (or any specific model). Leave Cursor on Auto.
5. **Switch bidding to Maximize Conversions** (or Maximize Conversion Value). Campaigns are `TARGET_SPEND` / Maximize Clicks. Measurement still mixes junk. Optimizing to page_view or junk stacked actions would burn money. AU is not “ready first.”
6. **Activate offline uploads** or turn `ZOHO_CRM_ENABLED` on.
7. **Treat form + booked call as duplicate tracking.** It is one person, two steps. Only flag the same action firing on repeat with no extra user action.
8. **Treat a booked call as an employer win** before Zoho says employer.
9. **Roll `/us` back to stage1-v8** (or any earlier family). The converting US forms hit stage1-v8; the live page is `baseline_v1_2026_08`. Fix forward only. The 14 Aug reconstruction also forbids treating an older page as a scored winner.
10. **Post the big Stage 1 Editor packages** or the `ads-launch/real-estate-2026-08-18/` expansion in the same breath as this cleanup.
11. **Import file 03** until file 02 has Posted clean.
12. **Change conversion settings now** (Primary/Secondary, import goals, GA4-linked page_view). Observe; clean later with approval.
13. **Assume hiring-language queries are job seekers** without CRM status. CRM decides junk vs employer.
14. **Expand real estate** from US-A18-02. Reconstruct only.
15. **Pause the RE Broad on n=1.**
16. **Raise budgets** because lost IS (rank) is high.
17. **Edit RSAs, match types, or Final URLs** on the two frozen paths.
18. **Put “watch / may be paid” copy on Executive.**
19. **Swap Cheyenne (US) and Holly (AU).**
20. **Ask George to run APIs or become the forensic worker.** Workers already pulled. Planner plans.
21. **Invent private lead details** (email, phone, company name, notes). Use record IDs.

---

## Source files (absolute, local)

- `xray/data/aug18-winning-paths.json`
- `ads-launch/aug18-winners/winning-path-registry.json`
- `ads-launch/aug18-winners/01-do-not-touch.md`
- `ads-launch/aug18-winners/CHANGELOG.md`
- `ads-launch/aug18-winners/README.md`
- `ads-launch/aug18-winners/02-au-recruitment-junk-reversible.csv`
- `ads-launch/aug18-winners/03-au-smm-exact-enable.csv`
- `ads-launch/aug18-winners/ZOHO-QUALITY-GATE-PROPOSAL.md`
- `ads-launch/aug18-winners/ZOHO-QUALITY-GATE-PROPOSAL.json`
- `xray/aug18-conversions.html`
- `xray/launch-control.html` (Checklist “Do this today”)
- `xray/data/aug18-forensic-zoho.json`
- `xray/data/aug18-forensic-ga4.json`
- `xray/data/executive-snapshot.json`
- `.local/ads/conv-actions-2026-08-19.json`
- `.local/zoho/quality-gate-extra-coql.json`
- Contrast only: `xray/docs/ads-launch/us-employer-conversion-reconstruction-2026-08-18.md`

---

## Questions for the planner

1. Sequence: Post file 02 now (Checklist already says today), or wait until George has Editor time and a clean Australia Get-recent-changes? File 03 still waits either way.
2. After 02: is Exact-enable of `hire a social media manager` (file 03) worth doing on n=1 Phrase convert, or wait for a second AU SMM employer?
3. Future bidding target: stay Maximize Clicks until a Zoho-gated Qualified Employer + booked call / Job Order exists — or prepare a **read-only** map of `VC_*_Thank_You` vs `VC_*_Calendly_Booked` as two steps of one person, without changing settings?
4. RE Broad: leave until a second Zoho row, or set a calendar reminder (e.g. 27 Aug) to re-score?
5. Company-required field: treat as a later form change **not** tied to `/us` visual rebuild — when, and on which markets?
6. Ads reauth: only to apply the protect label, or also one cheap conversion-action-by-day read to **name** the 2+4 fires and confirm reading (b)? (Call budget must be explicit. 1–2 calls.)
7. How should the planner talk about the 14 Aug unresolved US conversion so it does not get mixed into this Aug 18 ledger again?
8. `VC_Inquiry_Class`: when (if ever) to ask Cheyenne/Holly to use a dedicated class field, without turning uploads on?

---

**End of brief.** ChatGPT: plan only. Do not run tools. Do not invent PII. Do not override the freeze. Zoho people outrank Ads tags. Form + booked call is two steps, not a duplicate. Do not switch to Maximize Conversions. Do not activate offline uploads.
