# Conversion-action reconciliation — 13 August 2026

Source of truth for this table: `xray/data/recovery-audit.json` and `xray/data/recovery/conversions.csv` (window **1 Aug 2024 – 12 Aug 2026**). Attribution model and last-conversion date: **UNKNOWN** (not in the pull). Campaign-specific attachment on `VC_*`: **UNKNOWN**.

Google Ads API was **not** called again this pass.

**How to read “In Conv col”:** `include_in_conversions_metric`. That is what fills the account-default Conversions column. `primary_for_goal` is a separate flag on disk.

George’s current intent: thank-you, Calendly booked, and 60s phone are pipe checks; $1 placeholders; Primary OK for now; **E is not next**. On-disk inventory may lag later Ads UI work. Do not infer firing from existence.

---

## Answers

1. **What appears in the Conversions column today?**  
   On `VC_*` last 7 days: **0**. Account-default “in column” leftovers are US **eBook** and AU hidden UA goals — all **0** in two years. Historically the column was WordPress forms, thank-you pages, Calendly, calls, chat, and a thin Zoho upload.

2. **Which recent conversions are shallow pipe checks?**  
   `VC_US_Thank_You`, `VC_US_Phone_Click_Website`, `VC_AU_Phone_Click_Website`. Tel taps. Calendly **open**. Thank-you page views if anyone maps URL contains `thank-you` (must not).

3. **Are any actions firing twice?**  
   **Historically yes:** WP form + GA4 thank-you; Zapier + Standard OCI twins (JO and Discovery); AU Original + GA4 form. **Currently on `VC_*`:** 0 + 0, so no live double-fire observed.

4. **Could one form become multiple Primaries?**  
   **Yes if miswired:** thank-you event + form-submit alias + Calendly booked + Zoho offline, all Primary. Site already fires `employer_inquiry_submitted` and alias `form_submit_success` — GTM must map **only** the first. Crafted `/thank-you?sid=` can false-fire once per id.

5. **Are historical account-default goals silently attached to `VC_*`?**  
   **UNKNOWN.** If inherited, the only `include_in_conversions_metric: true` leftovers are junk with 0 volume. Still isolate goals in the Ads UI.

6. **US / AU separation?**  
   Separate customer IDs (`496-715-1855` / `573-539-1940`), separate GTM/GA4. Leak: AU account contains empty actions named **“VC US — virtualcoworker.app”**.

7. **Campaign-specific goals configured as intended?**  
   **UNKNOWN.** Planned: only new `VC_*` pipe checks. Editor CSV cannot express this.

8. **Anything influencing bidding that should not?**  
   `VC_*` are **Maximize Clicks** (`TARGET_SPEND`) — not conversion-optimized today. Switching those campaigns to Maximize Conversions while museum defaults remain would be the failure mode. Do not switch.

---

## New `VC_*` system (keep)

| Acct | Name | ID | Type | Status | Primary | In Conv col | Count | Window | Value | Conv / All (2y) | Cohort / risk |
|------|------|-----|------|--------|---------|-------------|-------|--------|-------|-----------------|---------------|
| US | `VC_US_Phone_Call_From_Ads` | 7713239223 | AD_CALL 60s | ENABLED | Yes | No | One | 30d | $0 | 0 / 0 | Pipe check. 0 fires in window. |
| US | `VC_US_Phone_Call_From_Website` | 7716194324 | WEBSITE_CALL 60s | ENABLED | Yes | No | One | 30d | $100 on disk | 0 / 0 | Label `Sf71CJSQr98cEOPyhMsD`. George later wants $1 placeholders — **UNKNOWN** if UI already changed. |
| US | `VC_US_Phone_Click_Website` | 7713281413 | CLICK_TO_CALL | ENABLED | Yes | No | One | 30d | $0 | 0 / 2 | Tap ≠ 60s. |
| US | `VC_US_Thank_You` | 7718196602 | WEBPAGE | ENABLED | Yes | No | One | 90d | $1 | 0 / 0 | GTM map **UNKNOWN**. Do not also map `form_submit_success`. |
| AU | `VC_AU_Phone_Click_Website` | 7719216886 | GA4_CUSTOM | ENABLED | Yes | No | One | 90d | $1 | 0 / 0 | Shallow. Not a 60s call. |
| AU | `VC_AU_Thank_You` | — | — | **Not in 13 Aug inventory** | Intended | — | — | — | — | — | Create-in-UI was still open on disk. |
| AU | AU website-call 60s | — | — | **Missing** | Intended | — | — | — | — | — | Checklist #16. |
| AU | AU ad-call 60s | — | — | **Missing** | Intended | — | — | — | — | — | Checklist #17. |
| US/AU | `VC_*_Calendly_Booked` | — | — | **Not in 13 Aug inventory** | Intended Secondary | — | — | — | — | — | Site has **no booked listener**. |

Empty GA4 auto-imports named `VC US — .app close_convert_lead / purchase / qualify_lead` (and AU copies): HIDDEN, 0, **museum noise**. Do not use.

---

## Historical museum — do **not** attach to `VC_*`

| Acct | Name | ID | Type | Primary | In Conv col | Conv / All (2y) | Overlap / risk |
|------|------|-----|------|---------|-------------|-----------------|----------------|
| US | Zoho JO Submitted US [Original] via Zapier | 7387464177 | UPLOAD_CLICKS | No | No | **67 / 125** | Best CRM-shaped Ads number. **Unverified.** Not a census of 782 JOs. |
| US | Zoho JO Submitted US [Standard OCI] | 7556921934 | UPLOAD_CLICKS | No | No | **23 / 85** | Twin of Zapier. Double-count if both live. |
| US | Zoho Discovery Scheduled US [Zapier] | 7387413269 | UPLOAD_CLICKS | No | No | 33 / 317 | Twin with OCI Discovery. |
| US | Zoho Discovery Scheduled US [Standard OCI] | 7556617802 | UPLOAD_CLICKS | No | No | 1 / 109 | Twin. |
| AU | Zoho JO Submitted AU [Original] via Zapier | (see recovery CSV) | UPLOAD_CLICKS | No | No | **36 / 69** | Same story as US. |
| AU | Zoho JO Submitted AU [Standard OCI] | (see recovery CSV) | UPLOAD_CLICKS | No | No | **14 / 51** | Twin. |
| AU | Zoho Discovery Scheduled AU [Zapier] / [Standard OCI] | — | UPLOAD_CLICKS | No | No | 48 / 231 and 3 / 19 | Twins. |
| US | Free Consultation Form Submitted [Original] | 6874549832 | WEBPAGE | No | No | 1036 / 1843 | WordPress. Overlaps GA4 thank-you. |
| US | GA4 contact_us___thank_you_page | removed | — | — | — | 788 / 837 | Removed; still in 2y metrics. |
| US | LK - Scheduled Calendly Call | removed | — | — | — | 373 / 457 | Museum booked signal. Not the new F action. |
| US | Calls from Ads* | removed | — | — | — | 241 / 271 | Legacy 60s unverified. |
| US | Clicks "I am searching for a job" | removed | — | — | — | 0 / **54** | **Confirmed job-seeker conversion.** |
| AU | Free Consultation Form Submitted [Original] + [GA4] | — | WEBPAGE / GA4 | No | No | 944 / 1154 and 232 / 1156 | Triple-count form risk. |
| AU | Chat Opened / Chat Started Oct 2023 | removed | — | — | — | 0 / 184 and 0 / 164 | Chat ≠ lead. |
| US | eBook Download (All Web Site Data) | 314649573 | UA_GOAL HIDDEN | **Yes** | **Yes** | 0 / 0 | Junk Primary still in column flag. |
| AU | Chat / Submission ×2 / Job order form / Lead Form Submit / Transactions | UA HIDDEN | UA | **Yes** | **Yes** | 0 / 0 | Junk Primaries still in column flag. |

Full 67-row dump: `xray/data/recovery/conversions.csv`.

---

## Hard rules (unchanged)

- Do not attach Zoho/Zapier / Standard OCI / UA / old Calendly / job-seeker click to `VC_*`.
- One inquiry ≠ two Primaries.
- Do not switch Maximize Clicks → Maximize Conversions on this CRM.
- E (form $ matrix) is not next.
- Leave museum actions in the account for history. Do not delete them in this pass.
