# 05 — Employer-gate experiment plan

## Critical framing (do not misread)

Virtual Coworker **intentionally** separates:

1. Businesses hiring offshore staff  
2. PH / elsewhere job seekers  
3. Fraudulent job-seeker spam  

The “Are you looking for a job?” style question is **not** an accidental mistake.  
**Problem = positioning / implementation of the gate**, not that a gate exists.

**Hard rules**

- Job-seeker path must **never** fire Ads employer-lead conversion  
- Job-seeker path must **never** enter Zoho as a sales lead  
- Pop-up / modal is a **testable variant**, not assumed best  
- Baseline is **inline** on the paid LP  

---

## Goals

| Primary | Secondary |
|---------|-----------|
| Maximize **qualified employer** form starts & completes | Minimize job-seeker contamination rate |
| Keep Ads learning on employer-only signals | Reduce spam without crushing employer conversion rate |

---

## Variants

### Baseline — Inline gate (control)

| | |
|--|--|
| **UX** | On-page question before/within form: “I want to **hire** offshore staff” vs “I’m **looking for a job**” (radio or two clear buttons). No modal. |
| **Hire path** | Reveal / enable employer form + phone CTA |
| **Job path** | Redirect or inline message → careers/.ph or “we hire differently” page · **no** Ads lead event · **no** Zoho sales lead · optional `jobseeker_path` analytics-only event |
| **Why control** | Lowest friction surprise; matches “gate is intentional” without pop-up hostility |

### Variant A — Multi-step quiz

| | |
|--|--|
| **UX** | 2–3 step quiz: intent → role/need → company size → then form |
| **Hypothesis** | Extra employer-qualifying steps reduce spam and raise sales-accepted rate more than they hurt completion |
| **Risk** | Drop-off before form; mobile fatigue |

### Variant B — Pre-form modal / pop-up

| | |
|--|--|
| **UX** | On first CTA click or scroll-to-form, modal asks hire vs job before showing fields |
| **Hypothesis** | Interrupts accidental job-seekers earlier; may improve lead quality |
| **Risk** | Feels like a dark pattern; higher rage-close; **not assumed best** |

---

## Experiment design

| Item | Spec |
|------|------|
| Platform | Same paid host; `gate_variant` in URL or cookie (`inline` · `quiz` · `modal`) |
| Traffic split | 50/50 or 33/33/33 once ≥50 paid sessions/day; until then **Baseline only** |
| Markets | US first; AU copies winner |
| Randomization | Sticky per browser (localStorage) so thank-you attribution stays consistent |
| Duration | Min 2 weeks **or** 100 employer form completes across variants (whichever later) |
| Pause rule | If any variant’s employer completion rate &lt; 50% of control for 40+ sessions, pause that variant |

---

## Metrics

### Primary (decision)

1. **Sales-accepted employer lead rate** = accepted employers / paid clicks (manual review by Braden/team)  
2. **Contamination rate** = job-path selections + spam rejects / paid sessions  

### Secondary (diagnostics)

| Metric | Where |
|--------|-------|
| Gate answer rate (hire vs job vs abandon) | GA4 |
| Form start · form submit · thank-you | GA4 + Ads observe |
| Time to submit · field error rate | GA4 / server logs |
| CTR ad→LP (should be equal across variants) | Ads — sanity |
| Bounce / engaged session | GA4 |
| CallRail calls from LP | CallRail |
| CPC · search-term relevance | Ads — not variant-causal |

### Explicitly not primary at Stage 1

Ads “Conversions” column (untrusted until hierarchy locked).

---

## Winner rules

A variant **wins** if **all** are true vs control:

1. Sales-accepted employer lead rate **≥ control** (or within 10% relative **and** contamination ≤ control − 20% relative)  
2. Contamination rate **≤ control**  
3. No material mobile breakage (qualitative + error logs)  
4. Braden agrees copy/UX is on-brand  

**Ties → keep Baseline (inline).**  
Modal/pop-up never wins on “feels modern” alone.

---

## Implementation notes (no live changes in this package)

- Fire `gate_answer` with `{intent: hire|job, variant}`  
- Fire `employer_form_submit` only when `intent=hire` and validation passes  
- Job path may fire `jobseeker_path` to GA4 only (not Ads primary)  
- Document winner in `docs/rebuild/` + dashboard Clean Rebuild phase progression  

**Owners:** George (build/instrument) · Braden (accept/reject leads weekly) · George (call winner)
