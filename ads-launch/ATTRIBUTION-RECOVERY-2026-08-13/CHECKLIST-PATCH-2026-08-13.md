# Checklist patch — 13 August 2026 (local only)

**Not deployed.** George overrode X-ray deploy for this pass.

Source of truth for the operator UI: `xray/launch-control.html`.
Companion recovery list: `ads-launch/ATTRIBUTION-RECOVERY-2026-08-13/CHECKLIST.md`.

Preserve existing items. No auto-checks. No Broad / PMax / DSA / Max Conv / budget / Brand enable.

---

## Why these changes (justified only)

| Change | Why it is justified now |
|--------|-------------------------|
| Correct Calendly booked wording | Earlier recovery text said the **site** has no booked listener. That is still true of Vision code. Published GTM **does** listen (`calendly.event_scheduled` → `calendly_event_scheduled`) on US v6 and AU v6. Existence ≠ firing. |
| Correct US thank-you (B) | Morning Ads inventory already has `VC_US_Thank_You`. Live GTM v6 maps `employer_inquiry_submitted` (not the alias) to an Ads conversion tag. Still **not** proven to fire. |
| Correct AU thank-you (D) + #16 hint | AU GTM v6 has a thank-you Ads tag **and** a website-call forwarding config for 1300. Morning Ads inventory still lacked `VC_AU_Thank_You` and AU 60s **actions**. Do not check #16. |
| Add four attribution items (unchecked) | Campaign-specific level is now API-verified; 782 is the wrong import denominator; Zapier/OCI overlap still unknown; Preview still required. |
| Hint on optional “demote old Zoho Primary” | 13 Aug inventory already has Zapier/OCI JO as Secondary. US `VC_*` `CONVERTED_LEAD` is not biddable. |

Do **not** check F, B, C, D, #16, #17, or Z6 from this pass.

---

## Exact diff — `xray/launch-control.html`

### 1. B (`ads51`) hint — replace stale “create in Ads”

**Before:** “Open — not live until you create it in Ads + publish GTM…”

**After:** Action `VC_US_Thank_You` exists (13 Aug inventory). Published GTM-M92DX9BJ v6 maps `employer_inquiry_submitted` only (not `form_submit_success`, not page view). Firing still unproven — GTM Preview one submit. Stay on Maximize Clicks.

### 2. D (`ads53`) hint — GTM tag exists; Ads action lag

**Add:** Published GTM-5T6KPVSF v6 already has an Ads conversion tag on `employer_inquiry_submitted`. Morning Ads inventory (16:03 UTC) did **not** list `VC_AU_Thank_You`. Confirm the AU action exists in the Ads UI before treating D as done. Firing unproven.

### 3. F (`ads70`) hint — GTM listens; site does not

**Before:** “Site already pushes Calendly… Ads action + GTM map can still be tightened later”

**After:** Vision code still only tracks overlay open (`calendly_cta_clicked`). Published GTM (US v6, AU v6) **does** listen for `calendly.event_scheduled` and has Ads conversion tags on `calendly_event_scheduled`. Existence ≠ firing. George still ticks F; we do not auto-check. Next Ads after F remains #16.

### 4. #16 (`ads42`) hint — GTM forwarding present; Ads action not proven

**Add:** Published AU GTM v6 already includes a website-call Google tag with `phone_conversion_number` 1300 886 740. Morning Ads inventory still had **no** AU 60s website-call **action**. Create/confirm the action in AU Ads UI. Do not check this box from GTM alone.

### 5. Item 21 (`ads28`) hint

**Add:** 13 Aug inventory: Zapier + Standard OCI JO are already `primary_for_goal=false`. US `VC_*` campaign conversion goals have `CONVERTED_LEAD` **not** biddable. Optional leftover: confirm they stay unattached. Do not delete museum actions.

### 6. New items (after Z6, before E) — all unchecked

- **AR1.** Amanda: screenshot campaign goals on all four `VC_*`. API: `goal_config_level=CAMPAIGN`. US biddable = phone + submit-form only. AU category map UNKNOWN.
- **AR2.** Do not import or score CAC off **782** Job Orders. Click-linked only (90d sample: 69 of 200 newest).
- **AR3.** Raffie/Caitlin: is Zapier or Standard OCI **still uploading**? Unknown. Do not test with an upload.
- **AR4.** Raffie: GTM Preview — one `employer_inquiry_submitted` fire and one `calendly_event_scheduled` fire. Listeners exist; firing unproven.

JS: never auto-complete `attrRec1`–`attrRec4`.

### 7. Not changed

Brand defense item 9 (`.com` goals) — different campaign. TRAFFIC READY items. Z1–Z6. E. Enable/budget/Brand.

---

## Exact diff — recovery `CHECKLIST.md` N3

**Before:** “Site currently has **no** booked listener”

**After:** “Vision code has **no** booked listener. Published GTM US v6 / AU v6 **do** listen for `calendly.event_scheduled`. Confirm a test booking hits Ads — existence ≠ firing.”
