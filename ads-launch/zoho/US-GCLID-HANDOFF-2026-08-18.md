# US GCLID → Zoho handoff (create-only)

Site already sends click IDs on `POST /api/lead`. Zoho mapping for this org uses **`utm_gclid`**, not `$gclid`. Production writes stay gated on `ZOHO_SUBMISSION_ENABLED`.

Absence of GCLID on a Zoho row does **not** mean the enquiry was organic.

## Payload → intended Zoho field

| Source key (`/api/lead` record) | Zoho API name | Type | Status |
| --- | --- | --- | --- |
| `gclid` | `utm_gclid` | text | Verified field. Mapper writes it when present. |
| `utm_source` | `utm_source` | text | Verified |
| `utm_medium` | `utm_medium` | text | Verified |
| `utm_campaign` | `utm_campaign` | text | Verified |
| `utm_term` | `utm_term` | text | Verified |
| `utm_content` | `utm_content` | text | Verified |
| `utm_matchtype` | Enquiry Notes line `match_type` | text | No dedicated field. Fold into `Other_Client_Profile_Information`. |
| `utm_device` | Enquiry Notes line `device` | text | Same |
| `gbraid` | proposed `utm_gbraid` | text | **Missing.** Notes-only until created. |
| `wbraid` | proposed `utm_wbraid` | text | **Missing.** Notes-only until created. |
| `lp_version` | proposed `VC_LP_Version` (or env `ZOHO_CRM_FIELD_LP_VERSION`) | text | Parsed in config; **mapper does not write a custom field today.** Notes line `lp_version`. |
| `landing_page_url` | `Referring_URL` | URL/text | Verified |
| `role` | `Job_Position_Required` | text | Verified |
| `session_id` / `submission_id` | `Gravity_Form_Entry_ID` (submission) + Notes `session_id` | text | Submission id mapped. Session id notes-only. |
| `market` | `Region` | picklist USA/AU | Verified |

## Zoho admin tasks

1. Confirm Leads (Sales Enquiry) has writable `utm_gclid`.
2. Optional: create `utm_gbraid`, `utm_wbraid`, `VC_LP_Version` as text. Until then, read notes.
3. Do **not** turn on `ZOHO_CRM_ENABLED`. Writes use `ZOHO_SUBMISSION_ENABLED` only when George approves.
4. After a safe test: submit one US employer lead with a dummy `gclid=TEST_GCLID_YYYYMMDD` on a non-production path or with sales warned. Open the Zoho record. Confirm `utm_gclid` equals that value. Then void/delete the test enquiry.

## Safe test procedure

1. Open `https://www.virtualcoworker.app/us?gclid=TEST_GCLID_20260818&utm_source=google&utm_medium=cpc&utm_campaign=test`.
2. Complete guided match with a clearly labelled test name/email (sales inbox).
3. Confirm thank-you `sid=`.
4. In Zoho: find the Sales Enquiry by email. Check `utm_gclid` = `TEST_GCLID_20260818` and notes contain `lp_version: baseline_v1_2026_08`.
5. Delete or mark as test. Never leave a test GCLID in reporting.

Code: `vision/lib/zoho/payload.ts`, `vision/lib/zoho/config.ts`.
