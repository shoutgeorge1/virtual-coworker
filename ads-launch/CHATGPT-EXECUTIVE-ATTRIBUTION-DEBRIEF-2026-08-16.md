# Virtual Coworker — Executive attribution debrief (for ChatGPT)

**Paste this whole file into ChatGPT.** Job: talk George through how to take credit for new-business volume when Google Ads is the only paid push, without turning a working-cost scoreboard into fake last-click CAC. Do **not** rewrite the live dashboard in this chat unless George asks. Do **not** invent buttons, Ads UI steps, or Zoho writes.

Live page George looks at: **https://vc-xray.vercel.app/executive** (hyphen). Repo bake: `xray/executive.html` from `xray/data/executive-snapshot.json` via `ads-launch/bake_xray_pages.py`.

| Field | Value |
|-------|-------|
| Date | Sunday 16 Aug 2026 |
| Repo | `/Users/george/Developer/virtual-coworker` |
| Snapshot bake | Ads pulled **2026-08-15 01:38 UTC** |
| Stage 1 live | `VC_US_S_CORE` / `VC_US_S_ROLES` · `VC_AU_S_CORE` / `VC_AU_S_ROLES` |
| Bidding | Maximize Clicks (Exact + Phrase). Not Max Conversions. |
| Brand | **Deferred.** Do not center this conversation on Brand remnants. |
| Zoho writes | **Off.** `ZOHO_CRM_ENABLED` stays false. Read-only census only. |
| Ads API | Read-only / 1–2 cheap probes. No mutations. Builds = Editor CSV. |
| Sales owners | Cheyenne Gichana = **US**. Holly Wallace = **APAC / AU**. Caitlin on maternity leave. |

George’s ask today: keep the look (cost / enquiry · cost / completed call · cost / job order · later cost / placement), stop using rolling “last 7 days,” use **fixed weeks**, bake about **once a week**, and figure out a fair way to take attribution for inbound that shows up as organic / website / Facebook / phone / referral — because he does **not** believe they are buying ads anywhere else, and last year they spent on the order of **a million dollars** on Google.

### Locked stakeholder pitch (George, 16 Aug 2026)

Do **not** talk him out of this. Tighten the one word if needed (see below), then help him pick weights.

> I’m using Cursor to pull Google Ads, take a read-only look at Zoho, and consolidate what Cheyenne and Holly send by email. That becomes a **weighted attribution** baseline for the week — cost per enquiry, cost per completed call, cost per job order, and later cost per placement. It’s not 100% accurate. We’ll tweak it. It gives you a picture of what you’re paying for new business while Google is the paid engine.

**Word to keep honest:** today the page is **not yet weighted**. It is spend ÷ that week’s inbound (junk still in the US 14). If George says “weighted” in the room, Cursor should actually apply weights next bake (job-seekers 0; Google-shaped channels high; Facebook / referral / Forbes lower; placements added when sales name them). Until that ships, “blended working cost / baseline we’ll tweak” is the safer synonym — same story, no one can ask “what are the weights?” and get a blank.

---

## 0. How to talk to George

- Plain English. Short. One decision at a time.
- He likes the page. Do not trash the design. Direction is locked: those four unit-economics tiles.
- He already knows the liberty: cost tiles are not Google last-click. He still wants some of that credit, on purpose.
- Distinguish **what he can say in a meeting** vs **what can drive bidding**. Those are different.
- Do not put “watch — organic may be paid” copy, chips, or amber banners on Executive. Stakeholders see Cheyenne’s labels as she wrote them.
- Do not recommend enabling Brand, writing to Zoho, or switching to Max Conversions in this pass.

---

## 1. George’s theory (treat as the working hypothesis)

1. Virtual Coworker is not running other paid media (no Meta spend, no Bing ads program he believes in). **Google Ads is the push on new business.**
2. Historically the old agencies spent ~**$1.18 million** (1 Aug 2024 → 12 Aug 2026) across US + AU Google Ads. Agency comparison on Executive: US **$724,880** / AU **A$458,167** in that long window. Production often **starts on Google** and later **surfaces as organic, website, phone, Facebook, referral.** Classic brand / demand halo, not last-click.
3. Therefore last-click `gclid` will always under-count. Waiting for click IDs before claiming any business impact is too tight for this company.
4. He is willing to take attribution for some website / organic / Facebook / random phone / referral-partner volume **while Google is the only paid engine** — labeled honestly as **estimated / working cost**, not “Google Ads produced this lead.”
5. North-star ladder on the scoreboard (same three tiles now, fourth later):

   **Cost per enquiry → cost per completed (or booked) call → cost per job order → cost per placement.**

6. Cadence: **fixed calendar weeks**, not a rolling last-7. He will look about **once a week.**

ChatGPT’s job is to help him pick **how much** of the inbox he is allowed to put in the denominator, and **what sentence** he says when someone asks “is this Google?”

---

## 2. What Executive is (and is not)

Executive is a **stakeholder scoreboard** for Braden, Cheyenne, Holly, Caitlin — not an Ads optimization console.

It currently mixes **two movies** on one page:

| Movie | Source | Tied to a Google click? |
|-------|--------|-------------------------|
| Ads traffic | Google Ads API (US + AU `VC_*`) | Yes — spend, clicks, impr, CTR, CPC, Ads conv |
| Unit economics | Cheyenne email (US) / Zoho census (AU) ÷ same-week `VC_*` spend | **No** — concurrent inbound |
| CRM halo | Zoho read-only, Stage 1 window vs a quiet baseline | **No** — volume while ads were on, 0 click IDs |
| vs prior agency | Old account CTR/CPC + Zapier JO uploads | Historical; old “conversions” were inflated |

`.app` forms email `us@` / `apac@`. They are **not** written into Zoho. Click stamps (`gclid` / `gbraid` / `wbraid` / UTMs) can live on the email. Live CRM still looks like WordPress + Zapier + humans. After ~5 Aug 2026, new Zoho enquiries stopped storing `utm_gclid`. Stage 1: **0 of 51** Sales Enquiries have a click ID.

So: Google can see **one** thank-you conversion. Sales can see **a normal week of inbox**. The tiles divide ads spend by that inbox.

---

## 3. Current numbers (bake 15 Aug 2026)

### US — Cheyenne email, Mon 10 Aug → Fri 14 Aug

- Spend used for cost tiles: **$844.94** (Core+Roles those dates)
- Cheyenne: **14 enquiries · 9 completed calls**
- Math: **$60.35 / enquiry · $93.88 / completed call · JO = dash**
- Quality inside the 14: 4 looking for work · 2 not a fit · 1 PH job-seeker
- Sources **as Cheyenne labeled them** (none say Google Ads):

  Google Organic 8 · Facebook 2 · Bing Organic 1 · Referral Partner 1 · Phone Call 1 · Forbes 1

- Same-week Zoho: **18 US Sales Enquiries · 0 click ID** (do not add 14+18)
- Ads last-7 (rolling, Aug 8–14): **$1,116 · 393 clicks · $2.84 CPC · 9.8% CTR · Ads conv = 1**
- That **1 Ads conversion** is the only Google-attributed thank-you (14 Aug, Core)
- Early sample Sat 8–Mon 10: $394.79 ÷ 4 enquiries = **$98.70 / enquiry** · 2 booked calls = **$197.40**

US cost tiles do **not** currently say “estimated.” Same math as AU. George likes the word **estimated**.

### AU — Zoho scoreboard, same Mon–Fri (Holly owns APAC)

- Spend: **A$670.51** Core+Roles 10–14 Aug (AUD; JSON field is named `cost_usd`)
- **13 enquiries · 2 discovery scheduled · 3 job orders submitted**
- Math (all labeled **estimated**): **A$51.58 / enquiry · A$335.25 / booked call · A$223.50 / JO**
- Booked-call denominator is a **proxy**: Discovery Scheduled, not Holly’s call log
- Holly: 1 Friday call she believes came through the new back-end; expects a JO next week — **already in the Zoho week, not added**
- Ads last-7 (rolling, Aug 9–15): **A$811 · 229 clicks · A$3.54 CPC · 13.1% CTR · Ads conv = dash**
- Click IDs: **0**

### Google vs GA4 (do not mix)

- Ads US conversions last 7d: **1**
- GA4 US property last 7d: marked conversions **0**; `/thank-you` **7 sessions** (page landings, not 7 Ads conversions)
- GA4 AU: thank-you sessions **0**; Paid Search sessions 52 (tags live since ~12 Aug)

### CRM halo (9-day Stage 1 vs quiet baseline)

| | Baseline Jul 1–9 | Stage 1 Aug 6–14 | Δ |
|--|--:|--:|--:|
| Sales Enquiries | 53 | 51 | −4% |
| Job Orders | 26 | 18 | −31% |
| Discovery scheduled | 0 | 4 | new |
| SE with gclid | — | **0 / 51** | — |

This block **undercuts a lift story**. Volume did not jump when `VC_*` turned on. That is expected while `.app` is not writing to Zoho and WordPress still is the CRM — but ChatGPT must not let George ignore it if he wants to claim “ads caused the inbox.”

### vs prior agency (fair to claim)

- US CTR 9.8% vs 1.6% · CPC $2.84 vs $8.29
- AU CTR 13.1% vs 1.4% · CPC A$3.54 vs A$9.24
- Old Ads “conversions” were forms, thank-you pageviews, Calendly opens, chat, phone taps, a thin Zapier JO upload (67 US + 36 AU vs **782** real job orders in CRM). Agency cost / Zapier JO: **$10,819 US · A$12,727 AU**. Enquiry/call was **not tracked**.

Traffic quality vs the old agency is a real win and does not need the lead tiles.

---

## 4. The window bug George already felt

Primary Ads KPIs on the page are **rolling last 7 days**. Sales-ops cost tiles are already a **fixed Mon–Fri**. They are not the same dates.

| Block | US dates | AU dates |
|-------|----------|----------|
| Ads “last 7 days” | Aug 8–14 | Aug 9–15 |
| Cost tiles (sales week) | Aug 10–14 | Aug 10–14 |
| Early CPL footnote | Aug 8–10 | — |
| CRM halo | Aug 6–14 vs Jul 1–9 | same |
| Impression share | last 7 *complete* days ending Aug 13 | same |

So US spend in the Ads row is **$1,116** (7d) while cost / enquiry uses **$844.94** (Mon–Fri). That is why the page feels slightly untrustworthy even when the math is documented.

**George’s direction:** kill rolling last-7 as the hero. Use a **fixed week**. Bake ~weekly after Cheyenne’s Friday US update (and Holly / Zoho for AU). “Today” can stay collapsed/secondary.

### Week definition to decide (do not pick silently)

Cheyenne’s email is a **US weekday** update. Weekend ads still spend.

| Option | Window | Pros | Cons |
|--------|--------|------|------|
| **A. Sales week** | Mon–Fri, matching Cheyenne | Matches the email he already gets | Drops Sat–Sun spend from the denominator’s numerator… wait: spend would also need to be Mon–Fri, so weekend clicks are orphaned |
| **B. Calendar week** | Mon–Sun (or Sun–Sat) | All ads spend in the week is in the math | Cheyenne’s Friday email won’t include Saturday–Sunday leads yet; bake Sunday/Monday after Zoho |
| **C. Cheyenne-complete week** | Mon–Fri leads + Mon–Sun spend | Simple for him | Mixes 5 days of leads with 7 days of spend — pessimistic CPL, easy to attack |

Recommend ChatGPT walk George to **one locked week** for **both markets**, same dates, spend and leads. Likely **Mon–Sun**, baked Monday after Cheyenne Friday + Holly/Zoho. Keep a footnote if Cheyenne’s email was Fri-only and weekend leads landed in Zoho.

US and AU must use the **same calendar dates**. Do not let timezone pull dates drift (that is how US last-7 and AU last-7 already diverged).

---

## 5. Three layers of “attribution” (keep them separate)

### Layer 1 — Proven paid (tiny today)

A Google click ID or a Google Ads conversion.

Today: **1 US thank-you**. AU: none. Zoho gclid: **0**.

This layer is what may eventually drive bidding. It is **not** the Executive hero yet.

### Layer 2 — Working cost / demand engine (what George wants)

`VC_*` spend this **fixed week** ÷ company inbound this week.

This is **unit economics while Google is the paid push**, not last-click CAC.

Fair **if**:

- labeled **estimated** or **working** on **both** US and AU
- junk is visible (job seekers / not a fit stay in the note, and optionally out of the money denominator)
- Cheyenne’s source chips stay as she labeled them (no “actually ads” rewrite on the page)
- the meeting sentence is: *“Google is the only paid engine. This is what the business paid per enquiry / call / job order this week, not a claim that every row clicked an ad.”*

Unfair **if**:

- used as Google Ads CAC in a deck
- imported into Ads as conversions
- used to switch to Maximize Conversions
- added to Cheyenne’s 14 + Zoho’s 18

### Layer 3 — Lift vs baseline (the uncomfortable check)

Did the CRM get busier when ads turned on?

Right now: **no**. SE −4%, JO −31% vs a quiet 9-day floor. That can mean: CRM isn’t receiving `.app` leads; Stage 1 is a cold start; junk mix changed; or ads have not yet moved the book.

George can still take Layer 2 credit **as a working cost** without claiming Layer 3 lift. ChatGPT should make him say which one he means.

---

## 6. How much of the inbox to put in the denominator

George said he does **not mind** taking website / organic / Facebook / phone / referral. ChatGPT should still offer **claim levels**, because “take some” is not “take all 14 including job seekers.”

Use US week as the example (14 Cheyenne enquiries, $844.94 spend).

| Claim level | Denominator | US cost / enquiry (approx) | What he is saying |
|-------------|-------------|----------------------------|-------------------|
| **0. Last-click only** | Ads conv = 1 (or gclid rows = 0) | ~$845–$1,116 per proven Ads conv | Too tight; matches Google; under-tells the business |
| **1. Sales-confirmed employers** | 14 − 4 looking-for-work − 1 PH job-seeker (− maybe 2 not-a-fit) → ~9 or ~7 | ~$94–$121 | Strongest “I will own this inbox” without counting junk |
| **2. Google-shaped halo** | Google Organic 8 + Phone 1 (+ maybe website if it appears) → ~9 | ~$94 | Takes the channels most likely to be ads-influenced; leaves Forbes / referral / Facebook / Bing out |
| **3. All inbound except junk** | 14 − obvious job-seekers | ~$70–$84 | George’s lean, cleaned |
| **4. All 14 (current page)** | 14 including junk | **$60.35** | Simplest; looks best; includes people who were never going to buy |
| **5. Zoho 18** | CRM census | ~$47 | Worse — different object than Cheyenne’s 14; still 0 gclid |

**Recommendation to debate, not impose:** lock **Level 3** (all inbound minus job-seekers / looking-for-work) as the **hero working cost**, keep Cheyenne source chips visible, keep Ads conv as a small separate KPI, keep JO / placement as the ladder rungs when sales names them.

Facebook / referral / Forbes: George may still take them under “only paid engine is Google.” That is a **company-economics** claim, not a channel claim. Fine in Layer 2. Do not relabel those chips to “Google Ads.”

Bing Organic: if they truly buy no Bing ads, treat like organic halo or leave out of Level 2. Do not invent a Bing campaign.

---

## 7. The ladder (this is the product)

Same three hero tiles US + AU. Fourth when sales will name a placement in the week.

| Tile | US now | AU now | What “good” means |
|------|--------|--------|-------------------|
| Cost / enquiry | $60.35 (not labeled estimated) | A$51.58 estimated | Working cost. Exclude job-seekers if Level 3. |
| Cost / call | $93.88 completed (Cheyenne) | A$335 estimated (discovery proxy) | Prefer **completed** when Cheyenne says completed; **booked** when only Calendly/discovery exists. Do not mix. |
| Cost / job order | — | A$223.50 estimated | Needs a named JO count from Cheyenne or Zoho **for that week**, not lifetime. |
| Cost / placement | not on page | not on page | Later. Placement ≠ JO. Some JOs cancel. Do not fake it. |

Agency comparison already shows enquiry/call were **not tracked**. That is why Stage 1 looking “cheap” vs $10k Zapier JO is easy to over-read. The honest contrast is: *they never had enquiry/call unit economics; we do, as working costs.*

---

## 8. What Cursor is doing technically (so ChatGPT doesn’t hallucinate a stack)

1. `ads-launch/pull_executive_snapshot.py` — **2 Ads API calls** (US `VC_US_%` + AU active campaigns), 14-day by-date, then Python splits last-7 vs prior-7. **This is the rolling window George wants to stop using as the hero.**
2. Cheyenne / Holly Gmail → `sales_ops_us` / `sales_ops_au` in the snapshot. Counts as **they labeled them**.
3. `ads-launch/probe_sales_ops_week_readonly.py` — Zoho **read-only**, capped. Never write. Quiet census on US; AU currently **is** the scoreboard because Holly’s email didn’t have a full week count.
4. `ads-launch/bake_xray_pages.py` writes static `xray/executive.html` (no “Loading”). Deploy: `cd xray && npm run deploy` → https://vc-xray.vercel.app
5. Impression share + GA4 are merged in when present (separate from the 2-call Ads budget).
6. Conversion pipe (separate from Executive math): thank-you `employer_inquiry_submitted`, phone click, 60s calls. Zoho offline import **deferred**. Do not attach museum Zapier/UA goals to `VC_*`.

Weekly ops rule (already locked): when Cheyenne or Holly sends an update — or it’s Friday and that market’s week is missing — put **that market’s week** on Executive and bake. Do not leave it in chat.

---

## 9. Decisions ChatGPT must get from George

Ask these in order. Do not skip to dashboard mocks.

1. **Week lock:** Mon–Sun vs Mon–Fri vs Cheyenne-Friday bake. Same dates US + AU.
2. **Claim level:** 1 / 2 / 3 / 4 from section 6. Which denominator is the hero?
3. **Label:** `estimated` on US as well as AU? Or `working`? George already likes estimated.
4. **Call definition:** completed (Cheyenne) vs booked vs discovery-scheduled proxy. One word per market, printed on the tile.
5. **Job seekers:** always out of the money tiles, or shown in the note only (current)?
6. **Facebook / referral / Forbes:** in the hero denominator or only in chips?
7. **Lift check:** keep the CRM halo on Executive (it currently looks like no lift) or move it off the stakeholder page?
8. **What he will say out loud** — lock a 2-sentence script. Suggested:

   > “Spend and the one Ads conversion are Google’s. Cost per enquiry is a working cost: what we spent on Search this week divided by the inbound sales logged this week. We are not writing the new site into Zoho yet, so almost none of those rows have a click ID. Google is the only paid engine; a lot of production shows up later as organic, web, phone, or referral.”

9. **Not for Ads bidding:** confirm working-cost tiles never become conversion imports.

If George says “just pick,” recommend: **Mon–Sun week, bake Monday, claim level 3, label estimated on both markets, job-seekers out of the money tiles, source chips unchanged, halo stays with “not ads causation,” Ads conv stays a small KPI.**

**If he uses the locked pitch (“weighted attribution”) in the room:** treat weights as the next Cursor bake, not as a reason to delay the pitch. Default starter weights to propose: job-seeker / looking-for-work **0**; Google Organic + phone + website **1.0**; Facebook / Bing / Forbes / referral **0.4–0.6**; then raise/lower once a placement week exists. Never import those weights into Google Ads.

---

## 10. Honesty rails (do not negotiate these away)

- Do not add Cheyenne email + Zoho census.
- Do not relabel Cheyenne’s “Google Organic” to “Google Ads” on Executive.
- Paid CAC with a click ID = **not yet** (0 gclid). Working cost ≠ paid CAC.
- A phone tap is not a 60-second call. Calendly open is not booked. Thank-you can be a test.
- Do not attach old account conversions to `VC_*`.
- Do not write to Zoho. Do not enable Brand as a strategy topic.
- Do not use this conversation to authorize Ads API mutations or production deploys unless George explicitly asks Cursor in the repo chat.
- Small type / density: George likes the direction, mildly hates the small text. If redesign comes later: bigger hero tiles, fewer IS decimals on the stakeholder page — not a new nav.

---

## 11. What “winning” looks like in 4–6 weeks

Not “Ads conv catches up to 14.” That will never match a mixed inbox.

Winning is:

- A **fixed week** on the page that matches the email he just read
- Estimated cost / enquiry / call / JO he can defend in one sentence
- Job-seekers visibly excluded from the money
- A second week, then a third, so the number isn’t a one-week vibe
- Proven paid (thank-you + 60s call) climbing as a **separate** column
- Eventually a placement tile from sales, not from Cursor guessing
- Still Maximize Clicks until the pipe is trusted

If weeks 2–4 of working cost stay ~$60–$120 / enquiry **after excluding junk**, and Cheyenne keeps completing calls, George has a story: *Google is expensive historically at the JO-upload layer; the new Exact system is producing a working cost the old agency never measured.* If JO and placement stay empty, the story is traffic-only — still a CTR/CPC win, not a sales win.
