# RSA + creative playbook — winners + competitors (2026-08-12)

**Source:** US RSA probe `LAST_14_DAYS` (`_us_rsa_probe.json`) · Executive creative themes · CEO comps (MyOutDesk, Wing, Magic) · George’s image feedback (beach / lifestyle faces can win).

**Build:** Editor CSV only — `build_rsa_winner_comp_us.py` → add + pause CSVs. No Ads API mutate (permanent). New ads **Paused**.

**Reads vs writes:** Google Ads API itself is fine. If pulls fail with `invalid_grant`, the local OAuth **refresh token** in `~/Developer/shoutgeorge-ads` expired/revoked — re-run `python scripts/generate_refresh_token.py` there. That restores read-only pulls. Creating/pausing ads still goes through Editor.

---

## Image lesson (George)

Warm **human faces** beat sterile “must look like an office desk” bias. Beach / lifestyle portraits can still get strong interaction if the person reads as a real teammate. Prefer Filipino talent energy over stock corporate bland. Keep headset / office too — don’t ban lifestyle.

---

## What our winning ads actually say

Themes with volume (exec creative, last 7d):

| Theme | CTR | Notes |
|-------|-----|--------|
| Hire Filipino / Philippines VA | ~10.6% | Explicit Philippines + Virtual Assistant |
| Dedicated teammate, not gig | ~10.4% | Anti-Upwork / anti-freelance |
| Agency / firm / company | ~11.1% | Staffing partner language |
| You interview. You pick. | ~9.8% | Control stays with buyer |

**Highest CTR RSAs (≥20 impr)** lean on:

1. **Plain search match** — “Looking for a VA?”, “Hire Filipino VA”, “Filipino Virtual Assistant”, “Virtual Assistant Agency”
2. **Philippines / Filipino / offshore** named in the headline (not buried)
3. **Dedicated seat** — not rotating freelancers / not Upwork
4. **You interview / you keep hire control**
5. **Role nouns** that match the query (Sourcer, Appointment Setter, Social Media, Customer Service)

**Caution:** The emotional ROLES pack (“Inbox Eating Your Week?”, “$8 an hour”, heavy pain copy) under-indexed on some AGs (e.g. Administration_EA_PH ~1.6% CTR on that RSA). Pain can work; **don’t drop Philippines + Virtual Assistant + dedicated seat.**

Paused **Offshore_VA_PH** RSA hit ~20.7% CTR / 31 clicks — that copy pattern is gold. Re-ship the *ideas* (spell out abbreviations for Editor policy) as new Paused ads.

---

## Competitor angles to steal (not brand names)

### MyOutDesk (CEO primary)
- CTA: **Book a Free Strategy Call**
- Outcomes: Hire in ~7 days · reduce admin overload · build teams · cost savings
- Social proof: reviews / clients served (only print numbers we can verify for VC)
- Visuals: real VAs at work, friendly faces

### Wing
- **Managed, not marketplace** — “own the work”
- Speed: live in ~48 hours
- Dedicated + supervised · cancel anytime energy
- Anti-freelancer framing (aligned with our winners)

### Magic
- Personal / busy-professional VA (weaker ICP fit)
- Steal carefully: dedicated to you · top-% talent · fast hire
- Don’t chase lifestyle-concierge as primary VC message

### SERP / Transparency
Chrome: Ads Transparency for myoutdesk.com · wingassistant.com · getmagic.com · plus a live SERP for `hire virtual assistant philippines`. Re-check weekly; paste new winning competitor lines into this doc.

---

## RSA rules for new winner-comp ads

- Spell out: Virtual Assistant, Philippines, Executive Assistant (no VA / EA / PH / DKI)
- Keep winning *meanings*: Looking for a Virtual Assistant? · Filipino · dedicated seat · you interview · not freelancers · staffing / agency
- Add comp CTAs: Book a Free Strategy Call · Hire in days (not fake “48 hours” unless ops agrees) · Reduce admin overload
- One `?` or one `!` max per ad (Editor punctuation)
- Final URLs = live role / hub LPs on `www.virtualcoworker.app`
- Ship **Paused** · CORE + ROLES only · Brand deferred

---

## Landing page implications (next CRO pass)

Align money LPs with ad promise:

1. Hero CTA stays **Book a Free Strategy Call** (MyOutDesk energy)
2. Above fold: **Philippines / Filipino dedicated teammate** + **you interview**
3. One line anti-marketplace (“not freelancers / not a gig bench”)
4. Speed / process: short hire path without inventing SLAs
5. Faces: keep human portraits (office *and* warm lifestyle OK)
6. Don’t over-index pain headlines that ads already tested soft

Site already simplified — this is copy/proof alignment, not a redesign.

---

## Import

1. Editor → **USA** → Get recent changes  
2. Account → Import → `google-ads-editor-rsa-add-winner-comp-us.csv`  
3. Preview = new Paused RSAs only  
4. Post · Enable the best after a few days of CTR vs incumbents  

AU twin later after AU GTM / goals cleanup.
