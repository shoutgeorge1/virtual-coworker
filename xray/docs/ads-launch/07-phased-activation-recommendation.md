# 07 — Phased activation recommendation

**Source of truth:** [`PHASED-ACTIVATION.md`](./PHASED-ACTIVATION.md)  
**Do not enable anything until blockers in `12-blocker-decision-list.md` are cleared.**  
All CSV entities ship **Paused**. Brand is **deferred** (not in package).

---

## Locked priority (George 2026-08-05)

1. **Long-tail high intent first** — especially **Philippine / Philippines / Filipino** + role/hire language.  
2. **Generic Core head terms later** (bare “virtual assistant”, hire-a-VA without geo).  
3. Early learning goal = impressions / clicks / CTR; don’t thin-spread chaos — phase by **intent quality**.  
4. Bookkeeping / accounting with strong PH long-tail = **Phase 1**, not automatically held.

### Wrong → right

| Wrong | Right |
|-------|-------|
| Core first, then Digital · Social · Admin; hold books/CS/HR/sales | **Phase 1:** PH/Filipino/offshore long-tail Exact (+ tight Phrase) across Core **and** Roles AGs that carry that intent |
| Hold accounting/books because “lower volume” | Prioritize by **query shape**; PH books/accounting can enable with Phase 1 |

---

## Activation phases (summary)

| Phase | Enable | Hold |
|-------|--------|------|
| **0** | Ops: durable leads, LP QA, budgets, explicit George approval | Any Ads enable |
| **1** | PH / Filipino / offshore long-tail Exact (+ tight Phrase) in Core + Roles (incl. books/accounting when PH-shaped) | Bare Core heads; Broad |
| **2** | Broader category Exact/Phrase **without** PH geo | Generic Core heads |
| **3 / later** | Generic Core heads with tighter CPC/budget once CTR/quality known | Brand, Broad, PMax, DSA, WP |

US first → AU after US looks sane (AU form-primary).

---

## Phase 0 — Local / ops readiness (now)

1. George reviews LP routes + A/B + gate on vision preview.  
2. Set lead delivery (email/webhook) — **not** log-only for paid.  
3. US phone + AU form-primary locked (`DECISIONS.md`).  
4. Careers exit locked to `/ph` (never WP).  
5. Budget + Max CPC defaults filled in CSV (Core/Roles) — revise if needed.  
6. Confirm paid host / custom domains (swap Final URL host; keep paths).

## Phase 1 — Soft import (still Paused)

1. Import Editor CSV (split US/AU or import then delete other market).  
2. Confirm networks/geo/Final URLs — **Core = market home**, Roles = category.  
3. Spot-check RSA uniqueness + no consult language.  
4. Leave **Paused**.

## Phase 2 — Enable PH long-tail first (one market first)

**Recommend US first.** When George explicitly approves enable — **still after real lead delivery**:

| Enable | Why |
|--------|-----|
| PH / Filipino / offshore Exact (+ tight Phrase) in `VC_US_S_CORE` | High-intent geo+hire ST density → `/us` |
| Same intent shape in `VC_US_S_ROLES` AGs (Digital · Social · Admin · **Bookkeeping · Accounting** · others with PH long-tail) | Role + PH queries → matching category LPs |

Watch 7–14 days: search terms, CTR, inquiry quality (human), CPA vs inquiry — **not** vs fake job-order ROI.

## Phase 3 — Broader category, then generic Core

1. Broader category Exact/Phrase without PH geo.  
2. Later: generic Core head terms with tighter CPC/budget.  
3. AU Core/Roles same pattern after US diagnostics look sane — still form-primary unless AU phone decided.

## Phase 4 — Never in Stage 1

- PMax / DSA / Broad positives  
- Competitor conquest farms  
- WP homepage/services Final URLs  
- Re-enabling historical catch-all museum campaigns without explicit decision  
- Treating phone clicks as qualified calls before CallRail + human QA  
- Brand Search until explicitly scoped and added  
- Treating log-only form accepts as paid conversions  

---

## Bidding note

Stay on Maximize Clicks with CPC cap until inquiry quality is trusted. Do not jump to Maximize Conversions on unverified conversion definitions.

---

## Evidence pointer

Real PH long-tail examples (incl. bookkeeping): see [`PHASED-ACTIVATION.md`](./PHASED-ACTIVATION.md). Source: `audit-data/performance/search_terms_usa_*.csv`.
