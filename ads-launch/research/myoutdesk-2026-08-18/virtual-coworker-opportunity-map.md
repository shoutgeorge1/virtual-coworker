# Virtual Coworker opportunity map — vs MyOutDesk (US Search)

Read-only. 18 August 2026. Do not implement ads from this file.

Cross-walk uses existing local evidence only: `ads-launch/_rsa_challenger_review.json`, agency-intent Editor CSV, `xray/data/ga4-snapshot.json` (10–16 Aug), `xray/data/executive-snapshot.json`, `ads-launch/US-LP-DESTINATION-MAP-2026-08-18.md`, `ads-launch/US-SEARCH-RESTRUCTURE-2026-08-18.md`, Zoho lead-to-placement audit (gclid/quality facts, not a new CRM pull).

## What MyOutDesk does that we do not

They run **separate noindex paid LPs** for (1) Philippines VA, (2) generic VA, (3) real estate, (4) brand + brand challenger. Almost all US CORE clicks still land on `/us`.

They collect **company name + business email** on the paid form and keep job applications on `/careers/`. We still have job-seeker search terms (`virtual assistant jobs`) and one early US junk job-seeker enquiry.

They sell a **managed, full-time, all-in monthly** product (public price from $1,988/mo) with security theater (SOC 2, HIPAA, 0.7% pass). We sell recruit → vet → shortlist → employer interviews. Do not impersonate their managed-oversight model.

## What we already have that they did not bother to clone on `/lp/`

These clusters **404'd** as `/lp/google-*` twins. They only appear as cards on generic/PH LPs. Virtual Coworker already bids them and already has role URLs:

| Cluster | VC ad groups | VC LP | GA4 10–16 Aug |
| --- | --- | --- | --- |
| Bookkeeping | Bookkeeping_Hire_PH / Outsource_PH | `/us/bookkeeping` | 40 sessions, 47.5% engaged — **#1 role** |
| Customer service | Customer_Service_* | `/us/customer-service` | 22 / **68.2% engaged** — best role engagement |
| Sales / setters | Sales_* / Appointment_Setter_* | `/us/sales` | 19 / 63.2% |
| Digital marketing | Digital_Marketing_* | `/us/digital-marketing` | 17 / 29.4% — soft |
| Social | Social_Media_* | `/us/social-media` | 15 / 40% |
| Admin / EA | Administration_EA_PH | `/us/administrative-support` | 14 / **21.4%** — weakest |
| Agency / staffing | Agency_PH, Staffing_Agency_PH, VA_Agency_Firm_PH | `/us` ; `/us/staffing` candidate not Ads | CORE buyer signals: remote staffing agency, VA agency, PH outsourcing agency |

So: they out-build us on **geo, head-term, real estate, brand**. We already out-build them on **role URLs**. The hole is **message match on CORE** (PH + agency/staffing still share `/us`) and **not pointing ads at `/us/staffing` or `/us/real-estate` until measurement is clean**.

## Overlap with proven Virtual Coworker search terms

Executive buyer signals that match this reconstruction:

- `philippines virtual assistant agency` / `philippines outsourcing agency` — employer provider language. MOD has a PH **VA** LP, not an **agency** LP.
- `remote staffing agency` — our ST is real; also bleeds temp/remote-job. MOD has no staffing paid LP.
- `virtual assistant firm / company` — same. Their generic LP is “VA services,” not “agency.”
- `va workers ph` — messy. Ignore as a build theme.

RSA search-term overlap to treat as **proven demand**, not as MOD clones:

- Offshore / PH VA (`offshore virtual assistants`, `virtual assistant philippines`)
- Agency (`virtual assistant agency`, `va company`)
- Staffing (`remote staffing agency` + junk `remote temp agency`)
- Bookkeeping / CS / sales setters (role ST exists; MOD did not dedicate paid URLs)

## Missing VC ad groups / pages that deserve a dedicated landing page

Build **message match**, not a 20-page MOD clone.

1. **Philippines VA (CORE)** — they have `/lp/google-philippines-virtual-assistants/`. We send that intent to `/us`. Highest-leverage missing LP. Keep it employer-gated. Do not copy their H1.
2. **Agency / staffing (CORE)** — they **lack** this paid URL. We have the terms and a `/us/staffing` candidate that is deployed noindex and **not** an Ads destination. When measurement on `/us` is trusted, this is the page that matches how buyers already search.
3. **Keep role pages; do not invent MOD-style role `/lp/` clones** — bookkeeping and CS already work as URLs. Admin needs a page fix, not a new ad group.
4. **Real estate** — they have a dedicated paid LP; we have `/us/real-estate` and a WATCH flag. Controlled test only after GA4 `/us` events are trusted. Do not lead with ISA/cold-call.
5. **Generic `virtual assistants`** — they have a head-term LP. We already paused junk Exact on Hire_VA_PH. **Do not build a page to chase the head term.** Negatives + agency language.
6. **Brand** — they run two brand LPs. Ours stays **deferred**.

## Job-seeker themes to keep off US hire

From MOD: careers language (“become a virtual assistant”), ZipRecruiter, Philippines apply.

From our account: `virtual assistant jobs`, `companies looking for virtual assistants`, `virtual assistant companies hiring`, `i need a va careers`, city “hire VA” tests, Recruitment_Hire_PH junk.

Action: negatives (`job`, `jobs`, `salary`, `career`, `careers`, `apply`, `resume`, `work from home`). Do **not** global-negative `hire` / `hiring`. Pause Recruitment_Hire_PH as a source of talent queries.

## What to build first

1. **One Philippines-employer LP** (or a clearly PH-themed `/us` variant) for Offshore_VA_PH / Hire_VA_PH geo terms — because MOD already message-matches that click and we do not.
2. **Staffing/agency destination** — `/us/staffing` is already the candidate. Measurement first, then Ads Final URL. This is where our proven terms live and MOD has no paid twin.
3. **Protect bookkeeping + CS** — already our best role engagement. Do not merge them onto `/us`.
4. **Real estate later** — page exists; do not point until DebugView/`/us` events are clean.
5. **Ignore brand and generic VA head terms.**

No Editor CSV in this pass.

## Prioritized table

| Priority | Proposed VC ad group | Keyword cluster | Match type | Landing-page angle | Evidence | Job-seeker risk | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `Offshore_VA_PH` (keep; tighten) | PH / Filipino VA hire | Exact | Dedicated PH employer LP: screened Filipino staff, US hours, agency-hire — not 70% / SOC 2 theater | MOD seed LP + `virtual assistant in the philippines` exact; VC already bids PH terms onto `/us` | Medium — add job negatives | Observed |
| 2 | `Staffing_Agency_PH` / `Remote_Virtual_Staffing_PH` | remote / PH staffing agency | Exact | `/us/staffing` when measurement passes: provider/agency, not “VA jobs” | VC ST + Executive buyer signal; MOD staffing `/lp/` 404 | Medium — temp/job bleed already in ST | Observed |
| 3 | `VA_Agency_Firm_PH` / `Filipino_VA_Agency_PH` | VA agency / firm / company | Exact | Same staffing/agency page or PH LP with agency H1 | VC agency-intent list + ST `virtual assistant agency`; MOD agency slug 404 | Low | Observed |
| 4 | `Bookkeeping_Hire_PH` | bookkeeping VA / PH bookkeeper | Exact | Keep `/us/bookkeeping` | GA4 40 sess / 47.5% eng; MOD no paid bookkeeping LP | Low | Observed |
| 5 | `Customer_Service_Hire_PH` | CS / support PH | Exact | Keep `/us/customer-service` | GA4 22 / 68.2% eng; MOD lists CS only as a card | Medium — CSR job titles | Observed |
| 6 | `Hire_VA_PH` | hire a VA / dedicated VA | Exact only on 3+ word employer phrases | `/us` or PH LP; do not chase bare `virtual assistant` | MOD generic VA LP exists; VC already saw `virtual assistant jobs` | High on short head terms | Observed |
| 7 | Real-estate AG (not live) | real estate VA | Exact | `/us/real-estate` after measurement — lead follow-up/admin, not ISA-first | MOD dedicated RE paid LP; VC page exists; restructure = WATCH | Low-medium | Observed (MOD) / policy (VC wait) |
| 8 | `Sales_Hire_PH` | sales VA / setter | Exact | Keep `/us/sales`; do not expand setters | GA4 19 / 63.2%; restructure said pause setters | Medium-high | Observed |
| 9 | `Administration_EA_PH` | EA / admin | Exact | Fix `/us/administrative-support` (21.4% engaged) before more keywords | Weak GA4; MOD lists EA everywhere, no dedicated LP | Medium | Observed |
| 10 | `Brand_VC` | virtual coworker | Exact | Deferred | MOD has two brand LPs; VC Brand deferred | Low | Policy |
| — | `Recruitment_Hire_PH` | hiring / careers / VA jobs | Negative | Do not land on hire LPs | MOD careers split; our ST already contaminated | Very high | Observed |
| — | Generic `virtual assistants` | head term | Ignore / negative-watch | No new LP | MOD has the page; we do not want that traffic mix | High | High-confidence inference |

## Discovery stats

- Local candidates generated: **3,468**
- URLs tested: **324** (319 ranked `google-*` + 5 unprefixed twins)
- Confirmed paid LPs: **5** (hit rate 1.5% of tested)
- Missing / true 404 template: **319** (shared hash `8bbc9b8f4dd498eb` — not a catch-all LP)
- Learned: unprefixed `/lp/{theme}/` twins of all five confirmed pages 404 — `google-` prefix is required
- Redirects / uncertain: **0**
- Stopped after two consecutive empty batches
- Remaining blind spots: unpublished slugs, other ad-network prefixes (low-score, not in the 319), Transparency creatives, volume/CPC (no Planner), Zoho quality by keyword (`utm_term` sparse)

## Files

- `myoutdesk-paid-landing-pages.csv`
- `myoutdesk-inferred-keywords.csv`
- `myoutdesk-campaign-map.json`
- `myoutdesk-lp-probes.csv`
- `myoutdesk-competitive-reconstruction.md` (this folder)
- `cache/` — raw HTML
