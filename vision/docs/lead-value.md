# Lead value scoring (website modeled)

Central config: `vision/config/lead-value.ts`. Edit multipliers there — not in components.

## What this is / is not

| Signal | Meaning | Ads bidding? |
|---|---|---|
| Raw form fill | Someone submitted. Includes spam / job-seekers if they slip through. | **No** (observe only) |
| `lead_score` 0–100 | Internal preliminary quality | **No** |
| `estimated_lead_value` | Website **modeled $** (hypothesis ≈ $1k for a truly good lead) | **No — not yet** |
| Zoho Qualified | Sales-accepted employer lead | Later offline import |
| Job Order | Commercial commitment | Later |
| Placement | Revenue-adjacent | Later |

CRM / offline value **supersedes** the website estimate. Keep both in history. Do not pretend modeled $ is revenue.

## Chips (same labels everywhere)

- **Company size:** 1–10 · 11–50 · 51–200 · 201+
- **Positions needed:** 1 · 2–3 · 4–10 · 11+

**Homepage `/us` `/au`:** tap chips on the employer form. Optional. Do not add more questions.

**Quiz LP `/us/quiz` `/au/quiz`:** same two questions inside the quiz (gamified). Form after the reward is prefilled — no re-tap.

## Formula (deterministic)

Main drivers = **positions** (big dial) × **company size** (modest). Urgency is a small modifier.

```
score = min(100, 14 + size.score + seats.score + round(urgency × 10))
$     = clamp(80, 280 × sizeMult × posMult × (0.94 + urgency × 0.16), 1200)
```

| Size | score | $ mult | Seats | score | $ mult |
|---|---:|---:|---|---:|---:|
| 1–10 | 10 | 1.00 | 1 | 12 | 1.00 |
| 11–50 | 24 | 1.25 | 2–3 | 30 | 2.00 |
| 51–200 | 30 | 1.45 | 4–10 | 44 | 3.50 |
| 201+ | 18 | 1.28 | 11+ | 54 | 5.00 |

ICP note: 11–50 / 51–200 + multiple seats is the sweet zone. 201+ is **not** 3×. 1–10 / 1 seat ≈ $280.

- Job seeker → score 0, $0, “Not a fit”
- Missing chips → slightly below explicit 1+1 (“Let’s discuss”)
- Fit labels (internal only — **never show $ to the visitor**): Strong ≥ 72 · Good ≥ 48 · else Let’s discuss

Default urgency = 0.35 until hiring timeline chips exist.

Tune after 20 / 50 / 100 manually qualified leads. No ML.

## Payload + dataLayer (on durable employer submit)

`company_size`, `positions_needed`, `hiring_timeline`, `role` / `role_category`, `lead_score`, `estimated_lead_value`, `value_kind=estimated_modeled`, `fit_label`, `market`/`country`, `landing_page`, UTMs, `gclid` / `gbraid` / `wbraid`, `submitted_at`, `submission_id`, `lp_surface` (`form` | `quiz`), `cta_mode` / `landing_type` (`form_primary` | `quiz_lp`).

Server **recomputes** score — do not trust the client. No PII in analytics.

Events (same stack homepage + quiz LP):

- `quiz_started` · `quiz_step` · `quiz_completed` · `lead_magnet_completed`
- `employer_gate_selected` · `employer_form_started` · `employer_form_validation_error`
- `employer_inquiry_submitted` (+ alias `form_submit_success`)
- `phone_cta_clicked` (+ alias `phone_click`)
- `quiz_copy` / `gate_headline` experiment events

`bidding_primary: false`, `modeled_value_for_bidding: false`.

## Quiz LPs

- `/us/quiz` · `/au/quiz` — homepage chrome, quiz in the form slot. **noindex** until ads use them.
- Quiz is the hero. No employer form on first paint. Size + seats inside the quiz. Big reward, then form reveals (role/size/seats prefilled). Call still available (888-964 / 1300).
- Job-seeker: footer link to PH careers (not a first-screen “who are you?”).

## Zoho / offline (interface only)

`OfflineConversionDraft` in `lead-value.ts`. Stages: `crm_qualified` → `job_order` → `placement`.

No Zoho API writes from this work. No modeled $ into Ads bidding.

## Phones (do not change)

- AU **1300 886 740**
- US **(888) 964-8644** / `tel:+18889648644` (George 2026-08-10 restore; never 888-864 or 888-954)
