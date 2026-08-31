# Recoverable-record candidates — 13 August 2026

**No uploads. Not “great leads.” Human review required.**

Google can only import an offline conversion if it still recognizes the **original click**. The CRM create date is not the click date. We did **not** ask Google whether any click id is still valid.

George guessed “perhaps 30–40.” The honest pool that even *looks* like a candidate is **smaller than that** once junk, ChatGPT source, and cancellations are removed.

Record ids: `.local/zoho/probe-attribution-recovery-2026-08-13.json` (gitignored). No emails or phones in this file.

---

## Window facts (cheap COQL, 13 Aug 2026)

| Set | Count |
|-----|------:|
| Enquiries with `utm_gclid` all-time | 576 |
| … created in last **90 days** | **231** |
| … created in last **180 days** | 500 |
| Newest 30 enquiries with gclid | **0** (newest gclid enquiry: **5 Aug 2026**) |
| Job orders with `UTM_Gclid` all-time | 18 |
| … created in last 90 days | **18** (all of them; 20 Jul – 7 Aug 2026) |
| Those 18 with Sales Enquiry lookup | **18** |
| Placements with a click-id field | **0 fields found** |

So: click ids did not vanish from history. They vanished from the **current** enquiry pipe after 5 Aug, while job orders created through 7 Aug still sometimes carried an older stamp.

---

## Bucket A — Potentially recoverable after human review

**Definition used here:** job order created in the last 90 days, has a click id, has a Sales Enquiry link, Region USA or AU, `UTM_Source` is `google` or `googleads` (not ChatGPT), stage is not already cancelled, company does not look like an internal test. Still **not** an upload list.

**About 11 job orders** fit that screen. Company names only (for Caitlin/Cheyenne to recognize):

| Created (UTC) | Region | Stage now | Company | Source tag |
|---------------|--------|-----------|---------|------------|
| 2026-08-07 | USA | Endorsed Candidates | Real Advantage Title | google |
| 2026-08-05 | AU | Endorsed Candidates | Safeco | googleads |
| 2026-08-05 | USA | Pending Feedback | Rain City Fence | google |
| 2026-08-04 | AU | Scheduled Client Interview | Waterlily Exercise Physiology | googleads |
| 2026-08-04 | AU | Placement | Foxlaw | google |
| 2026-08-03 | USA | Endorsed Candidates | TDE | googleads |
| 2026-07-31 | USA | Waiting for IV Feedback | Box&Go Moving | google |
| 2026-07-28 | USA | Placement | Collectively Corp | google |
| 2026-07-23 | USA | Endorsed Candidates | Lumiriam | google |
| 2026-07-23 | USA | Placement | Kim4Kids | google |
| 2026-07-21 | AU | Client Assessment | MB Brick and Block Laying | googleads |

Matching recent **enquiries** marked Job Order Submitted with a click id (same week): Safeco, Waterlily, Rain City Fence. Those are likely the same people, not extra conversions.

### Why they are still not importable

| Check | Result |
|-------|--------|
| Valid-looking click id stored | Yes (length 55–92) |
| CRM timestamp after an unknown click | **UNKNOWN** — click date not in CRM |
| Google still recognizes the click | **UNKNOWN** — not checked in Ads |
| Already uploaded via Zapier / Standard OCI | **UNKNOWN** |
| Human-confirmed real employer | **Not done** |
| Named “this is the conversion we tell Google” status | **Not done** |
| `.app` vs WordPress origin | These look like the **old** pipe (Caitlin / Lois / googleads), not the new `.app` form |

If Caitlin says “yes, these are real job orders” **and** Raffie/Amanda confirm they were not already uploaded **and** Google accepts the click id, a **later** Secondary test of **one** record could be discussed. That is not this pass.

---

## Bucket B — Useful for historical analysis only

- **231** enquiries with gclid in 90 days, minus the handful above. Newest 20 of those: **10 Junk Lead**, plus unresponsive / not a fit / no-show. Created by Caitlin (`googleads`) and Lois (`Website`).
- **345** enquiries with gclid older than 90 days (576 − 231). Outside a typical 90-day import window.
- Job orders with gclid but `UTM_Source = chatgpt.com` (Church St Dental; Prime Aus Collective) — click stamp + ChatGPT source is mixed. Research, not Google Ads import.
- Cancelled job orders that still have a click id (Mana, Neff Cullen, MEDIA360VR).
- Ads museum counts (67/36 Zapier JO, 23/14 OCI). Good for proving the old meter was thin. Bad for bidding.

Do not bid on this stash. Do not backfill it into `VC_*`.

---

## Bucket C — Not usable

- Newest 30 sales enquiries (after 5 Aug): **no click id**.
- Entire `.app` funnel to date: **not in Zoho**.
- Enquiries sourced Website with no click id (most of the 647).
- Gravity Forms ID: empty forever.
- Placements: no click id to send.
- Zoho Calls (379): no click id.
- Philippines Desk contacts, company “N/A”, tests (`zoflowx`, “agent assign test”).
- Any record we would have to “enrich” by guessing the click.

---

## What human verification still needs (before any one-record test)

1. Caitlin: are the Bucket A companies real paid-search employers, and is the **Job Orders row** the object that should ever count?
2. Someone with Zapier: did any of these already go to Ads?
3. Amanda / Ads UI: does a click-id lookup still resolve? (Do not run a bulk upload to find out.)
4. Cheyenne: any of these already marked junk on the phone?

Until those answers exist, the gate stays **not ready**.
