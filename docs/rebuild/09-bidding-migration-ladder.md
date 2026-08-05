# 09 — Bidding migration ladder (Stages 1–4)

Matches strategic direction. **Do not skip stages** because volume is impatient.

---

## Stage 1 — Maximize Clicks (launch)

| Item | Spec |
|------|------|
| Bid strategy | **Maximize Clicks** |
| Max CPC limit | Set **only** if keyword/performance exports show a stable CPC band; otherwise omit and review daily |
| Primary Ads goal for bidding | Clicks |
| Conversions | Wired · **Include in Conversions = OFF** for employer actions |
| Success diagnostics | CTR · search-term relevance · CPC · GA4 engagement · form funnel · manual lead quality |
| Exit criteria | ≥2 weeks live **and** employer form+call tracking verified **and** ≥15 manually reviewed leads **or** clear search-term stability with lower volume |

**Why:** Legacy accounts used Max Conv (`PM_*_Brand` export) while signal is untrusted (inference from structure + LP gaps).

---

## Stage 2 — Signal hardening (still Max Clicks)

| Item | Spec |
|------|------|
| Bid strategy | Stay on Maximize Clicks |
| Work | Negatives from search terms · pause junk KW · gate experiment · spam layers · exclude legacy conversion actions |
| CRM | Weekly accept/reject; compute contamination % |
| Exit criteria | Employer lead accept rate known · contamination trending down · no double-counting · CallRail qualified definition agreed |

---

## Stage 3 — Maximize Conversions (or tCPA)

| Item | Spec |
|------|------|
| Bid strategy | **Maximize Conversions** — optional tCPA once CPA band known from Stage 1–2 actuals |
| Primary conversions | `employer_lead_form` + `employer_lead_call` (qualified) only |
| Still excluded | jobseeker · micro form_start · legacy agency actions · page views |
| Guardrails | CPC/day budget caps; watch search-term quality weekly |
| Exit criteria | Stable CPA for 3–4 weeks · ≥30 primary conv / month / market preferred (if lower, stay longer on Max Clicks) |

**Do not** enable Max Conv the same day tracking is created.

---

## Stage 4 — Value bidding

| Item | Spec |
|------|------|
| Bid strategy | Maximize conversion value / tROAS |
| Values | `zoho_qualified_lead` · `zoho_opportunity` · `zoho_customer` (or placement) with agreed $ |
| Requirements | Offline conversion import with GCLID · &lt;24–48h latency preferred · values approved by Braden |
| Not before | Qualified loop has run ≥1 full month with clean joins |

---

## Forbidden until explicitly reopened

- Broad match + smart bidding combo  
- PMax / Demand Gen “for learning”  
- Sharing budgets across Brand + junk legacy campaigns  
- Optimizing to Calendly starts without employer validation  

---

## Owner cadence

| Cadence | Who | Action |
|---------|-----|--------|
| Daily (first 14d) | George | Search terms + CPC |
| Weekly | Braden + George | Lead QA scorecard |
| Stage gate meeting | Both | Sign Stage 1→2→3→4 in writing (Slack OK) |
