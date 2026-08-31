# Draft — sitelink descriptions + LP / image notes · 2026-08-17

**Status:** Editor import file is written. **USA first.** Get recent changes → Import from file → preview description-only → **George Posts.** Do not Enable via API.  
Ads API this pass: **0 calls** (read or write). Titles + Final URLs from `google-ads-editor-sitelink-add-us.csv` / `-au.csv`. Copy tightened from this draft to customer-facing lines (≤35).

## What this is not

- Not Brand. Not Maximize Conversions. Not GA4 event import.
- Link titles and Final URLs stay as in `google-ads-editor-sitelink-add-us.csv` / `-au.csv` (Aug 12 add). `#gate` already stripped from those files.
- Callouts on CORE/ROLES are already customer-facing (`Vetted Filipino Talent`, `Employer Hiring Only`, `Interview Your Shortlist`, `Not a Gig Marketplace`, etc.). Left alone.
- Quiz sitelinks (paused with `VC_*_S_QUIZ`) use the same description strings — if quiz ever posts, they should match.

Limits: link text ≤ 25 · each description ≤ 35.

---

## 1. The three Google ad images

Downloaded 2026-08-17 into `ads-launch/research/google-ad-images-2026-08-17/` (gitignored; large).

| URL | What it actually is |
|---|---|
| `tpc.googlesyndication.com/simgad/5480269960590890638` | 1024×1029 PNG. Young professional woman (Southeast Asian), gray blazer over white shirt, smiling at camera at a desk. Soft office bokeh. Laptop corner in frame. Sign in the background: **PEOPLE CULTURE GROWTH**. Classic “your hire” portrait. |
| `tpc.googlesyndication.com/pimgad/9396371545467201869` | 768×768 JPEG. Young woman in a **bright blue polo + over-ear headset**, hands on a laptop, mouse and notebook on the desk. Open-plan floor with colleagues behind. Call-center / support-desk read. |
| `tpc.googlesyndication.com/pimgad/8608220603278716569` | 1024×1029 PNG. Young woman in a terracotta V-neck, gold hoops, black mesh chair, plant, laptop. Phone on the desk shows a **content calendar**. Closest in pose and lighting to VC’s own `va-us.jpg`. |

**Do not steal these files** as landing-page heroes. Treat them as CTR evidence of a pattern: a real person’s face, eye contact, desk, “this is who you’d get.”

### Vs current LP photos (live)

All four US pages (`/us`, `/capacity`, `/time`, `/teammate`) use the **same** hero: `/brand/va-us.jpg` — Filipino woman at a desk, navy top, gold hoops, mesh chair, plant, monitor. AU twins use `/brand/va-au.jpg` — Filipino man, blue shirt, wooden desk, mug, plant. Mid-page on the challengers: consult photo with a **Virtual Coworker ROLE BRIEF**, plus a Manila-looking team table. Closer: `/brand/hero-us-2026.jpg` (man in a glass US-style office).

So: capacity / time / teammate already use human staffing photography. They do **not** differentiate the photo. The high-CTR ads are the same *kind* of picture as `va-us.jpg` / `va-au.jpg`, except the headset/polo shot (image 2), which reads more BPO-floor than “dedicated teammate.”

**Recommendation:** keep the human-staff portraits on those pages. Do not swap in the headset floor unless we have a **VC-owned** equivalent. If we change photos later, use approved `vision` / brand / guided-match assets, and vary the hero **per concept** (teammate gets the person; capacity could use the team table; time could use a cleaner solo desk). Same conversion pipe. Not this pass.

---

## 2. Honest LP verdict

Live 200s checked 2026-08-17: `/us`, `/us/capacity`, `/us/time`, `/us/teammate`, and the AU twins.

**Control (`/us`, `/au`) was not edited.** Still `GuidedMatchLanding`. Gate, GTM, phones, role chips unchanged.

George’s “they only changed the H1” is **half-right for the eye, wrong in the DOM.**

### Same on all three challengers (and why they *feel* like H1 swaps)

- Same shell: `CapacityChallengerLanding`
- Same hero photo (`va-us.jpg` / `va-au.jpg`)
- Same proof strip: Since 2011 · Save up to 80% · No recruitment fees · You interview and choose
- Same compare table (freelancer vs job board vs VC)
- Same proof block (“staffing company since 2011”)
- Same 5 hiring steps, same FAQs (capacity FAQ inherited)
- Same GuidedMatchGate chips: Admin / EA, Bookkeeping, Marketing / Social, Customer Support, Sales, Recruiting / HR
- Same GTM

### What actually changes (more than H1)

| | `/us` control | `/capacity` | `/time` | `/teammate` |
|---|---|---|---|---|
| Template | GuidedMatchLanding | challenger | challenger | challenger |
| Eyebrow | none | For growing companies hiring staff | For owners whose week is already full | Staffing since 2011 - not a gig marketplace |
| H1 | Hire reliable Filipino staff who work your hours. | Get the work off your team’s plate - without another expensive local hire. | Stop losing your mornings to work a skilled teammate could own. | Add a reliable teammate - not another freelancer to manage. |
| Lead | Tell us the role. We recruit, vet and introduce… | capacity + payroll/HR | recurring work consuming the team | interview and choose a dedicated professional |
| Form intro | none | capacity / hours / hiring path | “role squeezing your week” | dedicated teammate, not a freelancer directory |
| Situation H2 | How hiring works | Your existing team is carrying work… | Recurring work is eating the hours… | You need someone in the business… |
| Outcomes H2 | — | Give the existing team time back | Mornings for the business | Dedicated professional you chose |
| Featured quote | default GM set | Kyrstin | David Boyd | Laura W. |
| Closing H1 | — | Give your team the capacity they’ve been missing. | Get the mornings back… | Hire a teammate you can keep. |

So: **not a one-line H1 swap in the source.** Eyebrow, lead, form intro, situation cards, outcomes, compare title, featured quote, and closing line all move. **Visually it still reads as one page with a different headline** because photo, strip, table, FAQ, and form are identical.

If we want them *materially* different later (proposal only — not shipped):

1. Different hero photo per concept, from **approved VC assets**.
2. Concept-specific first FAQ and process lead (time/teammate currently inherit capacity FAQs).
3. Do **not** touch GuidedMatchGate, thank-you, Calendly, GTM, or phones.
4. Keep `/us` and `/au` as the control.

---

## 3. Sitelink before → after (US + AU, same copy)

Same 8 unique sitelinks. CORE uses 6; ROLES uses 6; titles overlap. AU uses the same descriptions and titles; URLs swap `/us` → `/au` and `?market=us` → `?market=au`.

**Import files (description lines only; titles + URLs unchanged):**

| Market | File |
|--------|------|
| USA | `ads-launch/google-ads-editor-sitelink-descriptions-us.csv` |
| AU (same strings; later) | `ads-launch/google-ads-editor-sitelink-descriptions-au.csv` |

Builder: `python3 ads-launch/build_sitelink_descriptions.py`

| Sitelink text (unchanged) | Current desc 1 / 2 | New desc 1 / 2 | Why |
|---|---|---|---|
| Tell Us Who You Need | Employer hiring path / Form for businesses | Tell us the role you need / A specialist will follow up | Current reads like an internal routing label. Searcher should hear what happens if they click. |
| How Hiring Works | Recruit, vet, shortlist / You interview talent | We recruit. You interview. / You choose who starts. | Closest to usable already. Tighten so it is a process, not a checklist. |
| Take the VA Quiz | Find the right role / A few taps. Employers. | Find the right staff role / A short quiz for employers | “A few taps. Employers.” is ops-speak. Keep employer-only, drop the device jargon. |
| Hire by Role | Admin, books, marketing / Philippines staff seats | Admin, books, or marketing / Dedicated staff, your hours | “Staff seats” is inventory language. Outcome: a dedicated person on your hours. |
| Admin Support Hire | EA / admin category LP / Role-specific landing | EA and admin on your hours / Calendar, inbox, follow-up | Current is a CMS label (“category LP”). Say what the seat actually covers. |
| Bookkeeping Hire | Philippines books staff / Category landing page | Books done without local hire / Invoices, reports, your hours | “Category landing page” is ours, not theirs. |
| Digital Marketing Hire | Philippines marketing staff / Category landing page | Marketing help on your hours / Content, ads, and campaigns | Same internal second line. Drop “category.” Keep role truth. |
| Social Media Hire | Philippines SMM staff / Category landing page | Social managed on your hours / Posts, replies, your hours | “SMM staff” is agency shorthand. Searcher wants someone who owns the channel. |

Char counts (new): all descriptions ≤ 29. Link titles unchanged, all ≤ 22.

**URLs (unchanged, from sitelink-add CSVs):**

| Link | US | AU |
|---|---|---|
| Tell Us Who You Need | `https://www.virtualcoworker.app/us` | `…/au` |
| How Hiring Works | `…/how-it-works?market=us` | `…/how-it-works?market=au` |
| Take the VA Quiz | `…/us/quiz` | `…/au/quiz` |
| Hire by Role | `…/services?market=us` | `…/services?market=au` |
| Admin Support Hire | `…/us/administrative-support` | `…/au/administrative-support` |
| Bookkeeping Hire | `…/us/bookkeeping` | `…/au/bookkeeping` |
| Digital Marketing Hire | `…/us/digital-marketing` | `…/au/digital-marketing` |
| Social Media Hire | `…/us/social-media` | `…/au/social-media` |

Not pointing sitelinks at `/capacity`, `/time`, or `/teammate` in this draft. Those are message tests, not sitelink destinations, unless George later wants a separate add.

Paused clutter from the Aug 10 sweep — **not in the import CSV** (do not revive): **US Employer Home** — Generic Core landing / Not WordPress homepage. Live hub sitelink is **Tell Us Who You Need**.

Older Stage 1 import still has `#gate` on some Final URLs. The live-safe add CSV already dropped fragments. This draft does not put them back.

---

## 4. Ads / API

- **No Ads were changed by us.** CSV is on disk for George to import. He Posts.
- **Google Ads API: 0 probes, 0 mutates** this pass.
- Bid strategy stays **Maximize Clicks**. Brand stays deferred.

---

## 5. Editor — USA (one action)

1. Google Ads Editor → **USA** account (`496-715-1855`) → **Get recent changes**.
2. After that refresh, **Account → Import from file** → `ads-launch/google-ads-editor-sitelink-descriptions-us.csv`
3. Preview must show **sitelink description edits only**. Campaign Status blank. No keywords, no RSA, no Brand, no pause, no Employer Home.

Then stop. George Posts. AU is a second action with the AU CSV, only after USA preview looks clean.
