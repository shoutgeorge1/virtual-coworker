# Launch sheet — Stage 1 v6 (Paused package)

**Status:** Local package ready for review · **Not** launch-ready  
**CSV:** `ads-launch/google-ads-editor-import.csv`  
**LP:** vision microsite category routes · `lp_version=stage1-v6`  
**Architecture:** **2 campaigns × 2 markets** (Brand deferred)

---

## Quick facts

| Item | Value |
|------|-------|
| Campaigns | **4** (Paused) — `VC_{US\|AU}_S_CORE` + `VC_{US\|AU}_S_ROLES` |
| Ad groups | 40 |
| Keywords (positive) | 1568 Exact+Phrase |
| RSAs | 78 (full 15/4 — no blanks) |
| Unique negatives | 191 (×4 campaign rows) |
| Final URLs | `/us\|au/{category}` only (no Brand generics in this package) |
| US phone | 310-730-9126 (env override OK) |
| AU phone | None — form primary (locked) |
| Careers URL | `/ph` via `NEXT_PUBLIC_CAREERS_URL` (locked for Stage 1) |
| Lead QA | `ALLOW_LOG_ONLY_LEADS=true` — TEMPORARY logs only; Zoho access ≠ integration |
| Editor Account col | USA `496-715-1855` · AU `573-539-1940` stamped on every CSV row |
| Budgets / CPC | Core $75 / Roles $50 (US) · Core A$75 / Roles A$50 (AU) · Max CPC $8 / A$6 — see `DECISIONS.md` |
| Monthly pace | ≈ $3.8k US + A$3.8k AU at these dailies — inside $10–20k/account story |

---

## Before any enable

- [ ] Lead delivery configured (**not** log-only)  
- [x] Careers URL decided (`/ph` — Stage 1 default)  
- [x] AU phone decision (form-primary)  
- [x] Budgets + Max CPC filled (2-campaign defaults; George can change)  
- [x] Architecture locked (2/account; Brand deferred)  
- [ ] GTM maps `employer_inquiry_submitted` carefully  
- [ ] Human review matrix (`09`) signed off  
- [ ] Explicit George approval to enable  

---

## Enable order (after gates green)

**Source of truth:** [`PHASED-ACTIVATION.md`](./PHASED-ACTIVATION.md)

1. US — **PH / Filipino / offshore long-tail** Exact (+ tight Phrase) in Core **and** Roles (incl. bookkeeping/accounting when PH-shaped)  
2. US — broader category Exact/Phrase without PH geo  
3. US — generic Core head terms later (tighter CPC once CTR known)  
4. AU — same pattern after US looks sane (form-primary)  

Never: Broad, PMax, DSA, WP spray, fake Zoho success, Brand until explicitly added. Do **not** hold PH books just because “Controlled.”
