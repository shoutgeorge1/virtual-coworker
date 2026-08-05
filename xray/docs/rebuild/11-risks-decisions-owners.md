# 11 — Risks, open decisions, named owners

---

## A. Open decisions (George / Braden)

| ID | Decision | Options | Needed before |
|----|----------|---------|---------------|
| D1 | Canonical paid LP host | Microsite (A) vs fix `try.*` (B) | Campaign Final URLs |
| D2 | Pause all legacy campaigns at launch? | Pause museum vs leave brand remnant | Go-live |
| D3 | AU path slug | `/au` vs keep `/apac` | LP + ads |
| D4 | Day-one KW: include bare `[virtual assistant]`? | Include with heavy negatives vs defer | Core launch |
| D5 | CallRail activate at Stage 1 or form-only first week? | Both vs form-first | Tracking |
| D6 | Zoho at launch vs email interim | Contract + creds vs email | Lead ops |
| D7 | Budgets US/AU daily | Numbers from Braden/George | Enable campaigns |
| D8 | Claims approval | “14 years”, white-glove, pricing | RSA/LP copy |
| D9 | Freemail block on form? | Block gmail/yahoo vs allow | Form build |
| D10 | Gate experiment start | Baseline-only 2 weeks vs immediate 3-way | Traffic |

---

## B. Data / access still required from VC

| Need | From | Blocking? |
|------|------|-----------|
| MCC Admin Accept | Braden — **done** | Verify Admin in-account still useful |
| Performance CSV pack (see `01-…`) | Braden/George post-Accept | No for blueprint; **Yes** for CPC guardrail + legacy conv audit |
| Spend owner + budgets | Braden | **Yes** to enable |
| Lead emails US/AU | Braden | **Yes** |
| Forward DIDs + CallRail seat | Braden | For call conv |
| Zoho API/webhook + field confirm | VC IT / Braden | For CRM push |
| Qualified lead definition | Braden | For Stage 2–3 |
| Privacy/recording consent stance | Braden | CallRail |

---

## C. Risks

| Risk | Severity | Mitigation | Owner |
|------|----------|------------|-------|
| Max Conv on untrusted legacy actions still spending | High | Pause museum / exclude actions before enable | George |
| Job-seeker contamination poisons Stage 3 bidding | High | Gate + negatives + never Ads-convert job path | George + Braden |
| WP sitelink spray returns | High | LP-only assets; checklist gate | George |
| try.* thank-you 404 / Formspree opacity | High | Prefer microsite or fix TY before spend | George |
| Double-counting form + Calendly + call | Med | One primary per session rule | George |
| Mega negative lists block good queries | Med | Curated shared lists only | George |
| Low Exact volume panic → Broad/PMax | High | Ladder forbids; document in dashboard | George |
| No performance history → wrong CPC limit | Med | Omit CPC cap until exports | George |
| Zoho spam leads | High | Employer_Confirmed gate + spam status | George + Braden |
| MCC / API quota burns | Med | Editor + UI only; no exploratory API | George |

---

## D. Named owners (RACI-lite)

| Workstream | Accountable | Does the work | Consulted |
|------------|-------------|---------------|-----------|
| Ads architecture & Editor build | George | George | Braden |
| LP / gate / tags | George | George | Braden (copy) |
| Lead quality loop | Braden | Braden’s team | George |
| Budgets / spend | Braden | Braden | George |
| Zoho contract | Braden | VC IT + George | — |
| CallRail | Braden (seat) | George (swap) | — |
| Stage gate approvals | Both | George proposes | Braden signs |
| Dashboard Clean Rebuild updates | George | George | — |

---

## E. First launch sequence (exact)

1. Verify Admin in-account (MCC Accept done)  
2. Pull performance export pack → `audit-data/performance/`  
3. Lock D1 (LP) + D7 (budgets) + qualified-lead definition  
4. Ship LP + thank-you + Baseline gate + observe-only conversions  
5. Build paused v1 campaigns in Editor/UI  
6. Pause/isolate legacy museum (D2)  
7. Tag Assistant + hire/job path tests  
8. Enable **US Brand** → 48h → **US Core** → roles → AU  
9. Stage 1 Max Clicks until ladder exit  

**This package stops before step 4 execution mutations.**
