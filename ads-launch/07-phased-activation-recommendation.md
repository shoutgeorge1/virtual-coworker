# 07 — Phased activation recommendation (v7)

**Do not enable anything until blockers in `12-blocker-decision-list.md` are cleared.**  
All CSV entities ship **Paused**. Brand is **deferred** (not in package).

---

## Activation subset (recommend first)

When George explicitly approves enable — **still after real lead delivery**:

| Enable first | Why |
|--------------|-----|
| `VC_US_S_CORE` | Highest historical employer ST density → Final URL `/us` |
| Inside `VC_US_S_ROLES`: **Digital · Social · Admin** AGs | Proven role intent + matching category LPs |
| Hold paused longer | Accounting · Bookkeeping · CS · HR · Recruitment · Sales AGs (built, CSV-ready) |
| AU | Same pattern after US diagnostics look sane — Core then Digital/Social/Admin |

Controlled-tier AGs stay **built but paused** until Core + primary Roles quality is trusted.

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

## Phase 2 — Enable Core only (one market first)

**Recommend US first.**

| Enable | Why |
|--------|-----|
| `VC_US_S_CORE` | Highest historical employer ST density (VA / hire / PH-offshore) → `/us` |

Watch 7–14 days: search terms, inquiry quality (human), CPA vs inquiry — **not** vs fake job-order ROI.

## Phase 3 — Roles expansion (controlled)

Enable Digital · Social · Admin AGs in `VC_US_S_ROLES` when Core ST quality looks sane.

Then optionally: Bookkeeping · accounting · sales · customer-service.  
HR · recruitment **last** (thin ST).

AU Core → AU Roles after US diagnostics look sane — still form-primary unless AU phone decided.

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
