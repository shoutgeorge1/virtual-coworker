# MyOutDesk paid-search reconstruction

Read-only. 18 August 2026. Human review only — no ads implemented.

Source of the seed click (analyzed locally, **never re-requested** with tracking):

- Landing page: `https://www.myoutdesk.com/lp/google-philippines-virtual-assistants/`
- `utm_campaign=LM_US_Virtual_Assistants_Outsourcing`
- `utm_content=Virtual_Assistants_Outsourcing`
- `utm_term=virtual assistant in the philippines_e`
- `utm_placement=c`
- `gad_campaignid=23338767511`

## Discovery method

Public, slow, cached GETs. Identified as a normal Chrome UA. `robots.txt` allows `/`. Sitemap has **zero** `/lp/` URLs.

| Step | Result |
| --- | --- |
| robots + sitemap-0.xml | 368 URLs. Services / industries / regions / careers / signup. No `/lp/`. |
| WordPress REST | Dead. Site is **Astro**. `/wp-json/` is the HTML 404 template. |
| Wayback `/lp/*` | False positive only (`lpmama`). |
| Common Crawl 2026-30 / 2026-25 | No `/lp/` captures. |
| Google Ads Transparency | Fetched `adstransparency.google.com?region=US&domain=myoutdesk.com`. App shell. **No creatives in HTML.** |
| Semrush / SpyFu / DataForSEO / SerpAPI | No credentials. Not used. |
| Google Ads Keyword Planner | Not called (1–2 call cap; not worth it here). |
| Local candidate universe | **3,468** slugs from VC keyword cache + sitemap twins + seed grammar. |
| Remote validation | Ranked GET queue, ~0.85s, cache under `cache/`. Soft-404 = HTTP 404 **or** title `Page Not Found \| MyOutDesk` + canonical `/404/` + shared hash `8bbc9b8f4dd498eb`. |

A 200 is not a find. Confirmed pages required: self-canonical `/lp/...`, `noindex, nofollow, noarchive`, employer form (`fullName` / `businessEmail` / `companyName` / `phoneNumber`), strategy-call CTA, unique body hash, and an H1 that matches the slug theme.

## How many paid landing pages were actually discovered?

**Five confirmed live paid LPs** (all `noindex`, all employer-form, all unique hashes):

| Slug | Title | H1 theme | Type |
| --- | --- | --- | --- |
| `google-philippines-virtual-assistants` | Philippines Virtual Assistants \| MyOutDesk | Hire a VA from the Philippines + 70% overhead | Geo |
| `google-virtual-assistants` | Virtual Assistants \| MyOutDesk | Award-winning VA services + 70% | Head term |
| `google-real-estate-virtual-assistants` | Real Estate Virtual Assistants \| MyOutDesk | Dedicated real-estate VAs | Industry |
| `google-brand-search-campaign` | Virtual Assistant Services \| MyOutDesk | Trusted leader | Brand |
| `google-brand-search-campaign-b` | Virtual Assistant Services \| MyOutDesk | You searched MyOutDesk | Brand challenger |

Plus **indexed commercial pages that are not paid LPs** (sitemap, typically indexable): `/services/*`, `/industries/*`, `/regions/*`, `/pricing/` (from $1,988/mo managed outsourcing), `/signup/` (7-day remote team), `/signup-discovery-call/` (`noindex`), `/careers/`.

`google-brand-search-campaign-a` and most brand truncations **404**. Singular / reversed PH slugs **404**. Almost every sitemap service/industry mirrored as `/lp/google-{same}/` **404**. Soft-404s are a real 404 template, not a catch-all that serves the seed page.

## How are pages organized?

**Combination — not a full role matrix.**

1. **Keyword / theme on the paid URL** — `/lp/google-{theme}/`. Theme is country, head term, one industry (real estate), or brand-campaign.
2. **Role is a module, not a URL** — admin, CS, SDR, bookkeeping, marketing, recruiting, TC, CRM, receptionist, EA sit on the generic/PH LPs as H3 cards. They do **not** get their own `/lp/google-bookkeeping/` (404).
3. **Industry is public IA first, paid twin only for real estate** — eleven industry sitemap pages; only real estate has a confirmed paid clone.
4. **Geography on paid is PH talent for US hours**, not US-city LPs. Talent hubs (Africa / APAC / LATAM) are **indexed region pages**, not `/lp/` twins in this pass.
5. **Employer vs job-seeker is a site split, not a paid split** — paid LPs are hire-side only. `/careers/` sends US corporate to ZipRecruiter and VA applicants to MyOutDesk Philippines.

## Keywords directly exposed vs inferred

**Directly observed (do not treat as theory):**

- Keyword: `virtual assistant in the philippines`
- Match: **exact** (`_e` suffix)
- Campaign: `LM_US_Virtual_Assistants_Outsourcing`
- Ad group / creative theme: `Virtual_Assistants_Outsourcing`
- Placement: `c`
- Campaign id: `23338767511`
- Brand-b campaign id (from an already-indexed URL, not re-hit): `12320808679`

**High-confidence inferred from live slugs / H1s:**

- `philippines virtual assistants`
- `virtual assistants`
- `real estate virtual assistants`
- `myoutdesk` (brand family)

**Inferred from campaign naming, not from a dedicated LP:**

- Outsourcing angle is in the **campaign name**, not in a live `/lp/google-virtual-assistants-outsourcing/` (that URL 404'd).
- Agency / staffing / Filipino / hire-a-VA slugs 404'd. Those themes are sold on the generic/PH templates.

## Messaging and offer (paraphrase, not for ad copy)

Shared paid-LP system:

- Conversion = **strategy session / find-your-VA form**, not a phone-first ATF.
- Hidden fields copy the full click-ID family (`gclid`, `gbraid`, `wbraid`, `fbclid`, UTMs, `first_landing_url`).
- Proof stack: 18+ years, 8,500+ clients, $140M saved, 4.9 Google, 0.7% pass rate, college degree, rematch, SOC 2, HIPAA. Brand-b adds CIS Level 2, PCI-DSS, NDA, US+PH legal entity, “as little as 1 week.”
- Offer frame: buy back time, cut overhead **up to 70%**, scale without local hiring drag.
- Pricing is **not** on the paid LPs. Public `/pricing/` starts managed outsourcing at **$1,988/mo** full-time, all-in.

Do not copy their sentences into Virtual Coworker ads. Do not adopt the 70% claim.

## Employer vs job-seeker

Paid LPs are employer-only (business email + company name required).

Job-seeker path is explicit and **off** the paid URLs: `/careers/` → ZipRecruiter (US staff) or Philippines VA apply.

That is cleaner than Virtual Coworker’s current risk: `Hire_VA_PH` search terms already include `virtual assistant jobs`, and the early US Zoho window had a job-seeker junk enquiry. MyOutDesk is not mixing those intents on the Google LPs we found.

## Campaign architecture (best reconstruction)

```text
LM_US_Virtual_Assistants_Outsourcing
  └─ AG Virtual_Assistants_Outsourcing
       └─ [virtual assistant in the philippines] exact
            → /lp/google-philippines-virtual-assistants/

[unknown generic VA campaign]
  → /lp/google-virtual-assistants/

[unknown real-estate campaign]
  → /lp/google-real-estate-virtual-assistants/

Brand Search
  ├─ /lp/google-brand-search-campaign/
  └─ /lp/google-brand-search-campaign-b/   gad 12320808679
```

`LM_US_` = Lead-style prefix + United States. Not proven beyond one click.

## Hit rate and learned grammar

See `probe-summary.json` / `myoutdesk-lp-probes.csv` for the live counts. Pattern that actually hits:

- `/lp/google-{country}-virtual-assistants/` — PH yes; Filipino no; reversed order no; singular no
- `/lp/google-virtual-assistants/` — yes
- `/lp/google-{industry}-virtual-assistants/` — **real estate only** among tested industries
- `/lp/google-brand-search-campaign[-b]/` — yes; `-a` and shorter brand slugs no
- `/lp/google-{sitemap-service-slug}/` — almost all no
- `/lp/{theme}/` without `google-` — **no** (unprefixed twins of all five confirmed slugs 404)

Blind spots: Facebook/Microsoft LPs, numeric campaign slugs, unpublished GrowthBook variants, city LPs, non-`google-` prefixes beyond a tiny test, and any LP never linked or archived.

## What we did not do

No forms submitted. No phones called. No Ads mutations. No tracking-parameter requests. No Keyword Planner. No claim that five LPs is their entire account — only that five survived a 3,468-candidate local universe and a ranked remote queue.
