# 07 — Phased activation recommendation

**Do not enable anything until blockers in `12-blocker-decision-list.md` are cleared.**  
All CSV entities ship **Paused**.

---

## Phase 0 — Local / ops readiness (now)

1. George reviews LP routes + A/B + gate on local/Vercel preview.  
2. Set lead delivery (email/webhook) — **not** log-only for paid.  
3. Confirm US phone; decide AU phone or stay form-primary.  
4. Set real `NEXT_PUBLIC_CAREERS_URL`.  
5. Replace budget + Max CPC placeholders.  
6. Confirm paid host / custom domain.

## Phase 1 — Soft import (still Paused)

1. Import Editor CSV (split US/AU or import then delete other market).  
2. Confirm networks/geo/Final URLs/category paths.  
3. Spot-check RSA uniqueness + no consult language.  
4. Leave **Paused**.

## Phase 2 — Enable Brand + Core only (one market first)

**Recommend US first.**

| Enable | Why |
|--------|-----|
| `VC_US_S_BRAND` | Known-intent, controllable |
| `VC_US_S_CORE_hire_va` | Highest historical employer ST density |

Watch 7–14 days: search terms, inquiry quality (human), CPA vs inquiry — **not** vs fake job-order ROI.

## Phase 3 — Role expansion (controlled)

Order by evidence + ops capacity:

1. administrative-support (already fed by Core URL)  
2. bookkeeping · social-media · digital-marketing  
3. sales · accounting · customer-service  
4. hr · recruitment **last** (thin ST)

AU mirror after US diagnostics look sane — still form-primary unless AU phone decided.

## Phase 4 — Never in Stage 1

- PMax / DSA / Broad positives  
- Competitor conquest farms  
- WP homepage/services Final URLs  
- Re-enabling historical catch-all museum campaigns without explicit decision  
- Treating phone clicks as qualified calls before CallRail + human QA  

---

## Bidding note

Stay on Maximize Clicks with CPC cap until inquiry quality is trusted. Do not jump to Maximize Conversions on unverified conversion definitions.
