# Sales Enquiry LP → Zoho create (test pass)

**Date:** 2026-08-17  
**Writes:** ON in Vercel production only (`ZOHO_SUBMISSION_ENABLED=true` env · still `false` in git · `ZOHO_CRM_ENABLED` false)  
**Ads / Zapier / Data Manager:** not touched  
**Batch:** not run

## 1. API domain + version

- Accounts URL: `https://accounts.zoho.com`
- API domain: `https://www.zohoapis.com`
- Version: CRM **v8**

## 2. Module

| UI name | API name |
|---------|----------|
| Sales Enquiries | `Leads` |

Confirmed from `GET /crm/v8/settings/modules`.

## 3. Required fields

Only **Last Name** (`Last_Name`) is system-mandatory.  
`Lead_Status` is **not** required and has **no metadata default**.

## 4. Field mapping (verified, no new Zoho fields)

| LP / test source | Zoho API name | Type | Notes |
|------------------|---------------|------|-------|
| First name | `First_Name` | text | |
| Last name | `Last_Name` | text | Mandatory |
| Email | `Email` | email | |
| Phone | `Phone` | phone | |
| Company | `Company` | text | Test: `[TEST] Virtual Coworker API` |
| Message + unmapped extras | `Other_Client_Profile_Information` | textarea | Enquiry Notes. This org has **no** `Description`. |
| Submission ID | `Gravity_Form_Entry_ID` | text | Existing field. `VC_Submission_ID` does not exist. |
| Market us/au | `Region` | picklist | `USA` / `AU` |
| Requested lead source text | `Form_Source` | text | `API Integration Test` (not a picklist value) |
| Lead source picklist | `Lead_Source` | picklist | Test uses existing **Other**. Do not invent `API Integration Test` on the picklist. |
| Status | `Lead_Status` | picklist | **New Enquiry (Auto)** only. Never Discovery Scheduled / Job Order Submitted / Placement. |
| Company website | `Website` | website | |
| Landing page URL | `Referring_URL` | website | |
| GCLID | `utm_gclid` | text | First test **omitted** (Ads Data Manager risk). |
| UTM source/medium/campaign/term/content | `utm_*` | text | Exist. |
| Campaign | `Campaign_Name` | text | |
| Role | `Job_Position_Required` | text | |
| Timestamp | `Submission_Timestamp` | datetime | |

## 5. Files created / modified

- `vision/lib/zoho/config.ts` — gate is `ZOHO_SUBMISSION_ENABLED` (default false)
- `vision/lib/zoho/payload.ts` — create-only map; safe status; notes field
- `vision/lib/zoho/client.ts` — `createEmployerLead` POST create, `trigger: []`
- `vision/app/api/lead/route.ts` — Zoho after email path; Zoho failure does not fail email
- `vision/lib/zoho/client.test.ts`, `vision/lib/lead-delivery.test.ts`
- `.env.example` — `ZOHO_SUBMISSION_ENABLED=false`
- `ads-launch/zoho/probe_sales_enquiry_metadata.py`
- `ads-launch/zoho/create_one_safe_test.py`
- `ads-launch/zoho/_common.py` — POST helper
- This file · `xray/zoho-test.html`

## 6. First test result

**One record created. Stopped.**

- Method: POST `/crm/v8/Leads` create-only, `trigger: []`, skip cadences
- First attempt (read-only token): HTTP **401** `OAUTH_SCOPE_MISMATCH`
- After least-privilege reauth (`Leads.CREATE` + existing READ only): HTTP **201** `SUCCESS`
- Record ID: `6724032000029820001`
- Submission ID: `VC-ZOHO-TEST-20260817T212046Z`
- GET-by-id HTTP **200**
- Stored: Company `[TEST] Virtual Coworker API` · Lead_Status **New Enquiry (Auto)** · Form_Source `API Integration Test` · no GCLID · not converted · JO flag false
- Owner: George Aguilar
- No other Zoho records modified

## 7. Batch results

Not run. Stopped after the one successful create.

## 8. Record IDs

| ID | Source | Status |
|----|--------|--------|
| `6724032000029820001` | First API test (do not modify) | New Enquiry (Auto) |
| `6724032000029822001` | Live `POST /api/lead` from `/us` | New Enquiry (Auto) |
| `6724032000029823001` | Live `POST /api/lead` from `/us/consult` | New Enquiry (Auto) |

## 9. Unmapped (folded into Enquiry Notes or omitted)

- `gbraid` / `wbraid` — fields do not exist
- `Referrer` — exists but **read-only**
- Ad group / keyword / match / device — no fields
- Requested source `API Integration Test` — not on `Lead_Source` picklist → `Form_Source` + notes
- Qualification, JO flags, discovery date, blueprint status — **intentionally not written** (Ads Data Manager)

## 10. Unexpected workflows / notifications / assignment

Create succeeded. No JO / Discovery / convert flags on the stored row. Owner assigned to George Aguilar (existing default). Data Manager still shows two live Leads connections:

- Zoho JO Submitted US [Standard OCI]
- Zoho Discovery Scheduled US [Standard OCI]

Zapier is separately linked. None of those were changed.

## 11. Errors

First create: `OAUTH_SCOPE_MISMATCH` (token lacked CREATE). After reauth: none. `NO_PERMISSION` did not occur.

## 12. Safe to enable live?

**Enabled on Vercel production** after the create-only path was proven. Git still has `ZOHO_SUBMISSION_ENABLED=false`. Email first; Zoho additional; Zoho fail does not fail email. Two live LP posts confirmed (`/us`, `/us/consult`).

## 13. Smallest remaining action

Team: open Google Ads → Data Manager → Zoho CRM card, fix the 1 issue on each Leads connection, set JO / Placement values they already use. Do not qualify / convert / book the `[TEST]` rows.

## Ads-filter safety (why the first payload was neutral)

Exact Data Manager filter JSON was not readable from CRM metadata. Named usages point at `Lead_Status` values **Job Order Submitted** and **Discovery Scheduled**. First payload therefore:

- Status **New Enquiry (Auto)** only
- No gclid / gbraid / wbraid
- No JO / discovery / qualification / placement / convert fields
- Company `[TEST] Virtual Coworker API`
- Notes `TEST RECORD — DO NOT CONTACT — DO NOT QUALIFY — DO NOT CONVERT`
