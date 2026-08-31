# CRO / lead-quality backlog — 2026-08-11

Audit against live PPC microsite (`www.virtualcoworker.app`) + repo.
Doctrine: **buyer purity before volume**. Do not break forms, phones, quiz, gate, tracking, or active site experiments.

Operator checklist: [Launch Control](https://vc-xray.vercel.app/launch-control) → section **CRO / lead quality**.

---

## 1. Job-seeker “back” path — status

### Already solved (do not rebuild)

| Piece | Behavior |
|-------|----------|
| LeadGate intent | Hire vs “looking for a job” → `exitToCareers` |
| EngageChat | Same binary → careers |
| Quiz LP link | “Looking for a job?” → careers |
| Exit | `window.location.replace` to `https://virtualcoworker.com.ph` — Back does **not** return to the LP gate |
| Tracking | `job_seeker_redirected` / `job_seeker_interstitial_viewed` with `primary_eligible: false` |
| API | Job-seeker / spam rejected; never durable employer submit; never Ads Primary |
| Employer footers | No careers promo (2026-08-07) |

### Shipped 2026-08-11 (hygiene)

PH interstitial (`/ph`, `/ph/apply`) no longer prompts “use US/AU in the footer.”
PH footer no longer shows “US employers / AU employers” cross-links.
Destination copy stays: **Looking for a job? Apply on Philippines careers.**

### Remaining (low priority)

- Soft popup + chat launcher **on hold** (2026-08-14) — they obscure the LP, especially mobile. A/B vs clean LP later. See §4.
- No session flag for “already identified as job seeker” (unnecessary while `replace` exits the host).
- WordPress `.ph` site is outside this repo — cannot control back-links there.

---

## 2. Lead magnets (tools, not PDFs) — recommend 2–3 only

Inspected: role categories, form chips (size + seats), quiz branching, RSA/cost/efficiency messaging, lead-value model.

### Ship order (when built)

#### A. **US/AU hire vs PH remote cost comparison** (MVP #1)

| Field | Spec |
|-------|------|
| **Intent** | “virtual assistant cost”, “hire VA”, “offshore staffing cost”, savings-framed RSAs |
| **Surface** | Mid-page tool on `/us`, `/au` + optional `/us/virtual-assistant` (or generic LP section). **Not** a new ad campaign until CORE proves demand. |
| **Inputs** | Role type (chips), seats (1 / 2–3 / 4+), rough local salary or “use our benchmark”, market (US/AU auto) |
| **Immediate result** | On-page range: estimated monthly cost local hire vs PH dedicated seat + “what you get” bullets (recruit / shortlist / you interview). No fake precision. |
| **Lead fields** | Role + seats = qualification. Email **after** first result (“Send this estimate + next steps”). Phone/company optional until consult CTA. |
| **Anti bait** | Full estimate visible before email; email enriches (“email me this plan”), does not unlock blank page. |
| **Events** | `tool_started`, `tool_result_viewed`, `tool_lead_capture` → then existing employer form path / `employer_inquiry_submitted`. Never Ads Primary on tool-only. |
| **Zoho** | Same employer lead + `source=cost_calculator`, role, seats, modeled savings band, size if asked. |
| **Scoring** | Seats + company size (if collected) drive value; urgency optional; role category for routing. |

#### B. **Which VA role first** — extend existing quiz (MVP #2, do not duplicate)

Live `RoleQuiz` already is this magnet. Improve later (see §3); do **not** ship a second role-finder.

#### C. **Delegation / staffing readiness score** (MVP #3, after A)

| Field | Spec |
|-------|------|
| **Intent** | Pain / “overwhelmed” / “what to outsource” search themes |
| **Surface** | Secondary section or quiz LP companion — after cost tool has data |
| **Flow** | 5–7 checklist taps → readiness score + “delegate first” recommendation → soft gate to form |
| **Email** | After score, same pattern as A |

### Explicitly deprioritize

Webinar signup, gated generic PDFs, ten parallel tools, “downloadable hiring plan” as PDF-first.

---

## 3. Quiz — improve, don’t replace

### Live today

- Homepage: 3-step employer role quiz → scroll to `#gate`
- `/us/quiz` · `/au/quiz`: + size/seats chips → compact LeadGate (`assumeEmployer`)
- Job-seeker: text divert on quiz LP only (no in-quiz hire/job step)
- Ads: `VC_*_S_QUIZ` **Paused**; LP ~70% — rework later (Launch Control)

### Do not do now

- Replace live quiz with a longer BANT flow site-wide
- Enable quiz ads
- Redesign quiz as full-page hero without George’s go

### Experiment outline (when capacity)

| Test | Arms | Success |
|------|------|---------|
| **Length** | A = current 3–4 step · B = 2-step (role + seats only) | `quiz_completed` → form start / submit rate on paid traffic |
| **Urgency chip** | Off vs `HIRING_TIMELINE_OPTIONS` (already in `lead-value.ts`, not in UI) | Form complete rate + CRM usefulness — watch for drop-off |
| **In-quiz job-seeker gate** | Link-only (today) vs first-step hire/job | Job-seeker divert rate ↑ without hurting employer starts |

Priority: **job-seeker filter hygiene > quiz length test > urgency chip**. Quiz ads stay paused.

---

## 4. Popup + chat — on hold (2026-08-14)

| Fact | Detail |
|------|--------|
| Components | `ExitIntent.tsx` · `EngageChat.tsx` — code stays in repo |
| Live? | **No.** George: they obscure the LP, especially on mobile. |
| Flags | Off unless explicitly true: `NEXT_PUBLIC_ENABLE_EXIT_INTENT` · `NEXT_PUBLIC_ENABLE_CHAT` |
| Later | A/B vs clean LP (form / phone / gate) to pick conversions. Do not remount without George. |

Live filter today = LeadGate + quiz link. Escape dismiss already in popup code if we turn it back on.

---

## 5. Sales video — production brief (no asset yet)

**Do not embed** until an approved file exists. No autoplay. No fake testimonials.

### Goal

~60–75s employer explainer: what VC is, why PH remote staff, roles, screening, cost/efficiency **without unsupported claims**, CTA book call / tell us the role.

### Placement options (test later)

1. Below hero, optional (thumbnail click-to-play) — least risk to LCP  
2. Near trust band  
3. Adjacent to form for hesitators  

Primary conversion remains form / qualified call — **not** video complete.

### Tracking (when live)

`video_start` · `video_progress` at 25/50/75 · `video_complete` · `video_cta_click`  
All observation-only; not Ads Primary.

### Script outline

1. (0–8s) Hook: week is full / hiring eats the calendar  
2. (8–25s) Offer: dedicated Filipino teammates, you interview, we recruit/screen  
3. (25–40s) Roles: admin, books, marketing, CS, sales — match existing categories  
4. (40–55s) Proof: only **verified** scale/social (Google/Clutch/since year — no invented logos)  
5. (55–75s) CTA: Call / send the role — obligation free  

### Shot list

B-roll: office collaboration (stock or approved), screen UI of process steps, role portraits already on site, logo end card. **No AI faces presented as real staff/customers.**

### Dependencies

Approved VO + edit · poster frame · CDN/hosting · Lighthouse check · George approval before LP insert.

---

## 6. Veo / AI video — investigate only

- No Veo credentials or config in repo / `.env.example`
- First MVP (later): short **non-human** motion graphics / B-roll variants for ads — not LP hero, not fake people-as-customers
- Needs: API access + billing controls · asset bucket/CDN · human approval gate · cost cap per month
- Effort: discovery 0.5d · MVP pipeline 2–4d after access — **after** sales-video brief has a human-shot path

Guardrails: no fake testimonials; no “meet our team” with generated faces; human review before publish.

---

## Priority stack

1. Job-seeker filtering / conversion hygiene ← current  
2. Quiz + employer qualification (experiments, not rewrite)  
3. Cost-comparison tool MVP  
4. Sales-video production + optional embed  
5. Veo experimentation  
