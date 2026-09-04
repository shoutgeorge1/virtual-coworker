# Form boxes → Zoho boxes (draft)

Which form boxes save into which Zoho boxes so we can see paid leads in CRM.

Generated: `2026-09-04T18:12:20.150163+00:00` · **writes OFF** · owner: **Cursor** (not George homework)

**Status (2026-08-14):** Draft parked. Zoho + offline conversions are **DEFERRED DURING COLD START** — not cancelled. Production writes remain OFF. No Zoho writes. No Ads mutate. No new Zapier. No Primary Zoho conversions.

**Next:** Draft parked. Zoho + offline conversions are DEFERRED DURING COLD START (not cancelled). Do not turn writes on during cold start. Revisit only after the five-item gate.

## Notes

- Click id for this org is utm_gclid — not $gclid.
- Extras without Zoho fields (role, size, seats, timeline) fold into Description for now.
- VC_Submission_ID / gbraid / wbraid: create or omit when writes turn on — not George homework.
- Production writes remain OFF. No Zoho writes. No Ads mutate. No new Zapier. No Primary Zoho conversions.
- Missing VC_* / .app stamps on current Zoho rows is expected — new forms are not connected. Not a Zoho failure.

## Mapping

| Form box | Zoho box | Clarity | Note |
|----------|----------|---------|------|
| Name (first) (`firstName`) | `First_Name` | Clear | Form first name → Zoho First_Name |
| Name (last) (`lastName`) | `Last_Name` | Clear | Form last name → Zoho Last_Name |
| Email (`email`) | `Email` | Clear | Form email → Zoho Email |
| Phone (`phone`) | `Phone` | Clear | Form phone → Zoho Phone |
| Company (`company`) | `Company` | Clear | Form company → Zoho Company |
| Message (`message`) | `Description` | Clear | Form message → Zoho Description |
| Google click id (`gclid`) | `utm_gclid` | Clear | Paid click id. Use utm_gclid (not $gclid) for this org. |
| UTM source (`utm_source`) | `utm_source` | Clear |  |
| UTM medium (`utm_medium`) | `utm_medium` | Clear |  |
| UTM campaign (`utm_campaign`) | `utm_campaign` | Clear |  |
| UTM term (`utm_term`) | `utm_term` | Clear |  |
| UTM content (`utm_content`) | `utm_content` | Clear |  |
| Market (us/au) (`market`) | `Region` | Clear | us → USA · au → AU (Zoho Region picklist) |
| Company website (`company_website`) | `Website` | Clear |  |
| Referrer (`referrer`) | `Referrer` | Clear |  |
| Landing page URL (`landing_page_url`) | `Referring_URL` | Clear |  |
| Role requested (`role`) | `Description (line)` | Clear | Cursor: keep as a Description line for now (no custom field yet) |
| Company size (`company_size`) | `Description (line)` | Clear | Cursor: keep as a Description line for now |
| Seats needed (`positions_needed`) | `Description (line)` | Clear | Cursor: keep as a Description line for now |
| Hiring timeline (`hiring_timeline`) | `Description (line)` | Clear | Cursor: keep as a Description line for now |
| Form submission id (`submission_id`) | `VC_Submission_ID` | Cursor parked | Field does not exist yet. Create before writes (dedupe). Not a George homework item. |
| iOS click id (`gbraid`) | `(omit)` | Cursor parked | Does not exist in Zoho. Omit until we create a field when writes turn on. |
| Web click id (`wbraid`) | `(omit)` | Cursor parked | Does not exist in Zoho. Omit until we create a field when writes turn on. |

## Cursor parked (until writes on)

`submission_id`, `gbraid`, `wbraid`

## Needs Sales meaning later

_None on this draft._ Sales meaning for Job Order / Placement stays on Checklist Z2–Z4 — not this map.

