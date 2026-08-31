# Executive truth — 13 August 2026

**Decision gate:** `NOT READY FOR CRM WRITES OR OFFLINE IMPORT`

Read-only. Nothing written, sent, posted, or enabled.

---

## What is currently working

- One Zoho CRM named **Virtual Coworker** is the real sales book. US and AU live together, split by **Region** (USA / AU). The Leads list is labelled **Sales Enquiries**. Deals are labelled **Placements**. **Job Orders** is a custom list beside those.
- Last 90 days the team logged **647 sales enquiries**, **242 job orders**, **122 placements**, **102 new contacts**, and **379 calls**. That is a working company, not an empty CRM.
- The new paid pages on **virtualcoworker.app** have a real form. A completed US/AU employer form goes to `POST /api/lead`, then email (designed as `us@` / `apac@`) and an optional webhook. Job-seekers are sent to careers and **do not** fire the employer conversion event.
- The form **can** keep Google click stamps (`gclid`, `gbraid`, `wbraid`) plus UTMs and landing page in the browser session and put them on the email. Unique id: `submission_id`.
- Live Search is a cold start on Maximize Clicks: `VC_US_S_CORE` / `VC_US_S_ROLES` and the AU twins. Exact + Phrase. Destinations `/us` and `/au`. Brand is deferred.
- New `VC_*` conversion actions exist in the US account for thank-you, 60-second calls from ads, 60-second website calls, and phone click. AU has a phone-click action. These are pipe checks, not proof of a hire. `VC_*` campaigns themselves show **0** conversions in the last-7-day snapshots.
- Most recent job orders **do** link back to a sales enquiry (`Client_Name` filled on **234 / 242** job orders in 90 days).

## What is broken

- **Google Ads and Zoho were never measuring the same object.** From 1 Aug 2024 to 12 Aug 2026 the two accounts spent about **$1.18 million**. Ads reported thousands of “conversions” (forms, thank-you pages, Calendly, chat, phone taps, a job-seeker click). The only CRM-shaped Ads number is a Zapier upload named Zoho JO Submitted: **67 US + 36 AU**, plus a twin called Standard OCI (**23 + 14**). This CRM has **782 job orders** in the same years. The Ads number is a thin, duplicate-prone slice — not how many job orders happened.
- **`.app` is not writing into Zoho.** Today’s CRM still looks like WordPress, Zapier, and humans. The paid-site switch `ZOHO_CRM_ENABLED` is off (example and this pass). Newest 30 enquiries: **zero** click ids. After 5 Aug 2026, new enquiries stopped storing `utm_gclid`.
- **Website ≠ Google Ads.** 550 of 647 recent enquiries are sourced Website. Only 6 say Google. You cannot filter paid-search leads from source alone.
- **Click ids die as the deal gets more real.** Enquiries: **576 / 3,433** ever stored `utm_gclid`. Job orders: **18 / 782**. Placements: no click-id field found.
- **Enquiry status “Job Order Submitted” is not the same object as a Job Orders row.** 213 vs 242 in 90 days. Job Orders stage “Job Order Submitted” is only **3**. Standard Zoho “convert lead” almost unused (**1** in 90 days).
- **Junk sits in the same lists.** Newest 20 enquiries that still have a click id: **10 marked Junk Lead**. Tests sit in job orders. Philippines Desk contacts sit in Contacts.
- **Calendly open is not booked.** The site fires `calendly_cta_clicked`. There is **no** booked-event listener in the `.app` code. Historical Ads “LK - Scheduled Calendly Call” (373 US) is a museum action, not the new pipe.
- **A phone tap is not a 60-second conversation.** US 60s actions exist and show 0 conversions in the forensic window. AU 60s website-call and ad-call actions were **not** in the 13 Aug inventory. CallRail is absent. Zoho logs calls (379 in 90 days) but those rows have no Google click id.
- **Vision’s Zoho mapper does not match live field names.** Code prefers `$gclid` and `VC_Submission_ID`. Live CRM uses `utm_gclid` / `UTM_Gclid`. `VC_Submission_ID`, `gbraid`, and `wbraid` **do not exist** on Sales Enquiries.

## What is unknown

| Item | Why it is unknown |
|------|-------------------|
| Whether the old Zapier → Ads path is still on | No Zapier access. Zoho webhook/workflow APIs were not readable. |
| Whether Google still recognizes any stored click id | Import window is from the **click**, not the CRM create date. Not checked in Ads. |
| Whether any of the 18 job-order click ids were already uploaded | Zapier / Standard OCI overlap not matched record-by-record. |
| Campaign-specific goals on each `VC_*` campaign | Not in the on-disk pull. Account-default junk (US eBook, AU hidden UA goals) is a latent risk if inherited. |
| Whether production email (`us@` / `apac@`) is actually delivering | Designed in code. Production env not read. |
| Who or what **Social Marketing (Lois)** is | Active Administrator, CEO profile, `virtualcoworker.com` domain. Created 21 of the newest 30 enquiries. Last-activity field not returned. |
| Whether Recruit holds the real hiring pipeline | Recruit id on job orders: **8** all-time. |
| What “signed client” is in Zoho | Placements have `Contract_Invoice_Status`. Meaning unused without a human. |
| Why all-time counts equal 1 Aug 2024 | Rebuild vs imported dates. |
| Remaining Zoho API credits today | Headers not sent. This pass used 11 reads after the earlier census. |
| Whether George’s later Ads UI work (Calendly booked / AU thank-you / $1 placeholders) is already live | 13 Aug inventory has US thank-you + US 60s calls + AU phone click. Calendly booked and AU 60s/thank-you were **not** in that inventory. Do not infer they fire. |

## What Google Ads currently thinks is a conversion

**On `VC_*` last 7 days:** nothing. The Conversions column is a desert. That is expected on Maximize Clicks while the pipe is being proven.

**Account-default “in Conversions column” (include_in_conversions_metric = true):** US = hidden **eBook Download** (0 in two years). AU = six hidden Universal Analytics goals (Chat, Submission ×2, Job order form, Lead Form Submit Completion, Transactions) — also 0. Those are museum leftovers, not the new system.

**What filled the old accounts for two years:** WordPress free-consultation forms, GA4 thank-you pages, Calendly, chat opens, phone taps, a job-seeker click, and a thin Zapier/OCI job-order upload. Many of those were Primary or double-counted. **Do not attach them to `VC_*`.**

George’s intended pipe checks (thank-you, Calendly booked, 60-second phone, $1 placeholders, Primary OK for now) are the right *idea*. On disk, some US actions exist and show **0**. Firing is **not proven**. E (form $) is not next.

## What Zoho considers an enquiry, job order, and placement

| Object | What it is | What it is not |
|--------|------------|----------------|
| **Sales Enquiry** | A person/company logged for sales to work. Status is a human disposition (junk, not a fit, brochure, discovery, job order submitted…). | Not automatically a Google click. Not a job order. |
| **Job Order** | A recruiting request the team is staffing. Stages include sourcing, interviews, endorsed, placement, cancelled. Almost half of the last 90 days were cancelled (97 / 242). | Not proof the click was paid search. Not a signed-client field by itself. Not a placement. |
| **Placement** | After-the-hire ops (New Placement, Day 1 check-in, 1 month, cancelled…). | Not an ad click. 41 of 122 recent placements have blank Region. |

A raw enquiry is not a qualified employer. A job order is not necessarily signed. A placement is the hire, and some of those cancel too.

## Does the new `.app` funnel reach Zoho?

**No.** Not today.

The write path exists in code and is gated off. Email/webhook is the live design. Zoho still receives WordPress / Zapier / human rows. That is two movies.

## Can a trustworthy historical winner be recovered?

**Not as a bidding truth.** Old Ads “winners” are mostly form fills and appointment pings on WordPress, often at very high CPA, often overlapping. Zoho JO 67/36 is not a census of job orders.

**As research:** yes, carefully. There is a stash of click ids (576 enquiries; 18 job orders). That can teach which *old* pages and sources existed. It must not be attached to `VC_*` and must not drive Maximize Conversions.

## Are any recent outcomes potentially importable?

**A small set is worth human review. None are ready to upload.**

- **231** enquiries in the last 90 days still have `utm_gclid` — but the newest 20 of those are half junk, and **after 5 Aug the new enquiries have none**.
- **All 18** job orders that ever stored a click id were created between 20 Jul and 7 Aug 2026. All 18 link to a sales enquiry. Four are already Placement. Two have `utm_source = chatgpt.com` (do not treat as Google Ads). Three are cancelled.
- Google may still reject them: we do not know the **click** date, and we do not know if Zapier already uploaded them.

See [RECOVERABLE-CANDIDATES.md](RECOVERABLE-CANDIDATES.md). Do not call them great leads.

## What must be verified before any integration

1. Caitlin / Cheyenne name the **one** status that means “real job order we would ever tell Google about.”
2. Someone who can see Zapier says whether the old upload is **still on**.
3. Cheyenne / Holly confirm they actually receive `.app` emails and can tell them from WordPress rows.
4. Raffie (or equivalent) can show whether GTM maps `employer_inquiry_submitted` once, and whether Calendly **booked** (not open) is mapped.
5. Amanda can confirm campaign-specific goals on `VC_*` exclude museum actions.
6. Only then consider a **later** Secondary offline path — never a Primary, never a backfill of the 576, never both Zapier and a new uploader.

Until then: stay on Maximize Clicks. Score quality through Cheyenne and Holly, not through this CRM’s Google column.
