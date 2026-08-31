# We cannot pull MyOutDesk’s full keyword book from a landing page

18 August 2026. Internal. **Do not fetch URLs that carry utm, gclid, gbraid, wbraid, or gad_campaignid.** Those hits land in their analytics.

## Plain answer

One paid click URL shows **one** keyword and some campaign/content labels. It is not their Google Ads account. Cursor cannot scrape that link and reverse-engineer every bid.

## What a tracked click actually exposes

A destination with `utm_*` + `gclid` / `gbraid` + `gad_campaignid` tells you:

- the **landing page** they chose for that click
- often **one** query (here: `virtual assistant in the philippines`, exact)
- campaign / ad-group / creative names they put in the URL

That is one row of traffic, not the account.

## What we already have (do not crawl again)

Public LP reconstruction is done:

- 3,468 local slug candidates
- 324 GETs
- **5 live paid LPs**
- Role / agency / staffing slugs **404**

HTML does not contain their keyword list. Ads Transparency was an empty shell last pass. Re-running a huge crawl will not invent the missing book.

## What to use instead

- The five confirmed LPs and the campaign map already in `ads-launch/research/myoutdesk-2026-08-18/`
- Message-match from those pages (PH VA, generic VA, real estate, two brand URLs)
- Our own employer keyword clusters in `ad-group-recommendation.md`

Do not promise a dump of every term they bid on.

PREVIEW ONLY — NOTHING LAUNCHED. No Ads mutations from this note.
