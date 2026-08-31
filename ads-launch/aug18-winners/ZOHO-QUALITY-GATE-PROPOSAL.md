# Zoho quality gate — proposal only

**Date:** 2026-08-20  
**Writes:** OFF. Do not turn on `ZOHO_CRM_ENABLED`. Do not write to Zoho. Do not activate offline uploads. Do not change Ads conversion settings. Do not switch bidding.

Worker JSON next to this file: `ZOHO-QUALITY-GATE-PROPOSAL.json`.

---

## Why this exists

The website form will never stop every job seeker. Zoho is the last gate.

A job seeker who beats the form still enters Zoho. Sales marks them Job Seeker. That row must **never** become a qualified-employer conversion sent back to Google Ads.

Only confirmed employer outcomes are eligible for a *future* offline upload. That upload is **not** turned on.

---

## How to count people (measurement correction)

Do **not** treat form-submit + booked call as duplicate tracking.

Intended funnel:

1. Employer form submitted
2. Call booked after the form

Report as: **one human lead, two funnel steps, stronger if they booked a call.**

Preserve separate configured values (`VC_*_Thank_You` and `VC_*_Calendly_Booked`). Only flag duplication if the **same** action fires repeatedly with no distinct user action.

Best path: ad click → employer form → booked call. That beats a form alone.

A booked call is a strong employer outcome **only after** the record is classified as employer (not junk / job-seeker / test / unknown).

---

## AU 4 Ads conversions vs 2 junk Zoho rows

Re-read with the rule above.

| Fact | Value |
|------|--------|
| Ads AU 18 Aug (click date) | 4.0 conversions (`executive-snapshot` 19 Aug) |
| Zoho paid people on that Ads day | 2 rows, both `Junk Lead` |
| Discovery / Calendly on those rows | **None.** Extra COQL 20 Aug: `Discovery_Call_Date` empty. Status is Junk Lead, not Discovery Scheduled. |
| Form + Calendly? | **No.** They did not book a call. |

Careful reading: this is **stacked measurement of one action family** on the same submit (form + thank-you + qualify + close), not four people, and not a legitimate form → booked-call progression.

US 2 Ads conversions match 2 Zoho people (1 good, 1 not a fit). That is 1:1. Do not change conversion settings.

---

## Can Zoho classify every inquiry today?

**Not reliably, as the CRM is used now.** The buckets we need do not all exist as filled fields.

| Bucket we need | Current Zoho signal | Reliable today? |
|----------------|---------------------|-----------------|
| Qualified Employer | `Lead_Status` = Job Order Submitted (enquiry label, not a Job Orders row) | Partial. Sales uses it. Not proof of a Job Order object. |
| Probable Employer | Brochure / Attempted to Contact / New Enquiry + company or role | Heuristic only. |
| Job Seeker | No working field. `Lead_Status = Resume` exists and is **0 all-time**. Monday “work-seekers” is not a CRM column. | **No.** |
| Spam | `Lead_Status` = Junk Lead | Partial. May mix spam and seekers. Ask Cheyenne/Holly. |
| Internal Test | Notes / Form_Source / `[TEST]` company | Heuristic. Works for `.app` API tests. |
| Unknown / Needs Review | Everything else | Default, not a picklist value. |

Extra COQL on the 5 paid gclid people (20 Aug, 1 call):

- `Qualification_Status`: empty on all 5
- `Discovery_Call_Date`: empty on all 5
- `Blueprint_Lead_Status` vs `Lead_Status`: US not-a-fit is **Decided Against / Not a Fit** on status and **Junk Lead** on blueprint. Do not trust blueprint alone.

---

## Proposed classification (create these, do not write them yet)

Add one dedicated picklist on Sales Enquiries (`Leads`). Suggested API name: `VC_Inquiry_Class`.

Do **not** overload `Lead_Status`. That field is the sales cadence (brochure, attempted, discovery, job order). Classification is a different question.

| Value | When |
|-------|------|
| Qualified Employer | Human review or Job Order path confirms they hire. |
| Probable Employer | Looks like a business. Sales still working it. Not junk. |
| Job Seeker | Looking for work. Even if they booked a call. |
| Spam | Fake / junk / no real person. |
| Internal Test | `[TEST]`, API Integration Test, agent assign test. |
| Unknown / Needs Review | Default. Stay here until a human picks. |

Create-time default: **Unknown / Needs Review**.  
Obvious `[TEST]` / `API Integration Test`: **Internal Test**.  
Form already flagged seeker (if that ever happens): **Job Seeker**.  
Do not auto-promote to Qualified Employer from the form.

### Preserve on every record

These already exist unless noted. Never drop them on later stages.

| Need | Field today | Gap |
|------|-------------|-----|
| GCLID | `utm_gclid` | Keep onto Job Orders (`UTM_Gclid` exists, rarely filled). |
| UTMs | `utm_source/medium/campaign/term/content` | Keep. |
| Market | `Region` (`USA` / `AU`) | Keep. |
| Campaign | `utm_campaign` / `Campaign_Name` | `.app` stores a numeric Ads id. Fine. |
| Ad group | **No field** | Add `VC_Ad_Group` (or Description line) before uploads. `utm_content` is the current proxy. |
| Keyword | `utm_term` | Keep. |
| Requested role | `Job_Position_Required` | Keep. |
| Company | `Company` | Keep. |
| Conversion timestamps | `Created_Time`, `Submission_Timestamp`, `Discovery_Call_Date` | Fill `Discovery_Call_Date` when a call is actually booked. Empty on all 5 paid rows. |

iOS `gbraid` / `wbraid`: fields do not exist. Omit until writes-on design.

---

## Upload-eligibility logic (future only — OFF)

Never send a row to Google Ads unless **all** of these are true:

1. `VC_Inquiry_Class` is **Qualified Employer** (not Probable, not Unknown).
2. Click id present (`utm_gclid`).
3. Outcome is a confirmed employer step: Job Order Submitted **or** Discovery Scheduled **after** classification as employer.
4. Not Job Seeker, Spam, Internal Test, or Unknown.

Hard blocks:

- Job Seeker → never upload, even with a booked call.
- Spam / Internal Test → never upload.
- Unknown → wait for review.
- Booked call on a junk or job-seeker row → **not** an employer conversion.
- Website `VC_*_Thank_You` / `qualify_lead` / `close_convert_lead` on the same submit → counting, not an upload trigger.

Probable Employer stays in Zoho for Cheyenne (US) / Holly (AU). Not an Ads upload.

---

## Maximize Conversions — deliverable 11

Evaluate AU and US separately. Do not force both to change together. **Neither is ready.**

Window we can prove for paid people: Zoho `utm_gclid` present, Created_Time **17–20 Aug PT** (`2026-08-17T00:00:00-07:00` → `2026-08-21T00:00:00-07:00`). Ads 18 Aug click-date counts are from the 19 Aug snapshot (live Ads API blocked `invalid_grant`).

Wider Zoho window (same dates, **all** sources, not just paid): US 14 · AU 14 · blank 1. Do not add those unpaid rows to the paid score.

### US (Cheyenne)

| Meter | Paid gclid | Note |
|-------|-----------:|------|
| Human inquiries | 2 | Both 18 Aug PT |
| Qualified employers | 0 | 1 probable (still calling). 1 not a fit. |
| Booked employer calls | 0 | No Discovery date. Window Discovery Scheduled rows are organic/direct, no gclid. |
| Job seekers | 0 | No working seeker field. |
| Spam / tests | 0 paid | 1 Internal Test in the wider US list (no gclid). |
| Unknown | 0 paid | |

**Ready for Maximize Conversions?** No. Two people is not a bidding sample. The one good lead has not booked a call.

### AU (Holly)

| Meter | Paid gclid | Note |
|-------|-----------:|------|
| Human inquiries | 3 | 2 junk on Ads 18 Aug AEST. 1 probable on 19 Aug. |
| Qualified employers | 0 | Brochure on the social-media row. Not a job order. |
| Booked employer calls | 0 | No Discovery date on any paid row. |
| Job seekers | 0 labeled | Junk may hide seekers. Cannot prove. |
| Spam / tests | 2 | Both `australia virtual assistant` → `/au/recruitment`. |
| Unknown | 0 paid | |

**Ready for Maximize Conversions?** No. Ads 4 on 18 Aug were junk people, not employers. That is the opposite of ready. Australia is **not** first.

### Actions that mix employer + junk / job-seeker

These fire on any form or booking. They do not wait for Zoho class.

- `VC_US_Thank_You` / `VC_AU_Thank_You`
- `VC_US_Calendly_Booked` / `VC_AU_Calendly_Booked` (only safe **after** employer class)
- GA4 `qualify_lead` / `close_convert_lead` (same-submit stack)
- Phone click / phone call (tap ≠ employer)

Zoho Discovery / JO uploads exist and are Secondary (`primary_for_goal` false, `include_in_conversions_metric` false). Do not turn them Primary. Do not start uploads.

### Currently Primary (`primary_for_goal` true) — 15 Aug / 19 Aug snapshots

**US Enabled:** `VC_US_Thank_You`, `VC_US_Calendly_Booked`, `VC_US_Phone_Call_From_Ads`, `VC_US_Phone_Call_From_Website`, `VC_US_Phone_Click_Website`.  
**US leftover in Conversions column:** hidden `eBook Download`.

**AU Enabled:** `VC_AU_Thank_You`, `VC_AU_Calendly_Booked`, `VC_AU_Phone_Call_From_Ads`, `VC_AU_Phone_Click_Website`, `Call (1300 886 740)`.  
**AU leftover in Conversions column:** hidden UA goals (Chat, Submission ×2, Job order form, Lead Form Submit Completion, Transactions).

Do not mutate these flags.

### Safe vs unsafe for conversion-based bidding

| Action | Safe to bid on now? |
|--------|---------------------|
| None of the website Primary stack | **No** — mixes junk and job seekers. |
| Future Zoho-gated Qualified Employer + booked call or Job Order | Only after n is real and uploads stay off until George says on. |
| Phone click | No. A tap. |
| GA4 page_view / user_engagement / session_start | Never. |
| Hidden UA leftovers | Never. |

---

## Front-end gate (extend — do not activate uploads)

The site already filters some junk before Zoho:

- Company name is required on the employer form (`validateEmployerLead`). Cheyenne asked for this. Do **not** rebuild `/us` or `/au/social-media` to make it stricter.
- Role pages preselect the role in the form. Keep that.
- Job-seeker phone / “looking for a job” already exits to careers. That person must never become an Ads conversion.

The website will still miss some seekers. Zoho is the last gate. Cheyenne (US) / Holly (AU) mark junk vs real employer. That mark is what we bid on later.

Do not turn on offline uploads. Do not change conversion settings. Do not switch to Maximize Conversions.

---

## Not done (on purpose)

- Offline uploads: OFF
- Conversion settings: unchanged
- Maximize Conversions: not switched
- Ads mutate: none. Protect label not applied (`invalid_grant`).
- Zoho writes: none
- `/us` and `/au/social-media` rewrites: none. Spend-only role pages already share the same trust stack (hours, dedicated seat, you interview, form role). No LP code change.
