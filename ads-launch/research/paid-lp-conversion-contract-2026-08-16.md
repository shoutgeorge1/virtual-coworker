# Conversion contract — current production (preserve exactly)

Inspected 16 Aug 2026 from live `vision/` code. **Do not change IDs, labels, aliases, or when events fire.** These local replacement mocks implement the same contract; they do not publish GTM or touch `/us` `/au`.

## Routes and destination

| Piece | Production |
|---|---|
| Submit | `POST /api/lead` JSON (`vision/app/api/lead/route.ts`) |
| Success destination | `/thank-you?market={us\|au}&sid={submission_id}` + optional `category`, `variant`; `eligible=0` if not conversion-eligible |
| Thank-you | `vision/app/thank-you/page.tsx` · noindex · Calendly overlay for us/au |
| Calendly (thank-you only) | US `https://calendly.com/cheyenne-virtualcoworker/30min` · AU `https://calendly.com/apac-virtualcoworker/30min` (env override allowed). Booking click is **not** Ads Primary. |
| Job-seeker exit | `https://virtualcoworker.com.ph` via `job_seeker_redirected` |
| Privacy / terms | `/privacy` `/terms` on `.app` |

Do not fire `employer_inquiry_submitted` until `/api/lead` returns `ok` + `submission_id`. Do not POST to Zoho from these mocks.

## Required JSON fields (`LeadInput`)

Server requires: `market` `us|au`, `intent` `employer`, `name`, `email`, `phone`. Optional: `company`, `company_website`, `role`, `category`, `variant`, `company_size`, `positions_needed`, `schedule`, `hiring_timeline` / `timeline`, `message`, `lp_surface`, `lp_version`, `lp_variant`, attribution (UTM + `gclid` `gbraid` `wbraid` `landing_page_url` `referrer` `captured_at` `submitted_at` `form_started_at`).

**Honeypot:** `website` and `company_url` must be empty. Visible `company_website` is **not** a honeypot and is **not** required.

**Too-fast:** if `form_started_at` is set, submit must be ≥ 2500ms later.

**Qualification IDs already in the API** (feed these; do not invent a new schema):

- `schedule`: `full-time` \| `part-time` \| `mix`
- `company_size`: `1-10` \| `11-50` \| `51-200` \| `201+`
- `positions_needed`: `1` \| `2-3` \| `4-10` \| `11+`
- `role`: copy from `formLabel` (e.g. `Bookkeeping support`, `Administrative / virtual assistant`)
- `category`: slug (e.g. `bookkeeping`, empty on Core)

Phone storage: `normalizePhoneForStorage` → US `+1…`, AU `+61…`.

`lp_version` live stamp: **`stage1-v8`**.

Money LP flags on submit today: `lp_surface: "form"`, `cta_mode: "form_primary"`, `landing_type: "form_lp"`. Replacement mocks that replace `/us` `/au` keep those three so GTM maps stay put. Guided-match diagnostic quiz events use the **existing** `quiz_started` / `quiz_step` / `quiz_completed` names (same as `RoleQuiz.tsx`). They are **not** Ads conversions.

## dataLayer events (canonical + aliases GTM may depend on)

Fire **both** where production does. Do not drop aliases.

| When | Canonical | Aliases already in code |
|---|---|---|
| First contact-field interaction (once) | `employer_form_started` | `form_start` (`alias_of: employer_form_started`) |
| Client validation fail | `employer_form_validation_error` | — |
| `/api/lead` durable success, once per `submission_id` | `employer_inquiry_submitted` | `form_submit_success`, `form_submit` |
| Same sid again | `employer_inquiry_submitted_deduped` | — |
| `conversion_eligible === false` | `employer_inquiry_log_only` (no submitted) | — |
| 502/503 / network / delivery_not_configured | `employer_inquiry_delivery_failed` | — |
| Job-seeker / honeypot / too_fast reject | `spam_or_applicant_rejected` | — |
| `tel:` click | `phone_cta_clicked` (`is_qualified_call: false`) | `phone_click` (`alias_of: phone_cta_clicked`) |
| Thank-you Calendly CTA | `calendly_cta_clicked` | `calendly_click` |
| Careers link | `job_seeker_redirected` | — |
| Quiz diagnostics (not Ads) | `quiz_started`, `quiz_step`, `quiz_completed` | also `lead_magnet_completed` on quiz finish |

Also present on live (not required for these two LPs to auto-fire): `employer_gate_selected`, `experiment_*`, chat/popup assist.

`trackValidEmployerSubmit` writes `primary_eligible: true`, **`bidding_primary: false`**. Do not call this until API success.

## Version One mock (local only — 16 Aug, tightened)

Guided-match diagnostics use **existing** quiz names plus two extra local names. **None of these are Ads conversions.** Do not map them to Google Ads.

| Visitor action | Events | Not |
|---|---|---|
| First guided click (role on Core, or hours/seats on a role page) | `quiz_started` + `guided_match_started` (`alias_of: quiz_started`) + `quiz_step` | `employer_form_started`, Ads |
| Completing hours/seats step | `quiz_step_completed` (`step: "2"`) | Ads |
| Reaching name/email/phone step | `quiz_completed` + `contact_step_reached` + `lead_magnet_completed` | `employer_form_started`, Ads |
| First name / email / phone focus | `employer_form_started` + `form_start` | Unchanged vs production 2/355 comparison |
| Role page (Bookkeeping) | Role locked; chooser skipped; first question is hours/seats | Do not make them pick Bookkeeping again |

Production `/us` `/au`, GTM publish, and Ads stay untouched until George says otherwise.

## Phones (do not invent)

- US display `(888) 964-8644` · `tel:+18889648644`
- AU display `1300 886 740` · `tel:+611300886740`

## GTM / Ads (do not publish, do not retarget IDs)

- US GTM `GTM-M92DX9BJ` · GA4 `G-2V3V0BS6JW`
- AU GTM `GTM-5T6KPVSF` · GA4 `G-7X1K9V2LFE`
- Ads conversion labels / Primary actions / campaign goals: **untouched**

`employer_form_started` is already on the dataLayer. Forwarding it into GA4 remains a **later GTM Preview** task, not this mock.

## Thank-you sid + Refresh

Thank-you page re-calls `trackValidEmployerSubmit`; sessionStorage `vc_primary_fired_ids` dedupes. Mocks must do the same.
