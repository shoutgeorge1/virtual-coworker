# Ash / Claude — Zoho read-only audit handoff

Virtual Coworker. One CRM for USA and Australia.  
Use this as a repeatable Claude checklist. **Read-only until George approves a write.**

Related plan: `ads-launch/ZOHO-JO-PLACEMENT-PIPELINE-PLAN-2026-08-19.md`  
Last Cursor census: 19 August 2026.

---

## Hard prohibitions

- Do **not** create, update, delete, upsert, convert, or merge CRM records.
- Do **not** bulk-clean, reassign, or “fix” old rows.
- Do **not** send email or SMS. Do not enable cadences, journeys, or Twilio/Sinch responders.
- Do **not** move, qualify, or convert records labeled `[TEST]`, including:

  - `6724032000029820001`
  - `6724032000029822001`
  - `6724032000029823001`

- Do **not** upload conversions to Google Ads.
- Do **not** change Data Manager connections, conversion actions, or bidding.
- Do **not** set `ZOHO_CRM_ENABLED=true`.
- Do **not** touch WordPress or the organic site.

If Claude is unsure whether a call is a write: **do not call it.**

---

## 1. Read-only connection

| Item | Value |
|------|--------|
| Product | Zoho CRM (customized). UI hides “Leads”; API module is still `Leads`. |
| API | REST + COQL, **v8** |
| Accounts URL | `https://accounts.zoho.com` |
| API domain | `https://www.zohoapis.com` |
| Org timezone | Australia/Brisbane |

Self Client OAuth ≠ CRM Admin ≠ Google Ads Data Manager admin ≠ Ads developer token.

Cursor’s current token can read org, users, modules, fields, records, and COQL. It **cannot** read layouts, blueprints, workflows, functions, or webhooks (401 / 404). Ash should use a **read-only Zoho seat** in the UI for those, or a token that also has settings-automation READ — still no write scopes.

---

## 2. Minimum OAuth scopes (read-only)

```
ZohoCRM.org.READ
ZohoCRM.users.READ
ZohoCRM.settings.modules.READ
ZohoCRM.settings.fields.READ
ZohoCRM.modules.READ
ZohoCRM.bulk.READ
ZohoCRM.coql.READ
```

Optional later (still READ only), if George approves a new token so Claude can see automations:

```
ZohoCRM.settings.READ
```

Never request `CREATE`, `UPDATE`, `DELETE`, or `ALL` for this audit loop.

---

## 3. Verified module and field API names

| UI | API | Notes |
|----|-----|-------|
| Sales Enquiries | `Leads` | Front door |
| Job Orders | `Job_Orders` | Custom |
| Placements | `Deals` | Renamed Deals |
| Accounts | `Accounts` | |
| Contacts | `Contacts` | |

### Sales Enquiries (`Leads`)

| Purpose | API name |
|---------|----------|
| Record id | `id` |
| Status (human) | `Lead_Status` |
| Parallel status | `Blueprint_Lead_Status` |
| Source | `Lead_Source` |
| Form source | `Form_Source` |
| Market | `Region` (`USA` / `AU`) |
| Email / phone / company | `Email` `Phone` `Company` |
| Click id | `utm_gclid` — **not** `$gclid` |
| UTM | `utm_source` `utm_medium` `utm_campaign` `utm_term` `utm_content` |
| Campaign text | `Campaign_Name` |
| Landing URL | `Referring_URL` |
| Referrer | `Referrer` (read-only) |
| Submission id | `Gravity_Form_Entry_ID` |
| Notes | `Other_Client_Profile_Information` (no `Description`) |
| Submit time | `Submission_Timestamp` |
| Follow-up | `Next_Follow_Up_Date` |
| Qualification | `Qualification_Status` (unused) |
| Opt-out | `Email_Opt_Out` |
| Convert flags | `Converted__s` `Converted_Account` `Converted_Contact` `Converted_Deal` |

Missing on Leads: `gbraid`, `wbraid`, `VC_Submission_ID`, `Landing_Page`.

**Do not write** these status values from any integration: `Discovery Scheduled`, `Job Order Submitted`, `Placement`.

### Job Orders (`Job_Orders`)

| Purpose | API name |
|---------|----------|
| Id | `id` |
| Name | `Name` |
| Pipeline | `Stage` |
| Market | `Region` |
| Enquiry lookup | `Client_Name` → `Leads` (label: Sales Enquiry) |
| Enquiry text | `Linked_Sales_Enquiry` (text, not lookup) |
| Account text | `Linked_Account` (text, not lookup) |
| Click id | `UTM_Gclid` (different spelling from Leads) |
| UTM | `UTM_Source` `UTM_Medium` `UTM_Campaign` `UTM_Term` `UTM_Content` |
| Email / phone | `Email` `Phone_1` |
| Client type | `Client_Status` |
| Recruit link | `Recruit_Job_Opening_ID` |
| Created | `Created_Time` `Submission_Date` |

### Placements (`Deals`)

| Purpose | API name |
|---------|----------|
| Id | `id` |
| Name | `Deal_Name` |
| Ops stage | `Stage` |
| Market | `Region` |
| Account / contact | `Account_Name` `Contact_Name` |
| Email / phone | `Work_Email` `Personal_Email` `Work_Phone` `Mobile` |
| Invoice / onboard | `Contract_Invoice_Status` `Onboarding_Status` |
| Start | `Start_Date` `Stage_Modified_Time` |

**No GCLID field. No Job Order lookup.**

---

## 4. Safe read-only queries

COQL SELECT / COUNT only. Cap volume. Stop on HTTP 429.

```sql
select COUNT(id) from Leads where Created_Time >= '{since_90}'
select Lead_Status, COUNT(id) from Leads where Created_Time >= '{since_90}' group by Lead_Status
select Region, COUNT(id) from Leads where Created_Time >= '{since_90}' group by Region
select COUNT(id) from Leads where Created_Time >= '{since_90}' and utm_gclid is not null
select COUNT(id) from Leads where Created_Time >= '{since_90}' and Email is not null
select COUNT(id) from Job_Orders where Created_Time >= '{since_90}'
select Stage, COUNT(id) from Job_Orders where Created_Time >= '{since_90}' group by Stage
select COUNT(id) from Job_Orders where Created_Time >= '{since_90}' and UTM_Gclid is not null
select COUNT(id) from Job_Orders where Created_Time >= '{since_90}' and Client_Name is null
select Client_Status, COUNT(id) from Job_Orders where Created_Time >= '{since_90}' group by Client_Status
select COUNT(id) from Deals where Created_Time >= '{since_90}'
select Stage, COUNT(id) from Deals where Created_Time >= '{since_90}' group by Stage
select COUNT(id) from Deals where Created_Time >= '{since_90}' and Account_Name is null
```

GET newest 30 (redact email/phone/gclid before pasting anywhere):

```
GET /crm/v8/Leads?per_page=30&sort_by=Created_Time&sort_order=desc
GET /crm/v8/Job_Orders?per_page=30&sort_by=Created_Time&sort_order=desc
GET /crm/v8/Deals?per_page=30&sort_by=Created_Time&sort_order=desc
```

GET the three test rows by id. Confirm they are still `New Enquiry (Auto)`. Do not change them.

Metadata:

```
GET /crm/v8/settings/modules
GET /crm/v8/settings/fields?module=Leads
GET /crm/v8/settings/fields?module=Job_Orders
GET /crm/v8/settings/fields?module=Deals
GET /crm/v8/org
```

**UI-only for Ash (API token cannot see these):**

- Setup → Automation → Workflow rules, Functions, Webhooks, Blueprints
- Layouts and pipelines on Sales Enquiries, Job Orders, Placements
- Google Ads / Data Manager cards inside Zoho (if present)
- Zapier account: any zap named JO Submitted or Discovery Scheduled
- **PhoneBridge / Zoho Voice ↔ CRM** settings (24 Aug forensic: Calls-module CTI stubs exist with DID-as-caller; Sales Enquiries are not auto-created — see `ads-launch/PHONE_CALL_CRM_FORENSIC_AUDIT.md`)

---

## 5. Red / yellow flag definitions

### Red (do not send to Ads)

- Treating `Lead_Status = Job Order Submitted` as a `Job_Orders` row
- Treating Job Order `Stage = Placement` as a `Deals` row
- Missing click id **and** missing email **and** missing phone
- USA enquiry / click uploaded to AU (or the reverse), or blank `Region`
- Zapier + Data Manager both sending the same milestone
- `[TEST]` or API Integration Test rows
- Job seeker / junk once Ash labels them
- Click older than 90 days
- Placement send while **no Placement conversion action exists** (verified 19 Aug: none)

### Yellow (recoverable / human)

- Email/phone present, no click id (enhanced conversions only)
- Job Order with email but empty `UTM_Gclid` while the linked enquiry has `utm_gclid`
- Unlinked Job Order (`Client_Name` empty)
- Placement with no Account / Contact / Region
- Returning / replacement / additional hire (may be a second real JO)
- No follow-up date (field unused on all 638 recent enquiries)
- Unresponsive / brochure / not-ready / not-a-fit — do not auto-nurture

---

## 6. Repeatable Claude checklist

Run weekly or after any CRM / Data Manager change.

1. Confirm `ZOHO_CRM_ENABLED` is false and this run is GET/COQL only.
2. Refresh 90-day counts for Leads / Job_Orders / Deals.
3. Status vs module: enquiry “Job Order Submitted” count vs Job_Orders count vs JO stage “Job Order Submitted”.
4. Placement vs module: JO stage “Placement” vs Deals count.
5. Fill rates: `utm_gclid`, `UTM_Gclid`, email, phone, Region.
6. Unlinked Job Orders; Placements with no Account / no Contact / blank Region.
7. GET the three `[TEST]` ids — still New Enquiry (Auto)?
8. Newest 8 Job Orders: hop to `Client_Name` enquiry. Count gclid lost and Region mismatch. Mask PII.
9. UI: any new workflow that writes `Lead_Status`, `utm_gclid`, or `UTM_Gclid`?
10. UI / Ads: Data Manager last import time, error count, filter still on Leads statuses?
11. Zapier: JO / Discovery zaps on or off?
12. Ads (screenshot, not API unless George authorizes): still no Placement-named action?
13. Write a short scoreboard. Do not implement fixes.

Cursor probe to reuse (read-only):

```
python3 ads-launch/probe_zoho_jo_placement_pipeline_readonly.py
```

---

## 7. Masked sample payloads

### Enquiry (what `.app` already creates)

```json
{
  "module": "Leads",
  "id": "6724032…[suffix]",
  "Company": "[company]",
  "Lead_Status": "New Enquiry (Auto)",
  "Region": "USA",
  "Email": "[email]",
  "Phone": "[phone]",
  "utm_gclid": "[gclid:Nchars]",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "24117249292",
  "Form_Source": "form",
  "Gravity_Form_Entry_ID": "vc_us_…",
  "Referring_URL": "https://www.virtualcoworker.app/us"
}
```

### Job Order (Ads should key off this id, not the enquiry)

```json
{
  "module": "Job_Orders",
  "id": "…",
  "Name": "[role or company]",
  "Stage": "Sourcing",
  "Region": "AU",
  "Client_Name": { "id": "…enquiry…", "name": "[enquiry]" },
  "UTM_Gclid": null,
  "Email": "[email]",
  "Phone_1": null,
  "Client_Status": "New Client"
}
```

### Proposed Data Manager event (do not upload)

```json
{
  "google_ads_customer": "496-715-1855",
  "conversion_action": "Zoho JO Submitted US [Standard OCI]",
  "conversion_action_id": "7556921934",
  "conversion_time": "2026-08-19T12:58:51+10:00",
  "order_id": "vc_jo_{Job_Orders.id}",
  "gclid": "[if present on JO or linked enquiry]",
  "hashed_email": "[if no gclid]",
  "hashed_phone": "[if present]",
  "value": "GEORGE_SETS_IN_ADS_UI",
  "exclude_if": ["blank Region", "[TEST]", "cancelled", "no gclid and no email"]
}
```

### Placement (cannot send today)

```json
{
  "module": "Deals",
  "id": "…",
  "Deal_Name": "Owner",
  "Stage": "New Placement",
  "Region": null,
  "Account_Name": null,
  "gclid_field": "DOES_NOT_EXIST",
  "job_order_lookup": "DOES_NOT_EXIST",
  "ads_action": "DOES_NOT_EXIST"
}
```

---

## 8. Environment-variable names (no secret values)

| Name | Role |
|------|------|
| `ZOHO_CRM_CLIENT_ID` | OAuth client |
| `ZOHO_CRM_CLIENT_SECRET` | OAuth secret |
| `ZOHO_CRM_REFRESH_TOKEN` | Refresh token |
| `ZOHO_CRM_ACCOUNTS_URL` | Default `https://accounts.zoho.com` |
| `ZOHO_CRM_API_DOMAIN` | Default `https://www.zohoapis.com` |
| `ZOHO_CRM_MODULE` | Must be `Leads` for this org |
| `ZOHO_CRM_SUBMISSION_ID_FIELD` | `Gravity_Form_Entry_ID` |
| `ZOHO_CRM_TIMEOUT_MS` | e.g. `15000` |
| `ZOHO_SUBMISSION_ENABLED` | Production create-only gate for `.app` → enquiry. Git default false. |
| `ZOHO_CRM_ENABLED` | **Must stay false.** Legacy. Does not authorize writes. |
| `ZOHO_WEBHOOK_URL` | Generic webhook ≠ CRM sync |
| `ZOHO_CRM_FIELD_GCLID` | Override; live field is `utm_gclid` |
| `ZOHO_CRM_FIELD_GBRAID` | Unused — field missing |
| `ZOHO_CRM_FIELD_WBRAID` | Unused — field missing |
| `ZOHO_CRM_FIELD_MARKET` | Override; live field is `Region` |

Never commit values. Never put these in `NEXT_PUBLIC_*`.

---

## 9. Google Ads facts Claude must not invent

| Account | Customer id |
|---------|-------------|
| USA | `496-715-1855` |
| Australia | `573-539-1940` |

Live Data Manager / OCI actions are **Job Order Submitted** and **Discovery Scheduled**, both on **Leads statuses**.  
There is **no Placement conversion action** (API check 19 Aug 2026).  
Zapier twins with the same names are still ENABLED and Secondary.

USA click → USA action only. Australia click → Australia action only.

---

## 10. Questions Ash should answer (do not guess)

1. When sales says “we have a job order,” is that the enquiry status, the Job Orders row, or both?
2. When is a Placement real — JO stage, Deals row, start date, or invoice?
3. What do Junk Lead vs Not a Fit vs unused Resume mean? Which is job-seeker?
4. Is Zapier still uploading JO / Discovery?
5. Should replacements and additional hires count as a second JO conversion?
6. Who owns Social Marketing (Lois) Website creates?
7. Meaning of `Contract_Invoice_Status` and `AI_Reasoning_Notes`?
8. Blueprint or Lead Status — which is truth?

---

Do not implement CRM writes, Data Manager filter changes, Ads uploads, or nurture until George explicitly approves the matching item in the pipeline plan.
