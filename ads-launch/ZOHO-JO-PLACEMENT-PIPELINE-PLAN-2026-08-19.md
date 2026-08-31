# Virtual Coworker — Job Order / Placement → Google Ads pipeline

**Mode:** audit and implementation plan only.  
**Generated:** 19 August 2026.  
**Live changes:** none. Zoho records, workflows, Ads settings, conversion actions, Data Manager connections, landing pages, and production env vars were not modified. No conversions uploaded. No email or SMS sequences activated.

**Read-only evidence this pass**

- Zoho CRM v8 GET + COQL (`probe_zoho_jo_placement_pipeline_readonly.py`, 55 calls). `ZOHO_CRM_ENABLED` stayed false.
- Google Ads conversion-action settings only (`probe_ads_zoho_conv_actions_readonly.py`, **2 GAQL calls**). US `496-715-1855`, AU `573-539-1940`. No metrics, campaigns, keywords, or mutations.
- Prior dictionaries: 13 Aug field map, 17 Aug LP write recap, 18 Aug lead-to-placement census.

---

## 1. Executive summary

The two Ads actions that are already connected are **not** “Job Order module + Placement module.”

They are enquiry **statuses** on Sales Enquiries (`Leads`):

| What people say | What actually exists |
|-----------------|----------------------|
| “Job Order conversion” | `Zoho JO Submitted [Standard OCI]` + Zapier twin, filtered on **Lead_Status = Job Order Submitted** |
| “Placement conversion” | **Does not exist** in either Ads account (verified 19 Aug). The second live Data Manager feed is **Discovery Scheduled**, not Placement |

A Sales Enquiry marked Job Order Submitted is **not** the same object as a `Job_Orders` row. A Job Order stage labeled Placement is **not** the same object as a Placements (`Deals`) row.

You cannot send verified Placements into Google Ads today without George approving a **new** conversion action (this brief forbids creating or renaming actions). Do not hijack Discovery Scheduled for that.

Click IDs almost never survive the hop: **222 / 638** enquiries in 90 days have `utm_gclid`; **18 / 231** Job Orders have `UTM_Gclid`; **0** Placements have a click-id field. Email on Job Orders is strong (**229 / 231**) and can support enhanced conversions for leads **after** the enquiry click is copied forward.

**Safest path (after approval, not now):** keep Data Manager; freeze Zapier twins; copy click id + market from the enquiry onto the Job Order; retarget the existing JO Standard OCI actions to the **Job_Orders module**; create Placement actions only when George says so; stay on Maximize Clicks.

---

## 2. Verified module / field / relationship map

Org: **Virtual Coworker** · one customized Zoho CRM · USA + Australia · timezone **Australia/Brisbane** · currency AUD.

| UI name | API name | Kind | Role |
|---------|----------|------|------|
| Sales Enquiries | `Leads` | renamed standard | Front door |
| Job Orders | `Job_Orders` | custom module | Recruiting request |
| Placements | `Deals` | renamed standard | After-hire / ops |
| Accounts | `Accounts` | standard | Company |
| Contacts | `Contacts` | standard | People dump |
| Recruitments | `Job_Openings` | webtab, `api_supported=false` | Recruit, barely visible |
| Google Ads | `Google_AdWords` | `api_supported=false` | Not proof the connector is on |

Standard convert (`Converted__s`) is almost unused (**1 in 90 days** on 18 Aug). Live path: keep the enquiry, create a Job Order.

```text
Search / ad click
    → landing-page form (.app create-only since 17 Aug, or WordPress / Lois / human)
    → Sales Enquiry (Leads)
         Region USA|AU · utm_gclid · Email · Phone
         Lead_Status is a human label (Job Order Submitted ≠ a Job Order row)
    → Job Order (Job_Orders)
         Client_Name lookup → that enquiry (225 / 231 in 90d; 6 unlinked)
         UTM_Gclid rarely copied (18 / 231)
         Stage includes Placement | Job Order Cancelled | Sourcing …
    → Placement (Deals)
         Account_Name → Account · Contact_Name → Contact
         NO Job Order lookup · NO click-id field
```

### Fields that matter for Ads matching

| Need | Enquiry (`Leads`) | Job Order | Placement (`Deals`) |
|------|-------------------|-----------|---------------------|
| GCLID | `utm_gclid` (not `$gclid`) | `UTM_Gclid` (different name) | **missing** |
| GBRAID / WBRAID | **no fields** | **no fields** | **no fields** |
| Email | `Email` | `Email` (99% in 90d) | `Work_Email` / `Personal_Email` |
| Phone | `Phone` | `Phone_1` (8 / 231) | `Work_Phone` / `Mobile` / `Home_Phone` |
| Company | `Company` | `Company_Name` (text) | via `Account_Name` |
| Market | `Region` USA / AU | `Region` | `Region` (42 / 109 blank in 90d) |
| UTM source…term | `utm_*` | `UTM_*` (Pascal) | **missing** |
| Landing URL | `Referring_URL` (not a Landing_Page field) | — | — |
| Enquiry id | `id` | `Client_Name` lookup | **missing** |
| Job Order id | — | `id` (+ text `Job_Order_ID`) | **missing** |
| Placement id | — | — | `id` |
| Milestone time | `Created_Time` / `Submission_Timestamp` | `Created_Time` / `Submission_Date` | `Created_Time` / `Start_Date` / `Stage_Modified_Time` |
| Dedupe / submit id | `Gravity_Form_Entry_ID` (used by `.app`) | — | — |
| Consent | `Email_Opt_Out` (0 true in 90d — not marketing-consent proof) | `Email_Opt_Out` | Twilio SMS opt-out fields |

`Linked_Sales_Enquiry` and `Linked_Account` on Job Orders are **text**, not lookups.

Layouts, pipelines, blueprints, workflows, functions, and webhooks: **this token cannot read them** (`settings.fields` / `modules` / `coql` only). HTTP 401 or 404 on every automation endpoint this pass. Ash must screenshot those in the Zoho UI.

---

## 3. Current Google Ads / Data Manager inventory

**Accounts (keep separate):** MCC `119-318-9031` · USA `496-715-1855` · AU `573-539-1940`.

**Verified 19 Aug 2026** — no conversion action in either account has “Placement” in the name.

### Live CRM-shaped actions (do not create / rename / change from this plan)

| Acct | Name | ID | Source | Type | Primary | In Conv col | Count | Click window | Value on disk |
|------|------|----|--------|------|---------|-------------|-------|--------------|---------------|
| US | Zoho JO Submitted US [Standard OCI] | 7556921934 | Data Manager / native Zoho | `UPLOAD_CLICKS` | No | No | MANY_PER_CLICK | 90d | $1, not forced |
| US | Zoho JO Submitted US [Original] via Zapier | 7387464177 | Zapier | `UPLOAD_CLICKS` | No | No | ONE_PER_CLICK | 90d | $0 forced |
| US | Zoho Discovery Scheduled US [Standard OCI] | 7556617802 | Data Manager | `UPLOAD_CLICKS` | No | No | MANY_PER_CLICK | 90d | $1, not forced |
| US | Zoho Discovery Scheduled US [Original] via Zapier | 7387413269 | Zapier | `UPLOAD_CLICKS` | No | No | ONE_PER_CLICK | 90d | $0 forced |
| AU | Zoho JO Submitted AU [Standard OCI] | 7556033964 | Data Manager | `UPLOAD_CLICKS` | No | No | MANY_PER_CLICK | 90d | $1, not forced |
| AU | Zoho JO Submitted AU [Original] via Zapier | 7387454826 | Zapier | `UPLOAD_CLICKS` | No | No | ONE_PER_CLICK | 90d | $0, not forced |
| AU | Zoho Discovery Scheduled AU [Standard OCI] | 7555860946 | Data Manager | `UPLOAD_CLICKS` | No | No | MANY_PER_CLICK | 90d | $1, not forced |
| AU | Zoho Discovery Scheduled AU [Original] via Zapier | 7387322815 | Zapier | `UPLOAD_CLICKS` | No | No | ONE_PER_CLICK | 90d | $0 forced |

**Not a Placement action:** AU historic metric `Converted Job Orders (Recruiting)` (1 / 56 over 2024-08-01–2026-08-12) is **absent** from the current non-REMOVED action list. Treat as museum. AU also still has a hidden UA goal `Job order form filled out` — website form, not CRM.

**Data Manager (UI observation, not API):** George reauthorized the Zoho cards on 17 Aug. Named live Leads connections: JO Submitted Standard OCI + Discovery Scheduled Standard OCI. Exact filter JSON, schedule, last successful import, and current error counts **cannot be read** from CRM metadata or these two Ads calls. Last team note: “1 issue” on each Leads connection — matching fails when the lead has no click id.

**Do not use a custom Google Ads API uploader.** The native / Data Manager path is already authorized and live. A second uploader would double-count unless Zapier + OCI are frozen and proven distinct.

George types Job Order and Placement **values** in the Ads UI. This plan does not guess them.

---

## 4. Data-quality scorecard

Window: last 90 days from 19 Aug 2026 (Created_Time ≥ 2026-05-21 UTC). Org clock is Brisbane.

| Stage | 90d | Email | Phone | GCLID | Market blank | Notes |
|-------|----:|------:|------:|------:|-------------:|-------|
| Sales Enquiries | 638 | 617 (97%) | 606 (95%) | 222 (35%) | 28 (4%) | Follow-up date blank on **all 638** |
| Enquiry status = Job Order Submitted | 205 | — | — | — | — | **Status, not a Job Order row** |
| Enquiry status = Discovery Scheduled | 5 | — | — | — | — | What Data Manager #2 actually watches |
| Job Orders module | 231 | 229 (99%) | 8 (3%) | 18 (8%) | 4 (18 Aug) | 6 unlinked to an enquiry |
| JO Stage = Placement | 92 | — | — | — | — | Stage label, not a Deals row |
| Placements module | 109 | Work 45 / Personal 46 | newest-30 phone 0 | **0 field** | 42 (39%) | 41 no Account · 43 no Contact |

18 Aug volume (for trend): Enquiries 639 / JO 236 / Placements 108. Today’s 90d window rolled forward one day; counts are stable.

### Newest 30 (19 Aug)

| Module | Email | Phone | GCLID | Unmatchable (no click + no email + no phone) |
|--------|------:|------:|------:|--------------------------------------------:|
| Sales Enquiries | 28 | 28 | 5 | 0 |
| Job Orders | 30 | 8 | 5 | 0 |
| Placements | 3 | 0 | 0 | **27** |

Attribution hop (8 newest Job Orders): **0 region mismatches** on the 7 linked rows. **1 unlinked** USA Job Order. **0 of 8** had `UTM_Gclid`. One linked enquiry was still **New Enquiry (Auto)** — a Job Order can exist without the enquiry status Data Manager watches.

Three `[TEST]` rows (do not touch): all still **New Enquiry (Auto)**, not converted, no gclid.

```
6724032000029820001  [TEST] Virtual Coworker API
6724032000029822001  [TEST] LP US — Do not contact
6724032000029823001  [TEST] LP US consult — Do not contact
```

---

## 5. Red-flag checklist

| # | Flag | Verdict | Evidence |
|---|------|---------|----------|
| R1 | Status mistaken for milestone record | **Open** | 205 enquiry “JO Submitted” vs 231 Job Orders vs 3 JO-stage “Job Order Submitted” (18 Aug). 92 JO-stage Placement vs 109 Deals. |
| R2 | Missing click id **and** missing email/phone | **Partial** | Enquiries newest-30: 0. Placements newest-30: **27 / 30**. 90d “both null” COQL rejected (AND-null parse). |
| R3 | USA/AU account mismatch | **Watch** | Hop sample 0 mismatches. 28 enquiries + 42 placements have blank Region — those cannot be routed. |
| R4 | Duplicate conversion risk | **Open** | Zapier + Standard OCI twins still ENABLED. Data Manager watches enquiry status; a later Job_Orders feed would fire again. |
| R5 | Data Manager and Zapier same milestone | **Open** | Same names, both ENABLED, both Secondary. Historic 2y: US JO Zapier 67 / OCI 23; AU 36 / 14. |
| R6 | Workflows strip attribution | **Unknown** | Automation APIs 401/404. Observed fact: gclid dies between enquiry (35%) and JO (8%). |
| R7 | Job seekers in employer pipe | **Unknown** | No seeker field. `Resume` status = 0. Junk 92 + Not a Fit 97 in 90d — mix unknown. Ask Ash. |
| R8 | Missing company | **Low** | 15 / 638 enquiries. |
| R9 | Disconnected JO / Placement | **Open** | 6 / 231 JO unlinked. Deals have **no JO lookup**. 41 / 109 Deals no Account. |
| R10 | Wrong timestamps / TZ | **Watch** | CRM Brisbane. Ads click window 90 days. Must send **milestone** time, not upload time. |
| R11 | Old clicks outside import window | **Open** | Any JO/Placement whose original click is >90 days old will fail or drop. |
| R12 | Test records in prod workflows | **Contained for the 3 IDs** | Still New Enquiry. Other tests (`job test`, `agent assign test`) sit in live JO stages. |
| R13 | No Placement conversion action | **Blocker** | 0 Placement-named actions US + AU (19 Aug). |

---

## 6. Yellow-flag checklist

| # | Flag | 90d signal | Owner later |
|---|------|------------|-------------|
| Y1 | Employer enquiry, no next action | New Enquiry (Auto) 10 · Follow-up date **0 / 638** | Cheyenne / Holly |
| Y2 | Stalled qualified companies | Qualification_Status unused (0 / 90d on 18 Aug) | Ash / Caitlin |
| Y3 | Incomplete but recoverable | JO email 99%, phone 3%; copy phone + gclid from enquiry | Cursor after approval |
| Y4 | Previous / returning customers | JO Client_Status: Returning 13 · Replacement 15 · Additional Hire 34 | Sales |
| Y5 | Lost / dormant still relevant | Unresponsive 113 · Not Ready 22 · Brochure 55 · Not a Fit 97 | Sales — do not auto-nurture |
| Y6 | Job Orders without a Placement | 231 JO vs 109 Deals; 92 JO at stage Placement | Ops definition needed |
| Y7 | Email/phone but no click id | ~65% of enquiries; still ECL-eligible | Data Manager matching |
| Y8 | No owner / follow-up date | Follow-up unused. Owners usually Cheyenne / Holly / Caitlin | Sales |
| Y9 | Blueprint vs Lead_Status drift | 21 / 80 newest disagreed on 18 Aug | Ask which is truth |
| Y10 | Lois / WordPress still the volume path | Social Marketing created most newest Website rows on 18 Aug | Do not touch WP |

---

## 7. Duplicate / import-risk analysis

```text
One paid click
  → VC_US_Thank_You / VC_AU_Thank_You          (online, Stage 1 pipe)
  → Zoho Discovery Scheduled  Zapier + OCI     (enquiry status)
  → Zoho JO Submitted         Zapier + OCI     (enquiry status)
  → (future) Job_Orders module feed            WOULD BE A FIFTH METER
  → (future) Placement feed                    sixth
```

Rules for any go-live:

1. **One milestone = one action per market.** Freeze or disconnect the Zapier twin before retargeting OCI.
2. Do not also fire on enquiry status **and** Job_Orders create.
3. Dedup key = module record id, not enquiry id (one enquiry can have many JOs: Additional Hire / Replacement).
4. Count setting: prefer **ONE_PER_CLICK** on the surviving JO action if George wants one paid click → one JO credit. Current OCI is **MANY_PER_CLICK** (replacements would count again). That is a George decision — do not change it from here.
5. Never upload a USA click into AU or the reverse. Route by `Region` on the **enquiry**, then confirm the same Region on the Job Order. Blank Region = hold, do not send.
6. Exclude `[TEST]`, `API Integration Test`, and the three locked IDs.
7. Do not attach any Zoho upload to `VC_*` campaign goals. Keep them Secondary until George says otherwise.
8. Do not switch Maximize Clicks → Maximize Conversions.

---

## 8. Proposed Job Order pipeline

**Triggering object:** `Job_Orders` row, **not** `Leads.Lead_Status`.

**Recommended condition (Ash + Caitlin must confirm one):**

- Preferred: Job Order **created** and `Client_Status` in `New Client` / `Additional Hire` / `Replacement Role` / `Returning Client`, and `Stage` ≠ `Job Order Cancelled` / `Cancelled NHI`.
- Alternative: first time `Stage` leaves a draft and is not cancelled.
- **Reject:** enquiry status Job Order Submitted as the Ads trigger.

**Ads account**

| Region on the **linked enquiry**, else on the JO | Action to use (existing) |
|--------------------------------------------------|--------------------------|
| USA | `Zoho JO Submitted US [Standard OCI]` `7556921934` |
| AU | `Zoho JO Submitted AU [Standard OCI]` `7556033964` |
| blank or disagree | **Do not send** |

**Do not** also send to the Zapier twins.

**Timestamp:** `Job_Orders.Created_Time` (or Caitlin’s approved milestone datetime). Convert to the timezone Ads expects. Do not use upload time.

**Attribution identifiers (in priority order)**

1. `Job_Orders.UTM_Gclid` if present  
2. else linked enquiry `Leads.utm_gclid` via `Client_Name`  
3. else hashed email (`Job_Orders.Email` or enquiry `Email`) + hashed phone for enhanced conversions for leads  
4. GBRAID / WBRAID: **cannot send until fields exist** (fold into enquiry notes today)

**Dedup key:** `vc_jo_{Job_Orders.id}`  
Never `enquiry id`. Never company name.

**Retry / failure:** Data Manager native retry. Ash logs weekly: sent / matched / unmatched / error. Cursor does not build a custom uploader.

**Audit log (proposed, not built):** append-only file or Zoho note on the Job Order: action id, account, timestamp sent, identifier type (gclid vs ECL), result. No writes until approved.

**Corrections / cancellations:** if Stage later becomes Cancelled, send a **conversion adjustment** (retract) on the same order id. Do not upload a negative value as a new conversion. George approves adjustments separately.

**Historic backfill:** last **90 days** only (click window). Exclude tests, cancelled, blank Region, and rows with no gclid and no email. Cap and review the list with Caitlin before any backfill. Default: **no backfill** — go-forward only.

**Test exclusion:** company / name contains `[TEST]`; Form_Source `API Integration Test`; the three locked enquiry IDs; owner George Aguilar + New Enquiry (Auto) from `.app` tests.

**Duplicate prevention:** pause Zapier JO zaps (human in Zapier UI); keep one OCI action; one order id; do not also key off enquiry status.

**Prerequisite before the filter change:** a Zoho automation that copies `utm_gclid`, `utm_*`, `Region`, `Email`, `Phone` from the linked enquiry onto the Job Order **without overwriting a filled JO field**. That is a CRM write. Not in this pass.

---

## 9. Proposed Placement pipeline

**Blocked for Ads send until George approves a new conversion action.**

There is no Placement action to point Data Manager at. Discovery Scheduled is the wrong object (5 enquiry rows in 90 days vs 109 Placements).

**Design to implement after that approval**

| Item | Spec |
|------|------|
| Triggering module | `Deals` (UI: Placements) |
| Condition | Caitlin names the real hire event. Candidates: record created at `New Placement`, or `Start_Date` set, or `Contract_Invoice_Status` = (unknown — ask). Exclude `Cancelled`. |
| Account | Same Region rule as JO. Blank Region = hold (**42 / 109** today). |
| Action | **Does not exist.** George creates `Zoho Placement US` / `Zoho Placement AU` in the Ads UI when ready. Cursor does not create them. |
| Timestamp | `Start_Date` if filled, else `Created_Time` |
| Identifiers | Walk back Job Order (once a lookup exists) → enquiry `utm_gclid` / email / phone. Today that walk is **impossible** in schema. |
| Dedup key | `vc_pl_{Deals.id}` |
| Retry / audit / retract | Same pattern as JO |
| Backfill | None until the action exists and the JO lookup exists |
| Test exclusion | Same `[TEST]` rules; also Placement names like `Owner` / `Manager` / `CFO` with no Account |

**Schema prerequisite:** add a lookup `Job_Order` on `Deals` → `Job_Orders`. Without it, Placement cannot carry a click id. That is a George/Ash CRM change.

Until then: **do not send Placements.**

---

## 10. Ash / Claude handoff

See `ads-launch/ASH_ZOHO_AUDIT_HANDOFF.md`.

---

## 11. Nurture opportunity plan (prepared, not activated)

Do not turn on email or SMS. Sinch/Twilio fields exist on Placements — leave them.

Consent: `Email_Opt_Out` is unused (0 / 638). That is **not** permission to market. Require a real consent field or a human opt-in before any send. Suppress `[TEST]`, Junk, job-seeker-once-defined, and anyone who asked to stop.

| Segment | Entry | Exclude | Owner | Purpose (draft only) | Consent | Exit | Human handoff | Measurement |
|---------|-------|---------|-------|----------------------|---------|------|---------------|-------------|
| New employer enquiry | `Lead_Status = New Enquiry (Auto)` · has company · not test | Junk, seeker, `[TEST]`, no email | Cheyenne USA / Holly AU | Confirm receipt + book discovery | Explicit | Discovery booked or 7 days | Owner call task | Not an Ads conversion |
| Qualified / stalled | Human-marked useful · no JO in 14 days · follow-up blank | Not a Fit, Unresponsive if they said no | Same | One reminder, then stop | Explicit | JO created or Not Ready | Owner | Not Ads |
| Open Job Orders | `Job_Orders` not Cancelled / not Placement | Tests, no client lookup | Caitlin + recruit | Ops updates only, not marketing | Client relationship | Stage Placement or Cancelled | Recruit | Future JO action already covers create |
| Previous customers | `Client_Status = Returning Client` | Opt-out, legal hold | Account owner | Reorder / extra seat | Existing client terms | New JO | Owner | Additional Hire JO (if MANY_PER_CLICK allowed) |
| Repeat-placement | `Replacement Role` or `Additional Hire` | Cancelled | Same | Seat change, not a new lead | Client terms | JO created | Owner | Same as JO pipeline |
| Dormant enquiries | Unresponsive or Brochure · >30 days · had company | Junk, seeker, `[TEST]` | Same | One reactivation, then stop | Explicit | Reply or opt-out | Owner | Not Ads |
| Lost but relevant | Not a Fit + company still real · Ash confirms | Job seeker, competitor, spam | Same | Do not automate | Explicit | Owner says yes | Owner only | Not Ads |

**Hard no:** auto-move `[TEST]` rows; auto-set Discovery Scheduled or Job Order Submitted; SMS until consent is proven; WordPress/legacy funnels.

---

## 12. Exact proposed changes, files, and systems

**This pass (done, read-only)**

- `ads-launch/probe_zoho_jo_placement_pipeline_readonly.py`
- `ads-launch/probe_ads_zoho_conv_actions_readonly.py`
- `ads-launch/ASH_ZOHO_AUDIT_HANDOFF.md`
- this file
- raw: `.local/zoho/audit-jo-placement-pipeline-2026-08-19.json`, `.local/ads/conv-actions-2026-08-19.json`

**After George approves — CRM (Ash / Caitlin, not Cursor writes)**

1. Screenshot Data Manager filters, schedule, last import, error reasons (US + AU).
2. Confirm Zapier JO / Discovery zaps on or off.
3. Decide the real JO trigger (module create vs stage).
4. Optional workflow: copy enquiry `utm_gclid` → JO `UTM_Gclid` if empty; copy email/phone/Region.
5. Optional field: `Deals` lookup to `Job_Orders`.
6. Optional fields: `utm_gbraid`, `utm_wbraid` on Leads (and copy to JO).

**After George approves — Ads UI (George only)**

7. Pause or disconnect Zapier twins if still on.
8. Retarget Data Manager JO connections from `Leads.Lead_Status` to `Job_Orders` (do not rebuild the cards).
9. Leave Discovery connections Secondary or freeze them — they are not Placement.
10. Create Placement actions **only if** George wants Placement in Ads. Cursor will not create them.
11. Type JO / Placement dollar values. Do not change Primary/Secondary or bidding from this workstream.

**Not proposed**

- Custom Ads API conversion uploader
- `ZOHO_CRM_ENABLED=true`
- WordPress / organic stack work
- Maximize Conversions
- Touching the three `[TEST]` IDs

---

## 13. Test and rollback plan

**Test (after approval)**

1. Keep `[TEST]` enquiries at New Enquiry (Auto). Confirm they still do not appear in Data Manager.
2. Ash picks **one** real Job Order Caitlin vouches for, with a stored gclid, Region filled, not cancelled.
3. Dry-run: show the payload (masked) — account, action id, timestamp, order id, identifier type. No upload.
4. If George says go: one Secondary send via existing Data Manager, not Zapier, not a new uploader.
5. Wait for Ads lag. Confirm one conversion on the correct account only.
6. Placement test waits for an action + JO lookup.

**Rollback**

- Data Manager: revert the filter to the previous Leads-status filter (screenshot first).
- Zapier: leave off if it was off; do not turn it back on to “fix” volume.
- CRM workflow: disable the copy-gclid rule; it must not overwrite filled fields.
- Ads: leave actions Secondary; do not delete museum actions.
- No CRM record cleanup as rollback.

---

## 14. Blockers and decisions George must approve

1. **What is a Job Order for Ads?** Enquiry status, `Job_Orders` row, or both? This plan recommends the **module row only**.
2. **What is a Placement for Ads?** JO stage Placement, `Deals` row, `Start_Date`, or invoice signed? `Contract_Invoice_Status` meaning is unknown.
3. **Create Placement conversion actions?** Required to send Placements. This brief currently forbids creating them.
4. **Freeze Zapier twins?** Required to avoid double-count if OCI is retargeted.
5. **Retarget Data Manager** from Leads status → Job_Orders module? Filter change, not a rebuild.
6. **Allow a CRM workflow** that copies gclid/email/phone/Region onto Job Orders (fill-if-empty only)?
7. **Add a Job Order lookup on Placements?** Required for Placement matching.
8. **ONE_PER_CLICK vs MANY_PER_CLICK** on JO (replacements / extra seats)?
9. **Go-forward only vs 90-day backfill?**
10. **Ash Zoho seat** (read-only) so Claude can see layouts/workflows this token cannot?
11. **Nurture:** none until consent + exclusions are written. Not this week’s money path.
12. **Values:** George types them in Ads. Nobody else.

Do not implement any of 1–11 until George says so in this conversation.

---

AUDIT COMPLETE — NO LIVE CHANGES MADE
