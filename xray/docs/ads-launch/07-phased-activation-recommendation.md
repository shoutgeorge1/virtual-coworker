# 07 — Phased activation recommendation (v6)

**Do not enable anything until blockers in `12-blocker-decision-list.md` are cleared.**  
All CSV entities ship **Paused**. Brand is **deferred** (not in package).

---

## Phase 0 — Local / ops readiness (now)

1. George reviews LP routes + A/B + gate on vision preview (casting approved).  
2. Set lead delivery (email/webhook) — **not** log-only for paid.  
3. US phone + AU form-primary locked (`DECISIONS.md`).  
4. Careers URL locked to `/ph` for Stage 1 (change if better URL confirmed).  
5. Budget + Max CPC defaults filled in CSV (Core/Roles) — revise if needed.  
6. Confirm paid host / custom domain (swap Final URL host; keep category paths).

## Phase 1 — Soft import (still Paused)

1. Import Editor CSV (split US/AU or import then delete other market).  
2. Confirm networks/geo/Final URLs/category paths.  
3. Spot-check RSA uniqueness + no consult language.  
4. Leave **Paused**.

## Phase 2 — Enable Core only (one market first)

**Recommend US first.**

| Enable | Why |
|--------|-----|
| `VC_US_S_CORE` | Highest historical employer ST density (VA / hire / PH-offshore) |

Watch 7–14 days: search terms, inquiry quality (human), CPA vs inquiry — **not** vs fake job-order ROI.

## Phase 3 — Roles expansion (controlled)

Enable `VC_US_S_ROLES` when Core ST quality looks sane. Inside the campaign, watch AG tiers:

1. Digital · Social · Admin first  
2. Bookkeeping · accounting · sales · customer-service  
3. HR · recruitment **last** (thin ST)

AU Core → AU Roles after US diagnostics look sane — still form-primary unless AU phone decided.

## Phase 4 — Never in Stage 1

- PMax / DSA / Broad positives  
- Competitor conquest farms  
- WP homepage/services Final URLs  
- Re-enabling historical catch-all museum campaigns without explicit decision  
- Treating phone clicks as qualified calls before CallRail + human QA  
- Brand Search until explicitly scoped and added  

---

## Bidding note

Stay on Maximize Clicks with CPC cap until inquiry quality is trusted. Do not jump to Maximize Conversions on unverified conversion definitions.
