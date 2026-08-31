# Paid LP experiment plan — 16 Aug 2026

**Status:** Local mock only. George chose **Version One** as the direction (16 Aug). Version Two is backup — do **not** run both live. **Do not publish GTM or GA4. Do not change live `/us` `/au`. Do not mutate Ads.**

Context: 8–14 Aug US paid `/us` = 406 Ads clicks, 355 sessions, **2** enhanced `form_start` users, 2 thank-you users. Form is already in the hero. Failure is **almost nobody begins**.

## Test design (after George approves a challenger)

| Lever | Value |
|---|---|
| Market | **US first** |
| Control | Current `/us` form LP |
| Challenger | **One** prototype: **B — guided match / progressive quiz** |
| Split | 50/50, stable first-party cookie/assignment |
| Traffic | Keep campaign bids, budgets, keywords, ads constant |
| Do not | Three-way live split (355 US sessions/week would starve each arm) |
| Do not | US variant A vs AU variant B as a “winner” |
| AU | Replicate the **same** challenger only after **≥7 complete days** of reliable AU GA4. Do not compare raw AU CVR to US. |

### Metrics

| Role | Event / ratio |
|---|---|
| Early (directional) | `employer_form_started` / paid landing sessions |
| Business | Legitimate thank-you / `employer_inquiry_submitted` (durable) |
| Secondary | `phone_cta_clicked` |
| Diagnostic (B) | `quiz_step_completed` (step 1, step 2), engagement, bounce |
| Guardrail | Job-seeker leakage; junk/unqualified submits |

Do **not** declare a business winner from form-start alone.

On Prototype B, **form_start fires when contact fields appear / first PII interaction**, not when they tap a role chip. Role chips fire `quiz_step_completed` only. Otherwise we would congratulate ourselves for clicking “Admin.”

## Canonical events (one name each — no aliases)

Live code today **double-fires aliases**. Before any test, stop using them as GA4 events:

- `form_start` is an alias of `employer_form_started` (`LeadGate.tsx` / `tracking.ts`)
- `phone_click` is an alias of `phone_cta_clicked`

**Required for the test (dataLayer → GA4, both markets):**

| Event | When |
|---|---|
| `experiment_exposure` | Assigned variant rendered |
| `lp_primary_cta_clicked` | Primary CTA click (quiz continue / form submit button click — not just paint) |
| `employer_form_started` | First interaction with **contact** fields (name/email/phone) |
| `quiz_step_completed` | Prototype B only; `step` = 1 or 2; include chosen role / hours |
| `phone_cta_clicked` | `tel:` click (`is_qualified_call: false`) |
| `employer_inquiry_submitted` | Server accept + durable delivery (existing) |

Shared parameters on every event:

- `experiment_id` = `lp_paid_recovery_202608`
- `variant` = `control` \| `challenger_b`
- `market` = `us` \| `au`
- `landing_page_path` (e.g. `/us`)
- `device_category`
- `category` / role / `utm_campaign` / `utm_term` when already captured

Do not add a second GA4 tag that also sends `form_start`.

## Smallest measurement change **before** launch

`employer_form_started` already lands on the dataLayer. **GA4 did not receive a usable employer-form-started stream in the 8–14 Aug paid pull** (enhanced `form_start` was the only related signal: 2 US users). Forward the canonical event into **both** GA4 properties. Do not publish until George says so.

### GTM → GA4 (draft — do not publish)

**Containers**

- US: `GTM-M92DX9BJ` → GA4 `G-2V3V0BS6JW`
- AU: `GTM-5T6KPVSF` → GA4 `G-7X1K9V2LFE`

Do **not** mix the two.

**Per container, in Preview (not Submit):**

1. Confirm a **GA4 Configuration** (or GA4 Event settings) tag already points at that market’s Measurement ID.
2. New trigger: Custom Event, Event name **equals** `employer_form_started`.
3. New tag: **Google Analytics: GA4 Event**
  - Configuration: the market’s existing GA4 config
  - Event name: `employer_form_started` (exact)
  - Parameters: `experiment_id`, `variant`, `market`, `landing_page_path` (from DL or `{{Page Path}}`), `device_category` (from DL or GA4 built-in), `category`
4. Repeat the same pattern for `experiment_exposure`, `lp_primary_cta_clicked`, `quiz_step_completed`, `phone_cta_clicked`, `employer_inquiry_submitted` — **only if** that event is not already forwarded. One tag per event name.
5. Enhanced measurement: if GA4 already records generic `form_start` from the same fields, **do not double-count**. Either map enhanced `form_start` as a diagnostic only, or keep it and **do not** also send a duplicate under a second name. Canonical for the experiment = `employer_form_started`.
6. Preview on `/us` (US container) and `/au` (AU container): type **one character** in the name field, confirm **one** GA4 event `employer_form_started` in the debugger / DebugView.
7. **Stop. Do not click Publish.** Screenshot Preview for George.

If site code still pushes `form_start` alongside `employer_form_started`, add a GTM exception or a code change **at launch** so only one hits GA4. That code change is not in this research pass.

Ads conversions stay as they are (thank-you / phone). This measurement change is **GA4 observation**, not a new Ads bidding conversion.

## Prototype scores (1–5)

Higher is better, except **implementation risk** (5 = easy / low risk, 1 = hard / high risk).

| Criterion | Control | A Rescue | B Quiz | C Productized |
|---|---:|---:|---:|---:|
| Message match with paid queries | 4 | 4 | 4 | 4 |
| Strength + truth of offer | 2 | 4 | 4 | 4 |
| Trust above the fold | 3 | 4 | 4 | 5 |
| Mobile clarity | 2 | 4 | 5 | 3 |
| Initial perceived commitment | 2 | 3 | 5 | 4 |
| Authenticity of people/proof | 3 | 4 | 4 | 4 |
| Ability to measure | 3 | 5 | 5 | 3 |
| Implementation risk (5=easy) | 5 | 5 | 3 | 2 |
| Likely form-start impact | 2 | 4 | 5 | 3 |
| Likely qualified-lead impact | 3 | 4 | 4 | 4 |
| **Total** | **29** | **41** | **43** | **36** |

**C risk label: HIGH.** New IA (form not dominating first screen), more components, role pages must reuse the same architecture, and moving the form down can **hurt** the early metric we are using to learn.

**Challenger: B.** It is the only prototype that tests the recurring competitor mechanic that matches our failure mode: **first click is a hiring choice, not contact info.** A is the fallback if George wants the smallest ship. Do not launch C first.

## Assignment (when building, not now)

Stable first-party cookie `vc_exp=lp_paid_recovery_202608:control|challenger_b` set on first `/us` hit. Sticky 30 days. QA override `?exp=control` / `?exp=challenger_b` for screenshots only. Role LPs inherit the same assignment and **preselect** the role instead of a new design.
