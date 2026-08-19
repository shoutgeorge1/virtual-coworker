# Landing-page stakeholder feedback

Living checklist for paid LP feedback that should survive page replacement.
These pages are still experimental. Do **not** force every variation into one
design. Apply factual / qualification / UX fixes where safe. Re-apply the rest
systematically only after traffic identifies a baseline worth keeping.

Source: George email 2026-08-19 — “Landing Page Feedback Updates + Preserve for Baseline.”
Sales input included Cheyenne / team notes already encoded in the form (20-hour
minimum) plus later pricing and hiring-process wording.

## Apply on every employer form (now and later)

- [x] **Company Name** is present on employer enquiry forms.
- [x] **Company Name is mandatory** (client + server). Useful for sales
      qualification and to separate employers from job seekers / solo noise.
- [ ] Keep Company Name mandatory if a future form is rebuilt. Do not drop it
      to shorten the gate.
- [ ] Do not break `/api/lead`, email, Zoho, conversion events, or `/thank-you`
      / Calendly when adding fields.

## Pricing language (review again on the winning baseline)

- Prefer **“starting at”** when a role rate varies by job description.
- Approved US homepage language is already **From $7/hour** (price-led H1).
  Sales example: instead of “Admin around $8/hour,” use **“Admin starting at
  $7/hour”** where that matches approved company pricing.
- **Do not invent pricing.** Do not put USD rates on AU pages.
- Role H1s stay RSA / hours language, not a dollar lead (baseline rule).
- **Deferred on purpose (do not force onto live tests):**
  - Consult / offer / proof challengers were written **without** a live $7
    starting-rate promise. Adding one would change the test hypothesis.
  - `INDUSTRY_STATS` `~$8` on quiz `MarketLanding` is cited as industry VA
    rate guides, not the Virtual Coworker rate card. Do not silently turn it
    into company pricing without a source decision.
  - Systematic “starting at” on every role card / H1 waits for a winning
    baseline. Current published US role record (nouns only on role H1s;
    `US_PUBLISHED_RATES`) must be re-checked with sales before display.

## Hiring-process wording

- [x] Replace awkward “You meet people on video” with human language.
- Preferred: **“You conduct a video interview with your chosen candidate.”**
- Keep it short. Do not add a fifth process step or rebuild the section.
- [ ] Re-read hiring-process copy on the winning baseline with sales so the
      video-interview step stays accurate as the product talk-track evolves.

## 20-hour / week minimum

- [x] Visible next to Full-time / Part-time / mix selection on
      `GuidedMatchGate` and `LeadGate`.
- [ ] Keep the note next to hours chips on any future form. Short. No extra
      required question.
- Eligible part-time starts at 20 hours. Do not imply a lower floor.

## Sales-team review (once a page earns baseline status)

Re-open this list with sales before treating any experimental page as the
long-term baseline:

1. Company Name still mandatory?
2. Rate language still “starting at” / market-correct (especially AU)?
3. Video-interview step still natural and accurate?
4. 20-hour minimum still next to hours selection?
5. Any new sales objections that should become form or copy rules?

## What this pass did vs deferred

| Item | Now | Deferred |
|------|-----|----------|
| Company Name on `GuidedMatchGate` | Added + required | Re-check on any new form |
| Company Name on `LeadGate` / trust-first preview | Already present | — |
| US admin “around $8” → “starting at $7” | Category meta + variant A subhead | Industry-stat `~$8` card |
| Live $7 on consult / offer / proof | Not added | Only if that page becomes baseline |
| Video-interview wording | Shared how-it-works, baseline, offer, proof, capacity/time/teammate | Further tone pass with sales |
| 20-hour note on `LeadGate` (quiz LPs) | Added beside hours chips | — |
| Campaign / bid / URL / tracking changes | Not touched | — |

## Zoho / tracking honesty

`/api/lead` can return success (email + thank-you + Calendly) **without**
`zoho_synced: true`. Traffic-ready delivery and CRM write are separate
channels. A prior live test sent email and opened Calendly but did not create
a Zoho record.

Code path (unchanged this pass):

1. Validate employer lead (name, work email, phone, **company** required).
2. Durable channels: email / webhook / sheet / `zoho_webhook`.
3. Direct `zoho_crm` upsert maps `company` → Zoho standard `Company`.
4. Thank-you + Calendly run if durable delivery succeeds, even if CRM fails.

Live Zoho populate still needs a **human** test enquiry after deploy. Do not
treat unit mapping tests as CRM READY.
