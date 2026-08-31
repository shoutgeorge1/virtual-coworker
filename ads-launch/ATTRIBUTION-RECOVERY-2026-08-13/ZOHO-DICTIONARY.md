# Zoho field and relationship dictionary — 13 August 2026

Org: **Virtual Coworker** · Zoho One Enterprise · AUD · Brisbane time · one CRM for USA and AU.  
API: CRM V8. UI “no Leads” is a **rename**.

This is a dictionary, not permission to write.

---

## Modules

| API name | What sales sees | Role in the journey |
|----------|-----------------|---------------------|
| `Leads` | **Sales Enquiries** | Front door. Human status lives here. |
| `Job_Orders` | **Job Orders** | Custom module. Recruiting request. |
| `Deals` | **Placements** | After the hire. |
| `Contacts` | Contacts | Long dump (8,011). Not the paid-search inbox. Newest include Zoho Desk / PH people. |
| `Accounts` | Accounts | Company record. |
| `Calls` | Calls | 379 in 90 days. Duration fields exist. **No gclid.** |
| `Job_Openings` | Recruitments (webtab) | `api_supported=false`. Recruit barely visible. |
| `Google_AdWords` | Google Ads | Present. `api_supported=false`. **Not** proof the connector is on. |

Installed extras visible as modules: Sinch SMS (`twiliosmsextension0__*`), Zoho Sign, Zoho Desk. **CallRail: not found. Calendly: not found. Zapier: not a CRM module.**

---

## Volume (independently re-checked)

| List | All-time | Last 90 days | Since 1 Aug 2024 |
|------|--------:|-------------:|-----------------:|
| Sales Enquiries | 3,433 | 647 | 3,433 |
| Job Orders | 782 | 242 | 782 |
| Placements | 386 | 122 | 386 |
| Contacts | 8,011 | 102 | 8,011 |
| Calls | — | 379 | — |

All-time = since 1 Aug 2024. Why: **UNKNOWN** (rebuild vs imported dates).

---

## Sales Enquiries (`Leads`) — fields that matter

| API name | Label | Type | Notes |
|----------|-------|------|-------|
| `id` | Record id | id | Use in restricted artifacts only. |
| `Region` | Region | picklist | **USA** / **AU** / blank. 90d: 338 / 283 / 26. |
| `Lead_Status` | Lead Status | picklist | Human disposition. See below. |
| `Lead_Source` | Sales Enquiry Source | picklist | 90d: Website 550, blank 57, Forbes 10, Phone 7, Zen Desk 7, Google **6**. |
| `Form_Source` | Form Source | text | 90d: Job Order Form 222, blank 425. |
| `Gravity_Form_Entry_ID` | Gravity Form Entry ID | text | **0 populated all-time.** |
| `utm_gclid` | utm_gclid | text | **The** click id. 576 all-time; **231 in 90d**; 0 in newest 30. Not `$gclid`. |
| `utm_source` `utm_medium` `utm_campaign` `utm_term` `utm_content` | UTM | text | Present. |
| `Campaign_Name` | Campaign Name | text | Text, not a live Ads link. |
| `Referrer` `Referring_URL` `Website` | URLs | website | Hosts observed: WordPress-era, not `.app`. |
| `Submission_Timestamp` | Submission Timestamp | datetime | |
| `Job_Order_submitted_via_form` | Job Order submitted via form | boolean | **0** in 90 days. |
| `Converted__s` `Converted_Account` `Converted_Contact` `Converted_Deal` | Standard convert | — | Almost unused (**1** converted in 90d). |
| `Account` | Account | lookup | |
| `gbraid` `wbraid` `VC_Submission_ID` | — | — | **Do not exist.** |

### `Lead_Status` seen in last 90 days (647)

| Status | n | Plain meaning (inferred — confirm with Caitlin) |
|--------|--:|--------------------------------------------------|
| Job Order Submitted | 213 | Sales says this enquiry became a job order. **≠ automatic Job Orders row.** |
| Unresponsive Clients | 111 | Dead / asleep |
| Decided Against / Not a Fit | 98 | Disqualified |
| Junk Lead | 86 | Junk |
| Information Brochure Sent | 63 | Nurture |
| Sales Call Follow Up 1 | 21 | Cadence |
| Not Ready - 1 Month | 20 | Deferred |
| No Shows | 13 | Discovery no-show |
| Discovery Scheduled | 6 | Booked consult |
| Placement | 1 | Rare enquiry-level flag |
| New Enquiry (Auto) | 2 | Auto entry |

---

## Job Orders — fields that matter

| API name | Label | Type | Notes |
|----------|-------|------|-------|
| `Stage` | Job Enquiry Status | picklist | Pipeline, not the enquiry status. |
| `Region` | Region | picklist | 90d: AU 127, USA 110, blank 5. |
| `Client_Name` | **Sales Enquiry** | lookup | **234 / 242** filled in 90d. This is the enquiry link. |
| `Linked_Sales_Enquiry` | Linked Sales Enquiry | **text** | Not a lookup. |
| `Linked_Account` | Linked Account | **text** | Not a lookup. |
| `UTM_Gclid` | UTM_Gclid | text | **18 all-time, all 18 inside 90d.** Different name from Leads. |
| `UTM_Source` … | UTM | text | Recent gclid JOs: google / googleads / **chatgpt.com**. |
| `Client_Status` | Client Status | picklist | On the 18: New Client 16, Replacement 1, Returning 1. |
| `Recruit_Job_Opening_ID` | Recruit Job Opening ID | text | **8 all-time.** |
| `Last_Sync_Source` | Last Sync Source | picklist | 90d: blank 234, CRM 8. |
| `Owner` | Job Order Owner | user | Recent gclid set: Caitlin. |

### `Stage` last 90 days (242)

Cancelled **97** · Placement **95** · Endorsed Candidates 17 · Sourcing 8 · Scheduled Client Interview 6 · Job Order Submitted **3** · plus interview/feedback tail.

**Job Orders stage “Job Order Submitted” ≠ enquiry status “Job Order Submitted”.**

---

## Placements (`Deals`)

| API name | Notes |
|----------|-------|
| `Stage` | New Placement 49, Day 1 Check In 26, 1 Month 17, Cancelled 12, Started 7, … — **ops, not ads**. |
| `Region` | AU 46, USA 35, **blank 41**. |
| `Account_Name` `Contact_Name` | Lookups to Account / Contact. |
| `Lead_Source` | Same picklist family. |
| `Contract_Invoice_Status` | **Candidate for “signed client.” Meaning UNKNOWN.** |
| Click ids | **Not found.** |

---

## Relationships (do not assume 1:1)

```text
Sales Enquiry (Leads)
    │  Client_Name lookup on Job_Orders  (234/242 in 90d)
    │  Standard convert fields almost unused (1 in 90d)
    ▼
Job Order
    │  Stage → Placement or Cancelled (95 vs 97 in 90d)
    │  Recruit_Job_Opening_ID → Recruit (8)
    ▼
Placement (Deals)
    ├── Account_Name → Account
    └── Contact_Name → Contact
```

Related-lists API returned **empty** on this login. Links are inferred from lookup field names + counts.

| Question | Evidence | Verdict |
|----------|----------|---------|
| Does enquiry status JO Submitted create a Job Orders row? | 213 vs 242 vs stage JO Submitted = 3 | **Not automatic. Ask Caitlin.** |
| Can a Job Order exist without an enquiry? | 8 of 242 in 90d lack `Client_Name` | **Yes, sometimes.** |
| Can one employer have many job orders? | `Client_Status` includes Replacement / Returning | **Likely yes. Confirm.** |
| Can one enquiry create many job orders? | Not counted | **UNKNOWN** |
| Can one job order create many placements? | Not counted | **UNKNOWN** |
| Is cancellation before or after signing? | 97 JO cancelled + 12 placement cancelled | **Both exist. Ask.** |
| Is CSA / signed client a field? | `Contract_Invoice_Status` on Placements | **UNKNOWN meaning** |

---

## What creates a Sales Enquiry today (from records, not assumptions)

Observed creators on newest rows: **Social Marketing (Lois)** (21/30, source Website), Cheyenne (phone / referral / Google), others. Pattern matches WordPress + humans, not `.app`.

`.app` write: **off**.

---

## Users (no emails)

38 seats · 29 active · 17 Administrator · 29 licenses purchased.

| Name | Status | Profile | Role | Why they matter |
|------|--------|---------|------|-----------------|
| Caitlin McCartan | active | Administrator | CEO | Owns most recent job orders |
| Cheyenne Gichana | active | Standard | Manager | US sales / Calendly default |
| Holly Wallace | active | Administrator | Manager | AU / sales |
| Social Marketing (Lois) | active | Administrator | CEO | 21/30 newest enquiries. Identity **UNKNOWN** |
| Contracts - Virtual Coworker | active | Administrator | Manager | Shared mailbox |
| Web Master | active | Read Only | Manager | Integration-shaped |
| Eliah Haddadin | active | Administrator | Manager | Created 1 gclid job order |
| George Aguilar | active | Standard | Manager | shoutgeorge.com; created 5 Aug 2026 |
| George Aguilar | deleted | Administrator | — | gmail seat |
| Peter Mill | deleted ×2 | Administrator | — | profitmill.io leftover |

Created-time / last-activity for Lois: **not returned** by the users endpoint this pass.

---

## Mapping gap vs `vision/lib/zoho`

| Code default | Live CRM | Action later (not now) |
|--------------|----------|------------------------|
| Module `Leads` | Correct API name | Keep |
| `$gclid` | `utm_gclid` | Env override |
| `VC_Submission_ID` | Missing | Create field **after** write design |
| `market` us/au | `Region` USA/AU | Transform |
| gbraid / wbraid | Missing | Create only if iOS clicks matter |
| Source Google Ads | Almost unused | New picklist value + rule |

Do not enable `ZOHO_CRM_ENABLED` until those names are agreed and Zapier is frozen.
