# Trust, auctions, and conversions plan — 15 Aug 2026

**Status:** Read-only. No live `.app` edits. No Ads mutate. Mock is a concept file only.

George’s Auction Insights names (do not add others):

**US:** Outsourcey, GetMagic, BruntWork, VirtualEmployee, LASolutions, WingAssistant, RemoteLeverage, FlexJobs, Indeed, TimeEtc.

**AU:** BruntWork, OffshoreMVP, Staff Domain, Upsource, Outsourcee, 24x7 Direct, Virtual Elves, Beyond the Maze, Your Phone's Covered, Tempo-Co, PH Offshore, Torino, Arc, Seek, Deel.

Confirmed live employer-staffing homepages this pass (not guesses):

| Name | Live URL | Notes |
|---|---|---|
| Outsourcey | https://outsourcey.com/ | `outsourcee.com` exists but parks to a lander — **not** the VA company. AU “Outsourcee” is Outsourcey. |
| BruntWork | https://www.bruntwork.com/ (`.co` exists, 403 to our fetch) | US + AU |
| VirtualEmployee | https://www.virtualemployee.com/ | India / multi-role shop; VA is one tile |
| Time Etc | https://www.timeetc.com/ | US-based VAs, 22,000+ clients since 2007 |
| Wing | https://wingassistant.com/ | Seen live earlier today |
| Remote Leverage | https://remoteleverage.com/ | Live |
| Offshore MVP | https://www.offshoremvp.com/ | AU-facing Philippines offshoring |
| Staff Domain | https://www.staffdomain.com/ | Australian-led PH/ZA teams |
| Upsource | https://upsource.com.au/ | ABN on footer; ISO; Cebu facility |
| 24x7 Direct | https://24x7direct.com.au/ | Melbourne BPO / PH VAs since 2001 |
| Virtual Elves | https://virtualelves.com.au/ | AU agency since 2009; ISO |
| Tempo Co | https://tempoco.com.au/ | Perth VA agency (not tempo.co news) |
| Your Phone’s Covered | https://yourphonescovered.com.au/ | Phone answering — adjacent, not staffing |
| Seek | https://www.seek.com.au/ | Job board |
| Deel | https://www.deel.com/ | Global EOR / payroll |
| FlexJobs / Indeed | flexjobs.com / indeed.com | Job boards |

**Not pinned to a unique homepage this pass (do not invent):** LASolutions.com, Beyond the Maze, PH Offshore, Torino, Arc. George still saw them in Insights — just no clean URL from this pull.

---

## Why you “aren’t getting clicks” (phone)

You **are** getting ad clicks. Last complete 7 days: US Core+Roles **406 clicks / ~$1,167**. AU Core+Roles **217 clicks / ~A$769**.

What you are not getting is **Ads conversions**, especially **phone**.

Those are different scoreboards.

### 1. Phone is designed to be quiet on the LP

On `/us` and `/au` the reasonably sized CTA is the **form**. Phone in the sticky bar is a small “Prefer to talk?” line, hidden while the form is on screen. Nav has the number, but the page is trained to convert on Book a strategy call, not a tap.

Competitors put the number (or “Let’s talk”) in gold/orange in the first viewport.

### 2. A phone *conversion* is harder than a phone *click*

| Action | What actually has to happen | Why volume is tiny |
|---|---|---|
| Call asset on the ad (mobile) | They see your ad **above** the competitor, tap Call, stay on | You lose **position above** to Outsourcey / Wing / etc. Call button often never appears |
| `tel:` tap on the site | Mobile user sees and taps 888 / 1300 | ~42% of recent paid sessions were **desktop** (GA snapshot). Desktop almost never “phone clicks” |
| 60s call from ads | Same + **60 seconds** connected | High bar. Cheyenne busy / miss / short tap = 0 |
| 60s website call | Google **forwards a dummy number** only after a real ad click cookie | Direct visit and fake `?gclid=` keep public 888. Verified 10 Aug. Most people who dial 888 from memory are **not** that conversion |

Site **does** fire dataLayer `phone_cta_clicked` / `phone_click`. That is **not** automatically an Ads conversion. Ads needs GTM (or the native click-to-call snippet) mapped to `VC_US_Phone_Click_Website` (`AW-962672995/Mr8ACIWr_d0cEOPyhMsD` on 10 Aug). Tracking page still treats some of this as unproven.

### 3. The Conversions column can ignore the VC actions even if they fire

13 Aug US inventory: every `VC_US_*` action was **Primary for goal = true** and **`include_in_conversions_metric = false`**.

**Today AU (API, 2nd call):** same pattern on `VC_AU_Thank_You`, `VC_AU_Calendly_Booked`, `VC_AU_Phone_Click_Website`, `VC_AU_Phone_Call_From_Ads`. All Enabled + Primary-for-goal + **not in the Conversions column**.

AU extras:

- Phone click is a **GA4 import**, not native Click-to-call.
- No `VC_AU_Phone_Call_From_Website`. There is a generic **Call (1300 886 740)** website-call action.
- Museum UA goals still sit **in** the conversions column (Chat, Submissions, Job order form…) all **HIDDEN** — junk account defaults, not Stage 1.
- Last 7d campaign metrics: **0 AU Ads conversions**. US had **1 primary** on Core, **0** on Roles (`all_conversions` 2 + 1).

Call 1 this afternoon (US conversion actions + metrics) failed: metrics.conversions cannot be selected on `conversion_action`. Did **not** retry US (quota rule). US flags above are 13 Aug disk + yesterday’s campaign counts.

### 4. Thank-you / other conversions

`VC_US_Thank_You` exists. GTM v6 was meant to map `employer_inquiry_submitted` only. Firing still **not proven** as a gclid-attributed Ads conversion (tracking.html still says map TBD; Launch Control later says verified — those docs disagree). Sales still got 14 US enquiries last week: the desk is working; Ads is not seeing it.

AU thank-you action exists in Ads. Campaign still shows 0. Either GTM is not firing with click ID, or the action is excluded from the column, or both.

Stay on **Maximize Clicks**. Do not flip Max Conv onto a column that is empty or half-wired.

---

## Why they sit above you (position above vs IS / abs-top)

Unchanged: **impression share** and **abs-top** count leftover auctions they skip. **Position above** only counts when you both showed. Maximize Clicks shops cheap clicks. CPC ceiling is already **$30 US / A$25 AU**; average CPC is **$2.50–$4**. Raising the ceiling further will not force Google to fight Outsourcey on the money terms.

### Who they actually are (plain)

**Same industry (Philippines / offshore staff):** Outsourcey, BruntWork, Wing, Remote Leverage, Offshore MVP, Staff Domain, Upsource, 24x7 Direct, Virtual Elves, Tempo Co. Homepages, fat nav, logo strips, named reviews, “book a call,” ISO/security theatre, $4/hr or 70% savings calculators. Outsourcey puts Shark Tank on the homepage. Upsource puts an **ABN** in the footer. Time Etc is a **US-based VA** mill with fake-precise “2,162,122 hours saved.” Virtual Employee is an **India IT shop** that happens to sell VAs.

**Job boards in your auctions:** Indeed, FlexJobs (US), **Seek** (AU). When the query is “virtual assistant,” they steal position from employer ads. That is not a landing-page problem; it is **who Google thinks the query is for**.

**Adjacent giants:** **Deel** (AU) is global payroll/EOR. **Your Phone’s Covered** is a receptionist/phone service. They will outrank you on overlapping words without being “another Virtual Coworker.”

### Landing pages vs you

| | `/us` `/au` (.app) | Competitors + **virtualcoworker.com** |
|---|---|---|
| What it is | Dedicated LP, form in the hero, thin nav | Full **homepage**: Services / Pricing / How it works / logo wall |
| Phone | Quiet, form-first | First-class button |
| Proof | Clutch/Google/LinkedIn chips, a few marks **below** the fold | Named clients, calculators, ISO, facilities, 700 videos / 22k customers |
| Domain | **`.app`** | **`.com` / `.com.au`** |
| Links | Few (good for a funnel, thin for Quality Score) | Lots (looks like a real company) |

Your **own `.com`** already looks closer to them (role grid, FBI-grade checks, Featured In, many quotes, Pricing). Paid Stage 1 sends people to `.app`. That is a legitimacy gap versus both the auction and the mothership site — not “nobody in this industry uses landing pages.” They use homepages **because** Google and buyers treat them as companies.

Whitespace / black space / badges / more links: yes. That is Quality Score landing-page experience **and** human “is this a scam?” in one package.

---

## What I would change (not today — George decides)

Priority is **measurement**, then **auction quality**, then **looks**. Looks will not register phone conversions that Ads is not allowed to count.

**A. Ads Goals (US then AU) — still Maximize Clicks**

1. Screenshot whether `VC_US_Phone_Click_Website` and the 60s call actions are **included in the Conversions column** (or listed under campaign-specific goals on CORE/ROLES). If they stay excluded, the column stays a desert.
2. GTM Preview: tap 888 on `/us` once. Confirm **one** Google Ads Conversion tag on `phone_cta_clicked` / `phone_click`, not the alias twice.
3. Same for `employer_inquiry_submitted` → `VC_US_Thank_You` (not page view, not alias).
4. AU: native click-to-call vs GA4 import; website-call 60s; put the `VC_AU_*` pipe checks in campaign goals; keep museum UA **out**.

**B. Funnel (Editor / site later — not this mock)**

- Make the number unmissable on mobile (Wing / Outsourcey style). Keep form. Don’t hide the sticky phone.
- Job-board negatives: Indeed / FlexJobs / Seek-shaped queries if they are already leaking (sniper list exists for some competitor brands). Don’t Broad.
- Do **not** raise Roles budget (lost-to-budget ~6–11%). Do **not** Max Conv on 1 event.

**C. Trust / LP (after A is proven)**

- Steal density from **your `.com`**, not a fantasy Fortune-500 logo wall. Role grid, process, office, ABN (AU), phone as a button, existing client marks in the first viewport.
- Keep `.app` URLs for tracking until George wants a `.com` paid destination. Don’t silently retarget Final URLs to WordPress.

Mock: `ads-launch/mocks/trust-lp.html` — US/AU toggle. Existing marks only.

---

## Chrome this pass (4 tabs)

1. Concept mock  
2. Live `/us`  
3. Live `/au`  
4. Outsourcey (on both Insights lists)

No other competitor tabs this round.
