# Conversion plan — VC_US_* / VC_AU_* (Stage 1)

**Status (2026-08-14):** Front-end conversion tracking stays the Ads job. **Zoho + offline conversions are DEFERRED DURING COLD START** — not cancelled, not next. **E form $ is not next.** Stay on Maximize Clicks. Lock: [ZOHO-COLD-START-DEFERRED-2026-08-14.md](./ZOHO-COLD-START-DEFERRED-2026-08-14.md).

**Do not** attach legacy Zoho/Zapier actions to `VC_*` campaigns. `VC_US_S_BRAND` is a separate Paused Editor package (13 Aug audit: TIS 85% · $12 cap · $15/day placeholder). Enable only after `.com` tags are verified. Do not blend brand conversions into CORE/ROLES headlines. Live `Brand_VC` inside CORE stays Enabled until George Approves a split.

Public site numbers (leave these): **US 888-964-8644** · **AU 1300 886 740**. Google forwarding may swap the *displayed* number for Ads visitors only — never publish 888-864 / 888-954 / hardcode a forwarding # as the public number.

---

## Shallow bridge (do first — Conversions column)

Goal: *something* fires so Ads isn’t a desert. These are **pipe checks**, not consultation quality.

| # | Action | Where | Notes |
|---|--------|-------|-------|
| **A** | US phone click stays **Primary** | Ads UI | George lock 2026-08-14: keep `VC_US_Phone_Click_Website` Primary for Stage 1 signal. Do not demote. (Verified Enabled · Primary.) |
| **B** | US thank-you | Ads UI + US GTM | New `VC_US_Thank_You` (Website). Map **only** from dataLayer `employer_inquiry_submitted` (not page view). US GTM already live. **Not live until George creates it in Ads + publishes GTM.** |
| **C** | AU phone click | Ads UI + AU GTM | New `VC_AU_Phone_Click_Website`. Needs Checklist #15 (AU GTM) to fire on `/au`. |
| **D** | AU thank-you | Ads UI + AU GTM | New `VC_AU_Thank_You`. Same map as US. Needs #15. |
| **F** | Calendly booked (consult / strategy call) | Ads UI + GTM | Done enough to **check** on Launch Control (George ticks it — not auto-checked). `VC_US_Calendly_Booked` / AU twin. **Secondary** while thank-you is shallow Primary. Fire on schedule confirmed only. |
| **E** | Ascending form $ | **Not add yet** | Buried. Keep preliminary front-end values separate from unverified CRM outcomes. Do not import to Ads now. |

**Hard truth:** tel: tap ≠ 60s consultation. Thank-you can be spam. Calendly open ≠ booked. Keep Maximize Clicks. **Phone click stays Primary** for Stage 1 signal (George) alongside 60s website/ads call Primaries — do not demote the tap.

---

## What’s live vs open (phone — quality layer)

| Signal | US | AU |
|--------|----|----|
| Call asset on Search (CORE/ROLES) | Live — 888-964-8644 | Live — 1300 886 740 |
| **Calls from ads** 60+ sec (`AD_CALL`) | **Live** — `VC_US_Phone_Call_From_Ads` · Primary · 60s | **Missing** — Checklist #17 (Ads UI only — no GTM required) |
| **Calls from website** 60+ sec (`WEBSITE_CALL` + Google forwarding) | **Live** — `VC_US_Phone_Call_From_Website` · Primary · 60s · $100 · GTM published · Checklist #14 done | **Missing** — Checklist #16 (after AU GTM #15) |
| Tel: / click-to-call (`CLICK_TO_CALL`) | `VC_US_Phone_Click_Website` · **Primary** (A — George lock; Stage 1 signal; tap ≠ 60s) | Create (C) after AU GTM |
| Thank-you / form durable | Create / map (B) | Create / map (D) after AU GTM |
| Calendly booked (consult scheduled) | Create / map (F) — `VC_US_Calendly_Booked` · Secondary · **not firing until GTM mapped** | Create / map (F) — `VC_AU_Calendly_Booked` after AU GTM |
| Microsite forwarding tag / number swap | **Installed** — GTM `AW-962672995/Sf71CJSQr98cEOPyhMsD` + `phone_conversion_number` | No AU GTM yet — Checklist #15 |

Test path for US #14 / AU #16: ad click → LP → **forwarding number shows** → call connects → **60+ sec** → conversion in Ads.  
Verify note (2026-08-10): /us fires gtag + WCM for label `Sf71CJSQr98cEOPyhMsD`; visible number stayed **(888) 964-8644** without a real ad-click cookie (fake `?gclid=test` did not swap).

---

## Measurement order

1. **Shallow A–B (US only)** — phone click Primary (US) + US thank-you. No AU GTM needed.
2. **AU GTM + GA4** — prerequisite (Checklist #15) before any AU website conversions / forwarding. One-step playbook: [AU-GTM-GA4-PLAYBOOK.md](AU-GTM-GA4-PLAYBOOK.md). Site already reads the AU env keys; IDs still need your Google login.
3. **Shallow C–D (AU)** — AU phone click + AU thank-you (after #15).
4. **F — Calendly booked** — done enough to check. Ads + GTM map can still be tightened later.
5. Phone routing — Cheyenne answers US 888-964; AU 1300 answered; missed-call owner.
6. **US website calls 60+ seconds** — **live** (Checklist #14). Not a `tel:` tap. No CallRail required.
7. **AU website calls 60+ seconds** — Checklist #16. Google forwarding, not tel tap. Public # **1300 886 740**.
8. **AU calls from ads 60+ seconds** — Checklist #17. Ads UI only — no GTM required. US already live.
9. **Zoho Qualified / offline import** — **DEFERRED DURING COLD START** (2026-08-14). Read-only monitoring only. No new OCI. No Zapier. No Primary Zoho conversions. Revisit only after the five-item gate.
10. **E — not add yet** — ascending form values / value matrix. After verified front-end signal — not after a Zoho build. Do not import to Ads now.

---

## Named Google Ads conversion actions

| Name | Type | Duration | Count | Status |
|------|------|----------|-------|--------|
| `VC_US_Phone_Call_From_Ads` | Calls from ads | **60s** | One | **Live** · Primary |
| `VC_US_Phone_Call_From_Website` | Calls from website | **60s** | One | **Live** · id `7716194324` · Primary · $100 · label `Sf71CJSQr98cEOPyhMsD` |
| `VC_US_Phone_Click_Website` | Click to call | — | One | **Live** · Primary (George lock — Stage 1 signal; do not demote) |
| `VC_US_Thank_You` | Website / GTM | — | One | **Create (B) in Ads UI** — shallow · ID/label TBD · not live yet |
| `VC_US_Employer_Form_Submit` | Website / GTM | — | One | Optional alias of thank-you / form — don’t double-count |
| `VC_US_Calendly_Booked` | Website / GTM | — | One | **Create (F)** — Secondary while thank-you Primary; schedule confirmed only — **not mapped yet** |
| `VC_US_Form_Started` | Website / GTM | — | One | **Create (G)** — Secondary / Observe only · first name/email/phone focus · not Conversions column |
| `VC_AU_Phone_Click_Website` | Click to call | — | One | **Create (C)** after AU GTM |
| `VC_AU_Thank_You` | Website / GTM | — | One | **Create (D)** in AU Ads UI — shallow · ID/label TBD · recipe below · not live yet |
| `VC_AU_Calendly_Booked` | Website / GTM | — | One | **Create (F)** after AU GTM — same Secondary rule as US |
| `VC_AU_Form_Started` | Website / GTM | — | One | **Create (G)** — same Secondary rule as US · AU account only · do not copy US `AW-` labels |
| AU website-call action | Create in AU Ads UI after #15 | **60s** | One | Not created yet — Checklist #16 |
| AU ad-call action | Create in AU Ads UI | **60s** | One | Not created yet — Checklist #17 |

**Hard rules**

- Do **not** attach old Zoho/Zapier / account legacy conversions to `VC_*`.
- Phone click stays **Primary** for Stage 1 signal (George). 60s website/ads calls stay Primary too — both fine.
- Website 60s wins = **connected call duration** via Google forwarding number — not a `tel:` tap.
- Don’t buy CallRail just for this Stage 1 signal.
- Prefer create conversion actions in **Ads UI** (tag + label come out of that flow). API create only if George asks and settings are locked.
- One inquiry ≠ two Primaries for the same form (thank-you **or** form submit — not both counting once each).
- Calendly **booked** ≠ Calendly open/click. Keep booked Secondary while thank-you is Primary; promote booked later if you demote thank-you.
- **Do not import all GA4 events** as Ads conversions. Quiz chips, `experiment_view`, `page_view`, and `user_engagement` are not leads. Form started is **Secondary / Observe** only — never Primary, never Maximize Conversions.

### Next

1. **F** — check off on Launch Control when you agree (not auto-checked).
2. **#16** — AU website-call 60s (Google forwarding, not tel tap). Ads UI: [Goals → Conversions](https://ads.google.com/aw/conversions) · Australia `573-539-1940`. Public # **1300 886 740**.
3. **#17** — AU ad-call 60s. Same Ads UI — no GTM required.
4. **Zoho** — read-only monitoring only. Offline qualified / Job Order import deferred during cold start.

E form $ is **not add yet** — after the four above, with CRM / value matrix. Do not put it in this list as a next action.

Campaign-specific goals on `VC_*`: include the call + shallow actions; exclude account museum defaults. Leave Maximize Clicks.

---

## Form (shallow + observation)

- dataLayer (microsite): `employer_inquiry_submitted` + alias `form_submit_success` — after durable delivery.
- Ads: map to thank-you actions (B / D) — Primary for Conversions column during shallow bridge.
- Form started (`employer_form_started` + alias `form_start`) is **first focus on name / email / phone** — not the first quiz chip. Ads: **G** Secondary / Observe only. See recipe below.
- Delivery: Resend → `us@` / `apac@` (+ George CC) · GitHub Issues backup.
- Modeled `estimated_lead_value` on site — **not** Ads conversion value. Keep preliminary front-end values separate from unverified CRM outcomes. E is not add yet.

---

## B — US thank-you mapping recipe (not live until Ads + GTM)

Site already fires the event. **Do not** add a second dataLayer event. **Do not** create this conversion via API.

### What the site fires today

| Piece | Behavior |
|-------|----------|
| URL | `/thank-you?market=us&sid=…` · `eligible=0` only when delivery was not conversion-eligible |
| Event | `employer_inquiry_submitted` (+ alias `form_submit_success`) after durable delivery |
| Where | LeadGate on `/us` after server accept, then ThankYouClient on thank-you (same `sid` is **deduped** — refresh-safe) |
| Job seekers | Never this event. They get `job_seeker_redirected` and leave to careers. No thank-you. |
| `eligible=0` / log-only | `employer_inquiry_log_only` only — **not** `employer_inquiry_submitted` |
| Calendly popup | Assist only. Open/click ≠ this conversion. Booked consult = **F** (`VC_US_Calendly_Booked`) |

US GTM `GTM-M92DX9BJ` already loads on `/us` and `/thank-you?market=us`. Google tag `AW-962672995` + Conversion linker already published — **do not add another Google tag**.

### Ads UI (George creates — USA account)

1. **Goals → Conversions → Summary → + Create conversion action.**
2. Website / conversions on a website. Domain `virtualcoworker.app`. Scan. Google tag should already be detected — **Done**, don’t install a new one.
3. Category: **Submit lead form** (or closest equivalent).
4. **+ Create conversion** → data source **Google tag** (not GA4 import).
5. Choose **Manually using code** — **not** “Automatically without code” / URL contains `thank-you`. A page-view rule would count `eligible=0` and double-count the same inquiry.
6. Conversion settings: name `VC_US_Thank_You` · **Primary** (Conversions column) · value **Don’t use a value** / unspecified · count **One**.
7. Save. Copy **Conversion ID** + **Conversion label** from the event snippet / GTM tab. Paste into Checklist B hint when known.

Stay on Maximize Clicks. This is a pipe check, not a 60s consult.

### GTM (`GTM-M92DX9BJ`) — after you have ID + label

1. New tag: **Google Ads Conversion Tracking** (not a second Google tag).
2. Paste Conversion ID + label from Ads. Transaction ID = dataLayer `submission_id` if the field is there (helps Ads dedupe).
3. Trigger: **Custom Event** named exactly `employer_inquiry_submitted`. Optional extra: Data Layer Variable `market` equals `us`.
4. **Do not** also trigger on `form_submit_success` (alias of the same inquiry — would double-count).
5. **Do not** trigger on thank-you Page View, `calendly_cta_clicked`, or calendar-open.
6. Preview: submit a real US employer form → one `employer_inquiry_submitted` → tag fires once. Refresh thank-you → `employer_inquiry_submitted_deduped` → tag does **not** fire again.
7. Publish. Then add `VC_US_Thank_You` to campaign-specific goals on `VC_US_*` (CORE/ROLES) if those campaigns don’t inherit account defaults.

**Not live** until the Ads action exists and this GTM tag is published. Checklist **ads51** stays unchecked until then.

---

## D — AU thank-you mapping recipe (after Checklist #15)

Same map as **B**. Site already fires `employer_inquiry_submitted` on AU (`/au` LeadGate + `/thank-you?market=au`). **Do not** add a second dataLayer event. **Do not** create this conversion via API. **Do not** copy US conversion labels or use US GTM `GTM-M92DX9BJ`.

AU IDs: Ads `573-539-1940` · GTM `GTM-5T6KPVSF` · GA4 `G-7X1K9V2LFE`. Public phone stays **1300 886 740**.

Popup / book CTA = secondary (not this action). Consult booked = **F**. Form $ = **E** later. Do not attach Zoho / Zapier / old Contact Us.

### Ads UI (George creates — Australia account)

Confirm the account ID in the header is **573-539-1940** (Australia). Not USA `496-715-1855`. Not the MCC.

1. **Goals → Conversions → Summary → + Create conversion action** (wording may vary: **Create conversion**).
2. Website / conversions on a website. Domain `virtualcoworker.app`. If Ads offers to install a Google tag on the website, **do not paste it into Vision** — `/au` already loads `GTM-5T6KPVSF`. Look for **Done** / skip install (wording may vary).
3. Category: **Submit lead form** (or closest equivalent).
4. **+ Create conversion** → data source **Google tag** — **not** GA4 / Analytics import.
5. Choose **Manually using code** — **not** “Automatically without code” / URL contains `thank-you`. A page-view rule would count `eligible=0` and double-count.
6. Name `VC_AU_Thank_You` · **Primary** (Conversions column) · value **Don’t use a value** / unspecified · count **One**.
7. Save. Copy **Conversion ID** + **Conversion label** from the event snippet / GTM tab. Do **not** paste US `AW-962672995` or the US thank-you label.

If the wizard only lists Analytics / GA4 events (old `.com.au` or `phone_click`): **Cancel**. Do not pick those. Screenshot and stop — we need Google tag + a label for GTM, not a GA4 import.

Stay on Maximize Clicks.

### GTM (`GTM-5T6KPVSF`) — after you have AU ID + label

Confirm the container ID in the header is **GTM-5T6KPVSF**. Not `GTM-M92DX9BJ`.

1. If Tags has no **Conversion Linker**, add one → trigger **All Pages**. If it is already there, skip.
2. If Tags has no Google tag / Google Ads tag for this **new AU Conversion ID**, add one (Conversion ID only, All Pages). Do not reuse the US `AW-` ID.
3. New tag: **Google Ads Conversion Tracking** (not a second Google tag, not a GA4 Event).
4. Paste the AU Conversion ID + label from Ads. Transaction ID = dataLayer `submission_id` if that field exists (helps Ads dedupe). Skip the field if it is not there.
5. Trigger: **Custom Event** named exactly `employer_inquiry_submitted`. Optional extra: Data Layer Variable `market` equals `au`.
6. **Do not** also trigger on `form_submit_success` (alias — would double-count).
7. **Do not** trigger on thank-you Page View, `calendly_cta_clicked`, or calendar-open.
8. If a GA4 Event tag named `employer_inquiry_submitted` already exists from earlier work, **leave it** — that is GA4, not this Ads conversion. Do not import it as the Ads action.
9. Preview (GTM Preview / Tag Assistant on `/au`) — do **not** submit a fake production lead. Publish when the tag is wired.
10. Then add `VC_AU_Thank_You` to campaign-specific goals on `VC_AU_S_CORE` and `VC_AU_S_ROLES` if those campaigns do not inherit this action.

**Not live** until the Ads action exists and this GTM tag is published. Checklist **ads53** stays unchecked until then.

---

## Calendly booked (consult scheduled)

- Site already opens / pushes Calendly on eligible thank-you — that is **not** an Ads conversion by itself.
- Ads actions: `VC_US_Calendly_Booked` · `VC_AU_Calendly_Booked` (Website) — **create in Ads UI**, then map in GTM from Calendly schedule-confirmed (e.g. `event_scheduled` / invitee created).
- Goal setting: **Secondary** while thank-you is shallow Primary (same funnel path). Stronger signal than form thank-you; promote later when reweighting.
- Status: **open** — do not treat as firing until GTM is mapped and a test booking lands in Ads.

---

## G — Form Started (Secondary / Observe)

Diagnostics only. **Not** a qualified lead. **Not** Primary. **Not** the Conversions column. Stay on Maximize Clicks.

**What the live page fires** (`https://www.virtualcoworker.app`, lp_version `stage1-v9`):

| Action | Event |
|--------|--------|
| First quiz chip (role tile) | `lp_micro_role_tile` + `quiz_started` / `lp_micro_quiz_start` |
| First focus on Full name / Work email / Phone | `employer_form_started` + alias `form_start` (`start_reason: field_interaction`) once |

Do **not** import every GA4 event. `experiment_view` is hundreds; quiz tiles outnumber form start; the last agency already poisoned bidding with page views / eBook / chat opened.

**Do not** create this via Ads API. **Do not** copy US `AW-` labels into Australia.

GA4 already counts `form_start` (Enhanced Measurement on the contact form). The Ads Conversions column stays empty until this action exists and GTM is published. Empty Ads ≠ the event is dead.

Alternative if Ads/GA4 is already linked: import **only** `form_start`, still Secondary. If the wizard offers a pile of events, **Cancel** — do not import them all.

### Ads UI (George creates — USA `496-715-1855`)

1. Confirm the account ID in the header is **496-715-1855**. Not Australia. Not the MCC.
2. **Goals → Conversions → Summary → + Create conversion action.**
3. Website / conversions on a website. Domain `virtualcoworker.app`. Google tag `AW-962672995` should already be detected — **Done**, don’t install a new one.
4. Category: **Other** (not Submit lead form).
5. **+ Create conversion** → data source **Google tag** (not GA4 import).
6. **Manually using code** — not “Automatically without code”, not a URL rule.
7. Name `VC_US_Form_Started` · **Secondary / Observe** (not Primary, not Conversions column) · value **Don’t use a value** · count **One**.
8. Save. Copy **Conversion ID** + **Conversion label**.

### GTM (`GTM-M92DX9BJ`) — after you have US ID + label

1. New tag: **Google Ads Conversion Tracking** (not a second Google tag).
2. Paste Conversion ID + label. Transaction ID optional (`submission_id` is not on form start — skip if unsure).
3. Trigger: **Custom Event** named exactly `employer_form_started`. Optional: Data Layer Variable `market` equals `us`.
4. **Do not** also trigger on `form_start` (alias of the same focus — would double-count).
5. **Do not** trigger on `lp_micro_*`, `quiz_started`, `quiz_step`, or Page View.
6. Preview on `/us`: tap a role tile → this tag does **not** fire. Click into Full name → tag fires once. Do **not** submit a production lead.
7. Publish only after George OKs this exact tag. Then keep it off campaign-specific **primary** goals; Observe is enough.

### Ads UI (George creates — Australia `573-539-1940`)

Confirm the account ID in the header is **573-539-1940**. Not USA `496-715-1855`. Not the MCC.

1. **Goals → Conversions → Summary → + Create conversion action.**
2. Website. Domain `virtualcoworker.app`. `/au` already loads `GTM-5T6KPVSF` — **do not** paste a new Google tag into Vision. Skip install / **Done** if offered.
3. Category: **Other**. Data source **Google tag** → **Manually using code**.
4. Name `VC_AU_Form_Started` · **Secondary / Observe** · no value · count **One**.
5. Save. Copy the **AU** Conversion ID + label. Do **not** paste US `AW-962672995` or the US form-started label.

If the wizard only lists a pile of Analytics / GA4 events: **Cancel**. Screenshot and stop.

### GTM (`GTM-5T6KPVSF`) — after you have AU ID + label

Confirm the container ID in the header is **GTM-5T6KPVSF**. Not `GTM-M92DX9BJ`.

1. Conversion Linker on All Pages if missing. Google tag for the **new AU Conversion ID** on All Pages if missing. Do not reuse the US `AW-` ID.
2. New **Google Ads Conversion Tracking** tag. Paste AU ID + label.
3. Trigger: Custom Event `employer_form_started` only. Optional: `market` equals `au`.
4. **Do not** also trigger on `form_start` or quiz / micro events.
5. Preview on `/au`. Same chip-vs-name check as US. Do **not** submit a production lead. Publish when George OKs this exact tag.

**Not live** in Ads until the action exists and GTM is published.

---

## GTM / GA4 / GSC

| Item | Status |
|------|--------|
| `NEXT_PUBLIC_GTM_US` / `NEXT_PUBLIC_GA4_US` | **Live** — `GTM-M92DX9BJ` → `G-2V3V0BS6JW` |
| Website-call / forwarding tag | **Live in US GTM** — Google Tag `AW-962672995` + `AW-962672995/Sf71CJSQr98cEOPyhMsD` (`phone_conversion_number` = (888) 964-8644) All Pages |
| AU GTM + GA4 | **Live** — `GTM-5T6KPVSF` → `G-7X1K9V2LFE` on Vercel **vision** Production (2026-08-12). `/au` serves AU GTM. Checklist #15 / ads33. Ads conversion tags still wait (C/D/#16). Playbook: [AU-GTM-GA4-PLAYBOOK.md](AU-GTM-GA4-PLAYBOOK.md). |
| GSC `virtualcoworker.app` / `www` | George may need to Verify — Checklist #22 |

---

## Zoho Qualified (quality / later) — DEFERRED DURING COLD START

- **Not this week’s Ads work.** Zoho is not cancelled. API stays read-only. `.app` writes stay OFF.
- Do not build a new Zoho→Google Ads offline conversion integration. Do not add Zapier. Do not make existing Zoho-related conversions Primary.
- Missing `VC_*` / `.app` stamps on current Zoho rows is expected (new forms are not connected) — not a Zoho failure.
- Revisit only after: enough qualified employer enquiries · VC names the Zoho owner · existing Zoho/Zapier/Ads uploads documented and reconciled · one `.app` Sales Enquiry tested safely end to end · CRM outcome definitions/values consistent enough to validate.
- **E form $ is later still** — not add yet. Keep front-end values separate from unverified CRM outcomes.
- Lock: [ZOHO-COLD-START-DEFERRED-2026-08-14.md](./ZOHO-COLD-START-DEFERRED-2026-08-14.md).

---

## Safety

No mass-pause KW/RSA · no budget/bid change · no Brand · no broad workers/remote · no legacy conv attach · no Ads API mutate unless George explicitly asks for that one action · no token exposure.
