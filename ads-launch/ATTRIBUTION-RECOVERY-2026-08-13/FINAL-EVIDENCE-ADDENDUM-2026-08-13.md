# Final evidence addendum — 13 August 2026

Read-only. No Ads mutations, Zoho writes, uploads, email, or deploy. Labels: **VERIFIED** / **INFERENCE** / **UNKNOWN**.

**Decision gate (unchanged):** not ready for CRM writes or offline import.

---

## 1. Ads goals — current `VC_*`

**VERIFIED** (API 13 Aug, remaining budget after a first-pass parse crash):

| Campaign | Status | Bidding | Goal config level | Custom goal |
|----------|--------|---------|-------------------|-------------|
| `VC_US_S_CORE` / `VC_US_S_ROLES` | ENABLED | TARGET_SPEND (Maximize Clicks) | **CAMPAIGN** | empty |
| `VC_AU_S_CORE` / `VC_AU_S_ROLES` | ENABLED | TARGET_SPEND | **CAMPAIGN** | empty |

They are not on the account-default basket. Editor CSV still cannot express this; this is Ads UI/API.

**VERIFIED US category map** (same on CORE and ROLES). `biddable=true` only for:

- `PHONE_CALL_LEAD` / WEBSITE
- `PHONE_CALL_LEAD` / CALL_FROM_ADS
- `SUBMIT_LEAD_FORM` / WEBSITE

**VERIFIED US `biddable=false`:** `BOOK_APPOINTMENT`, `CONVERTED_LEAD`, `QUALIFIED_LEAD`, `DOWNLOAD`, `PAGE_VIEW`, `CONTACT`, plus other leftovers. That matches the intended split: thank-you + 60s phone eligible; Calendly booked and Zoho/JO-shaped categories not eligible for bidding. Maximize Clicks does **not** optimize toward those flags today. They would matter if bidding changed.

**UNKNOWN:** AU category/`biddable` map (Ads ceiling hit). Morning conversion-action snapshot (16:03 UTC) still used for named actions — not replayed.

Morning snapshot (not this afternoon): US `VC_US_Thank_You` and three US phone actions ENABLED, `primary_for_goal=true`, `include_in_conversions_metric=false`. AU named `VC_*` in that snapshot: `VC_AU_Phone_Click_Website` only. Zapier/OCI JO: `primary_for_goal=false` on both accounts.

Account-default junk (US eBook `include=true`; AU hidden UA goals) is **not** what `VC_*` inherit while `goal_config_level=CAMPAIGN`. **INFERENCE:** leftover account flags can still confuse the UI; they are not proven attached to `VC_*`.

---

## 2. Historical config — can we prove what automated bidding optimized toward?

**NO** for 1 Aug 2024 – 12 Aug 2026.

| What we have | What it is not |
|--------------|----------------|
| Current `VC_*` = Max Clicks + campaign-level goals | Not history |
| On-disk 2-year **counts** by conversion action | Not which actions were Primary / in-column / campaign-attached in each month |
| Many non-`VC_*` campaigns currently typed Max Conv / similar (US 40/52, AU 41/64) | Current type stamped on a dated report — **not** a month-by-month bidding history |
| `change_event` | Typical lookback ~30 days. Pass 1 fetched 14 days then a FieldMask parse failed; **not retried** |

Monthly action mix for that window: **UNKNOWN this pass** (fetched once, unwritten, not replayed).

Do **not** say historical campaigns optimized toward Zapier JO, forms, or Calendly unless change history says so. Volume in the Conversions column is not proof of the bidding objective at the time.

---

## 3. Zoho join — click-linked only

Correct Ads-relevant denominator is **job orders with a Google click id on the JO or the linked Sales Enquiry**. It is **not** 782 (all sources).

**VERIFIED** (COQL, hashes only):

- Direct `UTM_Gclid` on Job Orders: **18** all-time. All 18 join to a Sales Enquiry. All 18 hashes **match** the enquiry `utm_gclid`. Unique hashes among those 18: **18**. None JO-only, none mismatched.
- 90-day Job Orders sampled: **200 of 242** (newest 200; 42 older 90-day rows not pulled). Of 200: 192 have an enquiry lookup; 18 have a direct GCLID.
- Click-linked in that 200: **69** = 18 on both objects + **51 inherited** (enquiry has GCLID, JO field empty) + 0 JO-only. **131** of 200 have no click id on either object.
- Unique effective hashes among those 69: **62** (some reuse — replacement/returning is plausible, not proven).
- Region of 69: USA **43** · AU **26**. Placement stage **26**. Cancelled-like **29**. Months: 2026-05 **7** · 06 **31** · 07 **25** · 08 **6**.

**UNKNOWN:** inherited GCLID on the 582 Job Orders outside this sample; uniqueness of the 576 enquiry GCLIDs (no bulk export); whether Google still recognizes any click (click date ≠ CRM create date; not looked up in Ads).

**Placements:** Deals have **no** Job Order lookup field (**VERIFIED** schema). Related-list settings API **401**. Related-record names `Deals` / `Placements` / `Contacts` / `Accounts` on a Placement-stage JO returned invalid relation (**VERIFIED**). Explicit JO→Placement link: **UNKNOWN**.

`.app` still does not write Zoho. `ZOHO_CRM_ENABLED` off.

---

## 4. Zapier JO vs Standard OCI

Morning snapshot, window 1 Aug 2024 – 12 Aug 2026:

| Action | US conv / all | AU conv / all | Primary | In conv col |
|--------|---------------|---------------|---------|-------------|
| Zapier JO | 67 / 125 | 36 / 69 | No | No |
| Standard OCI JO | 23 / 85 | 14 / 51 | No | No |

**UNKNOWN:** duplicate vs similar events; shared transaction IDs (none found on CRM); whether Ads can list uploaded click IDs (not queried; reporting API is a poor source of individual upload GCLIDs); whether either Zap is still on. **Did not upload to test.**

Do **not** treat 67+36 as “how many job orders Ads generated,” or 782−103 as “Zapier missed Ads JOs.” 782 is every source. Click-linked in the 90-day sample is 69 of 200, not 782.

---

## 5. Pilot pass/fail (code + Ads + published GTM)

Existence ≠ firing. `VC_*` last-7-day conversions on disk: **0** (CORE/ROLES); US ROLES **1** `all_conversions` in the 2-year window.

| Check | Result | Label |
|-------|--------|-------|
| `VC_*` Maximize Clicks | TARGET_SPEND, ENABLED | VERIFIED |
| Campaign-specific vs account default | CAMPAIGN on all four | VERIFIED |
| US biddable = phone + submit-form; not JO/Calendly categories | as above | VERIFIED |
| AU biddable map | — | UNKNOWN |
| Site fires `employer_inquiry_submitted` once per `submission_id` | code + tests | VERIFIED in code |
| Site listens for Calendly **booked** | **No** (`calendly_cta_clicked` / open only) | VERIFIED |
| GTM listens for `calendly.event_scheduled` → `calendly_event_scheduled` | **Yes** — published US `GTM-M92DX9BJ` **v6**, AU `GTM-5T6KPVSF` **v6** (spec’s AU v5 is stale vs live v6) | VERIFIED in container JS |
| GTM Ads conversion on `employer_inquiry_submitted` (not `form_submit_success`) | Yes, both containers | VERIFIED mapping |
| GTM Ads conversion on `calendly_event_scheduled` | Yes, both containers | VERIFIED mapping |
| Those tags **fired** into Ads | Not proven (desert / no Preview this pass) | UNKNOWN |
| AU thank-you / Calendly / 60s **Ads actions** | Absent from 16:03 inventory; GTM has labels + AU forwarding tag `1300 886 740` | UNKNOWN if created after that pull |
| `.app` → Zoho | Off | VERIFIED |
| Exact+Phrase only live | Not re-queried | UNKNOWN this pass |

---

## Withdraw these earlier claims

- Zoho/Zapier actions were Secondary **throughout history** (today they are Secondary; history **UNKNOWN**).
- Historical Max Conv campaigns optimized toward named actions (forms, Calendly, Zapier JO) — **not proven**.
- The same event definitely fired multiple actions.
- Zapier missed most Ads-generated job orders (invalid vs 782).
- Agencies treated Ads Conversions as the sales book **on purpose**.
- Spend ÷ 103 (or ÷ 67/36) is real CAC.
- All 782 Job Orders should have appeared in Ads.
- “The site does not listen for Calendly booked” — **site code** still does not; **GTM does**.

---

## Still blocked (human)

Caitlin: one JO definition; Zapier on/off. Raffie: GTM Preview one thank-you + one booked fire; Zap screenshot. Cheyenne/Holly: `.app` email + who answers 888 / 1300. Amanda: AU goal screenshot (US category map is already in this addendum).
