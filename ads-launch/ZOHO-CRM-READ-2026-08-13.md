# Zoho vs Google Ads — 13 Aug 2026

Read-only look. **Nothing was written in Zoho. Nothing was sent. Google Ads was not called.** The paid-site switch `ZOHO_CRM_ENABLED` stayed **false**.

George: this is the CRM the sales team actually uses. It is **not** safe to treat as Google’s conversion meter.

---

## What’s going on

- This is **one Zoho CRM** named **Virtual Coworker** (Zoho One, paid, Brisbane time, Australian dollars). US and Australia both live here. There is a **Region** field: **USA** or **AU**. We do not need a second CRM login to “find Australia.”
- What George saw as “no Leads” is a rename. The Leads list is labelled **Sales Enquiries**. Deals are labelled **Placements**. **Job Orders** is a custom list next to those. This is customized CRM, not “we accidentally opened Recruit instead.”
- There is a Recruit hook on Job Orders (`Recruit Job Opening ID`) but it is almost empty — **8 records**. Hiring may also live in Zoho Recruit; this token barely sees that.
- Last 90 days the sales team actually logged: **647 sales enquiries**, **242 job orders**, **122 placements**. That is a working company CRM. It is messy, not empty.
- Google Ads’ old “Zoho JO” numbers (**67 US / 36 AU** over two years) are **Zapier uploads into Ads**, not a count of this CRM. In 90 days alone this CRM has **110 USA + 127 AU job orders**. The Ads number is a thin, duplicate-prone slice — not “how many job orders we got.”
- About **1 in 6 enquiries ever stored a Google click id** (`utm_gclid` on **576 / 3,433** enquiries). On **job orders** it is almost gone: **18 / 782**. The newest 30 enquiries: **zero** click ids. So even when someone came from ads, Zoho often cannot prove which click.
- New paid pages on **virtualcoworker.app** are **not writing into Zoho**. Today’s CRM still looks like WordPress / Zapier / humans (a user called **Social Marketing (Lois)** created 21 of the last 30 enquiries).
- Junk is mixed in on purpose and by accident. Last 90 days, **86** enquiries are marked **Junk Lead**, **98** **Not a Fit**, **111** **Unresponsive**. Newest sample includes a Philippines “N/A” website junk row, and Contacts include Philippines people coming from **Zoho Desk** (staff/candidates, not US employers).
- Agency leftover: **Peter Mill** (`profitmill.io`) is in the user list as **deleted Administrator** (twice). **17 of 38 seats are Administrator.** George’s active seat is `shoutgeorge.com` (Standard). An old Gmail George seat is deleted.

---

## Volume (honest census)

| List (what sales sees) | All-time | Last 90 days | Same window as the Ads forensic (from 1 Aug 2024) |
|---|---:|---:|---:|
| Sales Enquiries (Leads) | 3,433 | 647 | 3,433 |
| Job Orders | 782 | 242 | 782 |
| Placements (Deals) | 386 | 122 | 386 |
| Contacts | 8,011 | 102 | 8,011 |

All-time and “since Aug 2024” matching means either this CRM started / was rebuilt then, or older history was imported with new dates. We did not download the whole database.

**Last 90 days — Sales Enquiries**

- Region: **USA 338 · AU 283 · blank 26**
- Source: **Website 550** · blank 57 · Forbes 10 · Phone 7 · Zen Desk 7 · Google **6** · referral 6. “Google” as a source is almost unused — paid clicks are probably dumped as **Website**.
- Form source: **Job Order Form 222** · blank 425. Gravity Forms ID field exists and is **empty on every record**.
- Status (what sales did with them): Job Order Submitted **213** · Unresponsive **111** · Not a Fit **98** · Junk **86** · Brochure sent **63** · follow-ups / not ready / no-shows make up the rest. **1** already marked Placement.

**Last 90 days — Job Orders**

- Region: **AU 127 · USA 110 · blank 5**
- Status: **Placement 95** · **Cancelled 97** · Endorsed candidates 17 · Sourcing 8 · plus a long tail of interview / feedback states. Almost half the job orders in 90 days were cancelled.
- Click id filled: **18 all-time**. Recruit id filled: **8 all-time** (and those 8 showed up in the newest 30 — Recruit sync looks new or unused).

**Last 90 days — Placements**

- Region: **AU 46 · USA 35 · blank 41**
- Stages are after the hire (New Placement, Day 1 check-in, 1 month check-in, Cancelled…). This is ops, not a Google click.

---

## Sample of what’s landing now (names + company only)

Newest sales enquiries are a mix, not a clean paid-employer pipe:

- Cheyenne logging phone / referral / Google (one Google row already **Junk**).
- **Social Marketing (Lois)** dumping Website rows — some look like real AU/US businesses (Physio to You, Naparoo, Obzervr), some look like junk (company “N/A”, Philippines).
- Statuses on those 30: 6 junk, 4 not a fit, 4 already **Job Order Submitted**, 5 discovery booked.

Newest job orders look like real hiring work (Fire Service Plus, Outback Distilling, Real Advantage Title) **plus tests** (“agent assign test”, “zoflowx august 11”). Created mostly by **Caitlin**. 7 of 30 still had a click id; utm_source on those was `google` / `googleads` / `(direct)` / `chatgpt.com`.

Contacts are not “employer leads.” Newest 30 include Philippines people from **Zoho Desk** and company contacts added by recruiters. **8,011 contacts vs 102 new in 90 days** — that list is a long-term dump, not the paid-search inbox.

---

## What’s broken / missing for Ads conversion import

Do **not** turn Zoho into a Primary Google Ads conversion.

1. **Click ids are the missing link.** Google can only import an offline conversion if the CRM still has the original click id. Enquiries: 576 ever. Job orders: 18. Newest enquiries: 0. That is not a pristine import.
2. **Zapier already built a second meter in Ads** named `Zoho JO Submitted … via Zapier` (and a duplicate “Standard OCI”). Turning Zoho on again without one definition will **double-count**.
3. **“Website” ≠ “Google Ads.”** 550 of 647 recent enquiries are sourced Website. Only 6 say Google. You cannot filter “paid search leads” from source alone.
4. **`.app` is not in this CRM.** Paid microsite forms are not writing here. WordPress / Zapier / humans still are.
5. **Job order ≠ paid click ≠ hire.** 242 job orders in 90 days, 97 cancelled, 95 placement. Ads’ 67/36 over two years is a different object.
6. **Junk and job-seekers sit in the same lists.** Junk Lead, Philippines contacts, test job orders. Importing “every Zoho create” would teach Google the wrong thing.
7. **No native Google Ads / CallRail / Calendly app showed up** in the module list. Tracking is home-grown UTM fields plus Zapier. Twilio/Sinch SMS and Zoho Sign are installed. Webhook settings were not readable with this login.

---

## What is actually usable

- This org is the **real sales book**: enquiries → job orders → placements, USA and AU together.
- Sales already has a human status that means something (**Job Order Submitted**, **Placement**, **Junk Lead**). That is useful **later**, as a *downstream* signal, after someone names the exact status that should count.
- Historical `utm_gclid` on **576 enquiries** is a research stash — not a live Ads import. Do not bid on it.
- User list shows who still has a key (and that Profitmill is gone).
- We can keep reading without turning writes on.

---

## Job Orders vs the “67 US / 36 AU” story

**Those Ads numbers are not a myth that “Zapier never fired.” They are a myth that “that’s how many job orders we got.”**

- Ads (forensic window 1 Aug 2024 – 12 Aug 2026): **67** US + **36** AU conversions on `Zoho JO Submitted … via Zapier`, plus extra counts on a second “Standard OCI” action (23 US / 14 AU). Those are **uploaded clicks**, marked secondary, not proof of hires.
- This CRM, same years: **782 job orders** (110 USA + 127 AU in the last 90 days alone).

So the agencies wired a Zap that sometimes told Google “job order,” while sales logged many more job orders that Google never saw — and Google also saw form/phone/Calendly conversions that were not job orders. Nobody was looking at the same object.

---

## Who’s in the CRM (no emails)

38 users: **29 active**, 6 deleted, 2 disabled, 1 closed. **29 licenses purchased. 17 Administrators.**

Active names include Caitlin (CEO profile), Cheyenne, Holly, Eliah, Charles, the **Contracts** mailbox, **Social Marketing (Lois)**, **Web Master** (read-only), and George (`shoutgeorge.com`, Standard).

Not Virtual Coworker addresses: Peter Mill **profitmill.io** (deleted, Administrator) — likely agency leftover; Maricor on zohomail (closed).

---

## Guardrails this pass

- Zoho: read only (~80 API calls, small samples, no full export)
- Google Ads API: not called
- `ZOHO_CRM_ENABLED`: false
- Brand: not enabled
- Email: **not sent**. No CEO draft — findings first. A note to Braden/Caitlin is only worth writing after one ops question below.
- No new X-ray page

---

## Recommended next human step

Ask **Caitlin or Cheyenne** (they own this CRM day to day):

> When a real employer becomes a job order, is that the **Job Orders** list, status **Job Order Submitted** — and is the old Zapier “tell Google Ads” still on? Also: who is the Zoho user **Social Marketing (Lois)**?

Until that is answered, do not enable Zoho writes, do not make Zoho a Primary conversion, do not Enable Brand.

I can keep reading (older enquiries with click ids, Lois/Zapier creator split) if useful. **None required today.**
