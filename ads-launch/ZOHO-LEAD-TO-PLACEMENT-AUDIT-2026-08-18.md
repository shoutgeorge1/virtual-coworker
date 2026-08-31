# Zoho lead-to-placement audit — 18 August 2026

Read-only. CRM v8 GET + COQL only (~107 calls across two probes). Nothing created, updated, or deleted. `ZOHO_CRM_ENABLED` stayed false. Google Ads was not called. Ash is **not** in the 38 Zoho user seats.

Org: **Virtual Coworker** · Zoho One Enterprise · AUD · Australia/Brisbane · 29 licenses / 29 active.

---

## Current flow (what the records actually do)

```text
Website form / human / WordPress dump
        │
        ▼
Sales Enquiry  (API module Leads)
        │  human Lead_Status
        │  Job Order created separately
        │  lookup Job_Orders.Client_Name → this enquiry  (223 / 236 in 90 days)
        ▼
Job Order  (custom module Job_Orders)
        │  Stage → Placement  (92) or Job Order Cancelled (95) in 90 days
        │  Recruit_Job_Opening_ID on 15 all-time
        ▼
Placement  (API module Deals)
        ├── Account_Name → Account
        └── Contact_Name → Contact
        NO Job Order lookup on Placements
```

Standard Zoho convert (`Converted__s`) is almost unused: **1 in 90 days**, 84 all-time. The live path is “keep the enquiry, make a Job Order.” Enquiry status **Job Order Submitted** (202 in 90 days) is **not the same object** as a Job Orders row (236 in 90 days). Ask Ash/Caitlin which one is the real handoff.

Phone does **not** have its own enquiry module. `Lead_Source = Phone` is rare (**8 / 639** in 90 days). Calls live in **Calls** (374 in 90 days): 369 outbound, 4 missed, **1 inbound**. Newest call subjects are mostly “Call scheduled with …”, with duration and `Call_Result` blank — scheduled consults, not a completed-call log.

---

## Modules and fields that matter

| UI name | API name | Role |
|---------|----------|------|
| Sales Enquiries | `Leads` | Front door for website and the few phone-tagged rows |
| Job Orders | `Job_Orders` | Recruiting request |
| Placements | `Deals` | After hire / ops |
| Accounts / Contacts | `Accounts` / `Contacts` | Company and people dump |
| Calls / Tasks | `Calls` / `Tasks` | Scheduled calls; follow-up tasks |
| Notes / Emails | `Notes` / `Emails` | Exist; this login could not census them (see limits) |

### Sales Enquiries — attribution

| Need | Field | In CRM? | Fill (facts) |
|------|-------|---------|--------------|
| GCLID | `utm_gclid` | Yes | 580 all-time · **222 / 639** in 90d · **9 / 88** in 14d |
| UTM source/medium/campaign/term/content | `utm_*` | Yes | 14d: source 38, term 10, `Campaign_Name` 4 |
| Google Ads campaign | `utm_campaign` / `Campaign_Name` | Text only | `.app` rows store a **numeric Ads id** (e.g. `24117249292`), not a name |
| Ad group | — | **No field** | |
| Keyword / search term | no Ads field; `utm_term` is closest | Partial | 248 all-time; 10 in 14d |
| Landing page | no `Landing_Page`; `Referring_URL` used | Partial | 6 in 14d (those 6 are `virtualcoworker.app`) |
| Form source | `Form_Source` (text) | Yes | 14d: blank **57**, Job Order Form 24, `form` 6, API Integration Test 1 |
| iOS click ids | `gbraid` / `wbraid` | **No fields** | |
| Paid vs organic flag | `Source_Type` (`Google Paid` / `Organic`) | Yes | **0 / 639** filled in 90d |

`.app` writes (from 17 Aug) use `Form_Source = form`, `Lead_Source = Website`, `Gravity_Form_Entry_ID` as submission id, owner George Aguilar. That `form` label is indistinguishable from a generic word — not a Zoho failure, a mapper string.

### Sales Enquiries — qualification / follow-up

| Field | Values / notes | Used? |
|-------|----------------|-------|
| `Lead_Status` | Working human status. Includes Junk Lead, Decided Against / Not a Fit, Job Order Submitted, Discovery Scheduled, Sales Call Follow Up 1–3, Unresponsive, brochure, no-shows, **Resume**, Pre-Qualified, Create Job Opening | Resume / Pre-Qualified / Create Job Opening = **0** in 90d |
| `Qualification_Status` | Not Yet Qualified / Passed / Failed | **0 / 639** in 90d |
| `Blueprint_Lead_Status` | Parallel picklist | Filled more than `Lead_Status` on some rows; **21 / 80** newest disagree |
| `Other_Client_Profile_Information` | Enquiry Notes | Used (130 / 200 newest) |
| `Next_Follow_Up_Date`, `Discovery_Call_Date`, `Outbound_Call_Count` | Dates / count | Present; not fully counted this pass |
| `AI_Reasoning_Notes`, `Sales_Call_Transcript`, `Call_Recording_Link` | Text / URL | Present; meaning of AI notes **UNKNOWN** |
| Owner | Cheyenne (US) / Holly (AU) on most live rows | George owns the new `.app` test/live writes |

There is **no** job-seeker / work-seeker field. Monday’s “work-seekers” bucket is not a CRM column we can query.

### Job Orders → Placements

- `Client_Name` = lookup **Sales Enquiry** (`Leads`). 223 linked / 13 unlinked in 90d.
- `Linked_Sales_Enquiry` and `Linked_Account` are **text**, not lookups.
- `Stage` is recruiting pipeline (Sourcing → … → Placement / Cancelled).
- `UTM_Gclid` (different name from Leads): **18 all-time**.
- Placements: `Account_Name`, `Contact_Name`, `Contract_Invoice_Status` (meaning **UNKNOWN**), `Onboarding_Status`. **No GCLID. No Job Order lookup.**

---

## Volume

| List | All-time | 90d | 30d | 14d |
|------|--------:|----:|----:|----:|
| Sales Enquiries | 3,461 | 639 | 210 | 88 |
| Job Orders | 791 | 236 | 68 | 30 |
| Placements | 390 | 108 | 32 | 18 |
| Calls | 1,128 | 374 | 118 | 41 |
| Tasks | 2,739 | 881 | 292 | 104 |
| Contacts | 8,012 | 100 | 15 | 6 |

This week (Mon 17 Aug PT → probe time Tue 18): **16** enquiries. Last complete week (Mon 10–Sun 16): **37**.

90-day enquiry source: Website **539** · blank 58 · Forbes 10 · Phone **8** · Zen Desk 7 · Google **6** · Referral Partner 6 · Other 4 · Internal Referral 1.

90-day enquiry region: USA 332 · AU 279 · blank 28.

---

## Counts: employer / job seeker / spam / test / unclassified

**The API cannot count job seekers.** `Lead_Status = Resume` exists and has **zero** records all-time. `Qualification_Status` is unused. Do not treat “Not a Fit” as job-seeker without Ash.

Last **90 days** (639 enquiries), by **status only** — mutually exclusive:

| Status (as stored) | n | Plain reading until Ash confirms |
|--------------------|--:|----------------------------------|
| Job Order Submitted | 202 | Sales marked a hiring outcome on the enquiry — **not proof of a Job Orders row** |
| Unresponsive Clients | 113 | Dead / asleep |
| Decided Against / Not a Fit | 95 | Disqualified — mix unknown |
| Junk Lead | 92 | Junk / spam / **maybe** seekers — **ask** |
| Information Brochure Sent | 59 | Nurture |
| Sales Call Follow Up 1–3 | 23 | Cadence |
| Not Ready (1/2/3 months) | 22 | Deferred |
| No Shows | 14 | Discovery no-show |
| New Enquiry (Auto) | 11 | Untouched auto-entry (includes new `.app` + tests) |
| Discovery Scheduled | 3 | Booked consult |
| Other (Placement, JO Cancelled, Attempted to Contact) | 5 | Rare |

Last **14 days** (88): Junk **21** · Job Order Submitted **21** · Brochure 13 · New Enquiry (Auto) **11** · Not a Fit 8 · rest cadence / no-show / discovery.

**Internal tests (heuristic, not a Zoho flag):** newest sample includes `[TEST] … Do not contact`, `[TEST] Virtual Coworker API`, `job test`, Job Orders named `job test` / `job order testing` / `agent assign test` / `crm to recruit recruit test`. Six of the 11 “New Enquiry (Auto)” rows in 14 days are George `.app` / API tests. Caitlin created an AU row `job test` today that already has a Job Order.

**Unclassified for Ads / hiring:** anything not Junk, not an obvious `[TEST]`, and not Job Order Submitted — especially Lois Website rows with company NA / Teleperformance / “Virtual Co worker”. That is a **people** classification, not a field.

---

## Which records can be tied to Google Ads

| Tie | Rule | 90d enquiries | 14d enquiries | Job Orders | Placements / Calls |
|-----|------|---------------|---------------|------------|--------------------|
| **Can** | `utm_gclid` / `UTM_Gclid` filled | **222 / 639** | **9 / 88** | **18 all-time** | **No field** |
| Weak | `utm_source` google/googleads or `Lead_Source = Google`, no click id | Source Google = 6 in 90d; more have utm google without gclid | 8 google-ish in newest-14d slice of 200 | A few `chatgpt.com` / google on JO UTMs | — |
| **Cannot** | No gclid and no google UTM | Majority of Website / blank / phone | **45 / 82** in the 14d slice of the newest 200 | Almost all recent JOs | All placements; all calls (0 gclid in description on 80 newest) |

Absence of GCLID does **not** mean organic. WordPress / Lois rows often have `(direct)` / `organic: google` / Facebook referral and no click id. New `.app` rows **can** store gclid + numeric campaign id + `utm_term` when the URL had them.

Do not use Zoho as a Primary Ads conversion until Ash/team name the exact status that means “real employer,” and click ids survive onto Job Orders.

---

## Data-quality / workflow problems

1. **Two meters for “job order.”** Enquiry status 202 vs Job Orders rows 236 vs JO stage “Job Order Submitted” = **3** in 90 days.
2. **No Job Order → Placement link.** Newest placements named Owner / CFO / Founder with **no Account and no Contact** (31 / 80 newest have blank Account).
3. **Job Orders without an enquiry:** 13 / 236 in 90d. Newest include tests and Recruit-sync shaped names (`Ms`, `Manager`, `Owner`) with `Recruit_Job_Opening_ID` set.
4. **Qualification unused.** The field that would say Passed/Failed is blank on every 90-day enquiry.
5. **Blueprint vs Lead Status drift** on 21 / 80 newest.
6. **Lois / WordPress still the volume path.** Social Marketing (Lois) created 117 / 200 newest enquiries. `.app` is a thin overlay (6 `form` + tests).
7. **Phone inbound is invisible as an enquiry source.** 1 inbound Call vs 8 Phone-source enquiries vs 888/1300 lines in the real world.
8. **Emails and Notes unread on this token.** Related-list metadata HTTP 401. `GET /Emails` 403. Notes COQL rejected. Follow-up **tasks** are visible (`CALL Sales Enquiry`, Client Check-in SMS/email/phone) — all 80 newest still **Not Started**.
9. **Duplicates in newest 200 enquiries:** 3 repeated emails, 3 phones, 9 companies. Not a full-org duplicate scan.
10. **Test debris** sitting in live pipelines (enquiry + job order).
11. **Ash has no Zoho seat** in the user list. He cannot verify UI vs API unless someone shares a screen or a seat.

---

## Recommended fixes

### Cursor can implement (after this audit is approved — not now)

- Keep production writes create-only; do not upsert; do not change statuses to Discovery / JO Submitted.
- Change `Form_Source` from the word `form` to a labelled value (e.g. `VC.app US` / `VC.app AU`) **if Ash/George agree the string**.
- Fold gbraid/wbraid into Enquiry Notes until fields exist (already the parked plan).
- Keep `utm_gclid` mapping; do not invent `$gclid`.
- Repeat this read-only census after Ash answers (script: `ads-launch/probe_zoho_lead_to_placement_audit.py`).
- Do **not** enable `ZOHO_CRM_ENABLED`. Do **not** create Zoho fields from Cursor without approval.

### Ash / team must decide

- What **Junk Lead** vs **Not a Fit** vs unused **Resume** means — which bucket is job-seeker / spam / internal.
- Whether sales will **use `Qualification_Status`**, or it is dead schema.
- When a real employer becomes a Job Order: enquiry status, Job Orders row, or both.
- Whether Placements must look up a Job Order (schema change).
- Who **Social Marketing (Lois)** is and whether WordPress should keep creating Website rows.
- How a **phone enquiry** should be logged (Sales Enquiry source Phone vs Call vs both).
- Who deletes/voids **test** enquiries and job orders.
- Whether Ash gets a **read-only Zoho seat**.
- Meaning of `Contract_Invoice_Status` and `AI_Reasoning_Notes`.
- Whether Blueprint or Lead Status is the source of truth.

---

## Limits of this login (do not guess past these)

- Related-list **settings** 401 — cannot list every child relation from metadata.
- Notes / Emails record census failed (COQL invalid or 403). One Lead Emails related-list returned HTTP 200 with **0** rows.
- No full duplicate scan of 3,461 enquiries — only newest 200.
- Workflows, permissions, and Zapier/Flow were **not** read (would be settings writes-adjacent / out of scope).
- Google Ads inventory was **not** queried.

---

## Questions for Ash (do not guess)

See chat draft. Do not send until George approves.
