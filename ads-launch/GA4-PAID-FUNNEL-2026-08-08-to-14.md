# Paid LP funnel — 2026-08-08 to 2026-08-14

Read-only. Paid Search `google / cpc` to `/us` and `/au` only. Organic, Direct, Zoho, and virtualcoworker.com excluded. No site edits, no Ads mutations, no xray deploy.

**Ads (existing impression-share pull, complete days Aug 8–14):** US Core+Roles **406 clicks, $1,166.75, 1 conversion, all_conversions 3 (2+1)**. AU Core+Roles **217 clicks, A$769.28, 0 conv / 0 all_conv**. Matches George: 1 thank-you + 2 website phone clicks.

**GA4:** US `G-2V3V0BS6JW` (549075481) · AU `G-7X1K9V2LFE` (549811743) · Viewer SA · Data API 2026-08-15. Paid stored as **Paid Search = `google / cpc`** (same 355 US / 66 AU sessions either way). Organic on these LPs: 9 US, 1 AU (dropped).

**Launch-to-date:** US Stage 1 ≈ Aug 8, so LTD = this window. AU Stage 1 ≈ Aug 9; AU **GA4 tags only live ~Aug 12**, so AU funnel is a post-tag slice, not the 217 Ads clicks.

---

## WHAT IS ACTUALLY HAPPENING

People click. Ads CTR is strong. They land on the current `/us` and `/au` template with the form already in the hero. About half leave immediately. Almost nobody types in the form: GA4 enhanced `form_start` is **2 users out of 355 US paid LP sessions**, and **0 of 66** tagged AU paid sessions. The ones who do start appear to finish (2 US thank-you users in GA4 vs 2 form starts; Ads recorded 1 thank-you). This is **failure to begin**, not a proven submit-broken form, and not a flood of thank-yous missing from Ads. Phone is the only other on-site action Ads counted (2 website phone clicks). GA4 never received `phone_cta_clicked` / `employer_inquiry_submitted` — GTM is firing Ads conversions, not forwarding those dataLayer events into GA4. Visible search terms are **not** mostly job-seeker junk; they are a mix of clear employer queries and generic/ambiguous VA-role queries, with ~55% of clicks missing from the search-term report entirely. Below-fold testimonials are largely unseen on mobile (only 13 of 196 US paid mobile users triggered the 90% scroll event).

---

## US / AU funnel (paid LP only)

| Step | US (355 sessions / 339 users) | AU tagged (66 / 62) — incomplete |
| --- | --- | --- |
| Ads clicks Aug 8–14 | 406 ($1,167) | 217 (A$769) |
| GA4 paid `/us` or `/au` sessions | 355 (87% of clicks) | 66 (30% of clicks; tags ~Aug 12) |
| Device | 204 mobile / 145 desktop / 6 tablet | 30 mobile / 35 desktop / 1 tablet |
| Engaged sessions / rate | 168 / **47%** (mobile 42%, desktop 55%) | 37 / **56%** (mobile 40%, desktop 69%) |
| Avg engagement time | **16s** (5,568s ÷ 355) | **24s** (1,598s ÷ 66) |
| Bounce | 53% (mobile 58%, desktop 45%) | 44% (mobile 60%, desktop 31%) |
| Pages / session | 1.25 (443 page views) | 1.32 (87) |
| Scroll 90% (GA4 enhanced `scroll` + `percentScrolled=90` only) | 42 events / **40 users** (13 mobile, 27 desktop) | 14 / 14 (2 mobile, 12 desktop) |
| CTA / outbound `click` (enhanced) | 7 users (3 mobile, 4 desktop) | **0** |
| Form start | `form_start` **2 users** (1 mobile, 1 desktop). `employer_form_started` **missing in GA4** | **0** |
| Form validation | `employer_form_validation_error` **missing in GA4** | missing |
| Submit | `employer_inquiry_submitted` / aliases **missing in GA4** | missing |
| Thank-you page | **2 users**, 4 views (1 desktop + 1 mobile) | **0** |
| Ads thank-you / phone | 1 thank-you · 2 website phone clicks | 0 / 0 |
| Phone dataLayer | `phone_cta_clicked` / `phone_click` **missing in GA4** | missing |
| Calendly open / booked | `calendly_cta_clicked`, `calendly_embed_viewed`, `calendly_event_scheduled` **missing in GA4** | missing |
| JS/form `exception` | **0** paid and sitewide | **0** |
| Hub vs role landings | `/us` 249 (70%) · role LPs ~105 · quiz 1 | `/au` 47 (71%) · rest role |

Landings with more sessions (US paid): `/us` 249, `/us/bookkeeping` 30, `/us/social-media` 18, `/us/digital-marketing` 17, `/us/sales` 15, `/us/administrative-support` 13. `/us/sales` desktop 7 sessions at 86% engaged — tiny, not a campaign verdict.

---

## Direct answers

| Question | Answer |
| --- | --- |
| Failing to begin the form? | **Yes.** Paid US `form_start` = 2 / 355 (0.6%). AU tagged = 0 / 66. Form is already in the hero (`LeadGate` on `MarketLanding`), so this is not “they never scrolled to it.” |
| Begin then abandon? | **Not what the paid numbers show, and not fully measurable.** 2 form starts vs 2 thank-you users. If those are the same people, they finished. `employer_form_started` is not in GA4, so abandon-after-type is uncounted. |
| Submit but no thank-you? | **No evidence.** No delivery-failed events in GA4 (that event is also not forwarded). Ads 1 thank-you; GA4 2 thank-you users on paid sessions. |
| Thank-you in GA4 not Ads? | **Slight gap, not the story.** 2 GA4 users vs 1 Ads thank-you. Does not explain hundreds of clicks. |
| Phone in dataLayer/GA4 not Ads? | **Opposite.** Ads has the 2 website phone clicks. GA4 has **zero** `phone_cta_clicked` / `phone_click`. Site code does fire both (plus alias). GTM is not sending them to GA4. |
| Material mobile vs desktop? | **Worse on mobile, not broken.** US paid: 57% mobile; engagement 42% vs 55% desktop; 90% scroll 7% of mobile users vs 20% of desktop. Form starts 1 and 1. No `exception` events. |
| Either market better? | **Neither converts.** AU’s tagged slice looks slightly stickier (56% engaged, 24s) but **0** form starts, thank-yous, or Ads conv, and most AU clicks never hit this GA4 property. US has the only Ads outcomes (1 + 2). |
| Technical form problem? | **Not shown.** Zero GA4 `exception`. The rare starters line up with thank-you arrivals. Code submits to `/api/lead` then `/thank-you`. Measurement hole ≠ form outage. |

---

## Ranked causes

**1. Weak offer / message or insufficient trust (primary)**  
CTR is strong; on-page action is not. Form sits in the first screen and still almost nobody starts it. Average stay ~16s (US). Only 11% of US paid users hit 90% scroll, so TrustBand / process / reviews below the hero are mostly unused. That is a “looked, left” problem, not a tracking desert.

**2. Wrong traffic (real mix, not a junk wipeout)**  
Reported search terms (US **174 of 406 clicks**, AU **106 of 217** — Google withholds the rest):

| Bucket | US clicks / spend | AU clicks / spend |
| --- | --- | --- |
| 1 clear employer | 51 / $147 (29% of *reported* clicks) | 43 / A$151 (41%) |
| 2 ambiguous | 122 / $378 (70%) | 63 / A$218 (59%) |
| 3 job seeker | **0 clicks** (5 impression-only crumbs) | **0** |
| 4 competitor | 1 / $2 | 0 clicks (impr only: Belay, Cloudstaff) |
| 5 irrelevant | 0 | 0 |

Top US reported: `remote staffing agency` 16 clicks / $45; `virtual coworker` 10 / $23; `digital marketing assistant` 6 / $25; plus bookkeeping / SMM / “what is a virtual assistant.” Top AU: `australia virtual assistant hiring` 10 / A$33; `24x7 direct` 9 / A$37; hiring-AU variants. Job-seeker queries are already largely not getting clicks in this report. **Do not treat the unclassified 55% as proven junk.** Ambiguous generic VA / role queries are the live leakage, not a few “VA jobs” rows.

**3. Form friction / technical failure (not supported as the main leak)**  
Nothing in GA4 shows validation errors, delivery failures, or JS exceptions. You cannot call the form “broken” from this week’s data. You also cannot call field-level friction the bottleneck when almost no one enters a field.

**4. Attribution / tracking discrepancy (small, and backwards from the usual scare)**  
Ads 1 thank-you + 2 phone vs GA4 2 thank-you users + 0 phone events. Outcomes are scarce in both systems. Custom events from `vision/lib/tracking.ts` (`employer_form_started`, `employer_inquiry_submitted`, `phone_cta_clicked`, Calendly, validation) **are not in these GA4 properties for paid LP sessions**. Enhanced measurement only: `page_view`, `session_start`, `scroll` (90%), `click`, `form_start`. Experiment beacon is unrelated (`experiment_*` only). This gap hides the middle of the funnel; it does **not** invent a pile of uncounted thank-yous.

---

## Three incremental changes (current template)

Keep stars, testimonials, reviews, proof, and visual identity. No new LP concept.

1. **Tighten the first-screen headline/subhead to the queries that actually click** — especially US `remote staffing agency` / hire-staffing language alongside the existing VA/role line — without touching Trust chips or the form layout. Evidence: form is already in the hero and `form_start` is 2/355; 53% bounce; visible terms split employer-staffing vs generic VA, not job ads.

2. **Keep one existing testimonial/review visible in the first screen on mobile** (duplicate a quote already on this template, don’t invent a new proof system). Evidence: TrustBand sits below the process block; only **13 of 196** US paid mobile users fired 90% `scroll`, so below-fold reviews are not in play.

3. **Do not demote the current phone CTA** (sticky / hero `tel:`). Evidence: Ads counted **2 website phone clicks vs 1 thank-you** in the same week the form almost never started. Phone is the only other behavior Google recorded. No new page; don’t hide 888 / 1300 behind the form.

---

## What analytics cannot answer (exactly)

Cannot see first-field start vs abandon, validation failures, Calendly opens/books, or true phone taps in **GA4**. Those events exist in code (`employer_form_started` + alias `form_start`, `employer_form_validation_error`, `phone_cta_clicked` + `phone_click`, `calendly_cta_clicked`, GTM `calendly_event_scheduled`) but **GTM is not forwarding them to US/AU GA4**.

**Single event to add:** a GA4 Event tag on **`employer_form_started`** (already pushed from LeadGate on first field; ungated LPs do not fire on page load). That one number answers “won’t start” vs “start then quit.” Do not add a new site event. Map existing dataLayer → GA4.

AU paid behaviour for **Aug 8–11 is missing in GA4** (tags ~Aug 12). Search-term classification covers **only ~43–49% of clicks**.
