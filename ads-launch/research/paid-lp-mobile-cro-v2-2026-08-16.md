# Paid LP mobile CRO V2 — visual rhythm (16 Aug 2026)

Prototype only. Live `/us` `/au` unchanged. Isolated mock: `ads-launch/mocks/paid-lp-mobile-cro-v2/`. Not a Vercel deploy.

Structure and pacing only. Do not copy competitor branding, layouts, cheap-labor prices, “top 1%,” or invented ROI.

## What competitors do on a phone

One idea fills the screen. Then space. Then a support line. Then one action. Then the next idea. The page is allowed to be long.

Inspected at mobile width (first-viewport rhythm, no forms submitted):

| Page | First screen (rhythm) | When they ask “what role / who are you” |
|---|---|---|
| **Outsourcey** | Huge H1 + one offer line. Benefits come later as separate beats. Form is far down. | After the sell. |
| **Magic VA LP** | Large H1, three short proofs, one CTA (+ a quieter secondary). Rest of the page is section-sized ideas. | Call is the ask. Role interrogation is not ATF. |
| **Wishup** | Large H1 + one price as a supporting line + one CTA. Then stacked arguments. | After the argument. |
| **BruntWork VA** | One offer (they lead with $/hr — **do not copy**). Reviews as their own beat. Contact later. | After the offer. |
| **VirtualStaff.ph** | One sentence H1 + one paragraph + one CTA. Price as a simple line, not a widget. Process after they understand the seat. | After the product is explained. |
| **VC live `/us`** | Headline + support + stars + progress + question + seven chips + job-seeker, all in a tight stack. Photo competes. | Immediately. Qualify before they believe. |

Shared mechanic (not a skin): **attention is sequential**. They spend height, not density. VC currently spends pixels.

## Live VC problem (the compression)

On 390px, `/us` tries to finish seven decisions in one view: what this is, whether to trust it, where you are in a quiz, what role, which chip, phone vs form vs careers. Type is small so it all fits. That is efficient with pixels and wasteful with attention.

## Proposed rhythm (this prototype)

1. **WHAT** — same headline: “Hire reliable Filipino staff who work your hours.” ~44–52px, wraps clean.
2. **DIFFERENCE** — one paragraph: dedicated offshore, FT/PT, hourly, recruiting + employment handled. Smarter expansion, not cheapest labor.
3. **TRUST** — “Staffing businesses since 2011.” Not a badge wall.
4. **ACTION** — one full-width gold button. Phone is available in the nav, not a third on-screen job.
5. Photo as its **own** moment.
6. Three statement sections, one each: *They work your hours.* / *We recruit. You choose.* / *We handle employment.*
7. Trust, big: 2011, then Google, then Clutch. LinkedIn 450K+ / Facebook 290K+ as supporting copy, not a chip dump.
8. One quote. How hiring works as four tall steps. Team photo.
9. **Then** guided-match — large question, large tiles, same type system. Role pages still skip the role step.
10. Contact PII last. Mock submit. Job-seeker only in the footer.

## Verified vs flagged

**Use (from `TRUST_PROOF` / live `/us` contract):** Since **2011**. US Google **5.0 · 39**. AU Google **4.8 · 23**. Clutch **4.9 · 7**. US phone **(888) 964-8644**. AU **1300 886 740**. Dedicated Philippines staff. FT/PT. Hourly (structure on the brief — no live price). Recruit → you interview → we handle payroll / employment admin. Quotes already on production (College Hunks, Good Co., Credit Card Compare, Buzinga). LinkedIn **450K+** (live 452,500 on 2026-08-11).

**Flag — do not inflate:**
- Facebook **290K+** is a CEO-approved floor (11 Aug). Live scrape was blocked; press Mar 2026 printed 257,000. Show the floor, do not invent a higher exact.
- Clutch sample is **7** reviews. Print 4.9 · 7. Do not imply a huge review base.
- No $ savings, % cheaper, “top 1%,” ROI, or competitor prices.

## Prototype vs production

This folder is a **local look**. Production `vision/` guided-match is untouched. When George approves, port composition — not a rebuild.

Screens (390 sequential + desktop): `ads-launch/research/screenshots/mobile-cro-v2/`.

Local preview (not production): `http://127.0.0.1:8765/mocks/paid-lp-mobile-cro-v2/index.html?preview=1`  
Compare: `http://127.0.0.1:8765/mocks/paid-lp-mobile-cro-v2/compare.html`

## Every meaningful change (prototype vs live `/us`)

| Change | Why |
|---|---|
| Quiz leaves the first screen | Sell before qualify. Headline + difference + 2011 + one CTA. Not seven decisions at once. |
| Type gets actual territory | Mobile H1 ~44–52px, section H ~34–42px, body ~20px. Competitors spend height; we were shrinking to fit. |
| More space in and between sections | One idea per band. Page is longer on purpose. |
| Hero action is “See how hiring works” | Continues the argument. Phone stays in the nav. “Tell us the role” appears after they have seen hours / choose / employment / 2011. |
| Photo is its own moment on a phone | No more copy + quiz + portrait fighting in one fold. Desktop still shows photo beside the new quiet hero. |
| Features become statements | *They work your hours.* / *We recruit. You choose.* / *We handle employment.* Not four cramped cards. |
| Trust is 2011 + ratings, not a badge wall | Google and Clutch as printed figures. LinkedIn 450K+ as support. |
| Job-seeker leaves the hero | Footer only. Employer is the page. |
| Guided-match still exists | Same steps, same events, large tiles. Role pages skip role. `employer_form_started` only on PII. Submit mocked locally. |
| No prices, savings, top 1%, ROI | Rates still “on the hiring brief.” Economic value = dedicated + FT/PT + hourly + employment handled. |
| Chrome hidden in screenshots | `?preview=1` |

Not changed on purpose: colors, Century Gothic + Poppins, phones, `/api/lead` contract names, thank-you query keys, Calendly URLs (visual overlay only in the mock), employer vs job-seeker split, since 2011.

**Still open if this ships:** sticky phone after scroll; whether the first gold button should say “Tell us the role” and jump; AU mobile pass; tracking density if gated later.
