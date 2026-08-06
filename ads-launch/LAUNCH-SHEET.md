# Launch sheet — Stage 1 v5 (Paused package)

**Status:** Local package ready for review · **Not** launch-ready  
**CSV:** `ads-launch/google-ads-editor-import.csv`  
**LP:** vision microsite category routes · `lp_version=stage1-v5`

---

## Quick facts

| Item | Value |
|------|-------|
| Campaigns | 22 (Paused) |
| Ad groups | 46 |
| Keywords (positive) | 1604 Exact+Phrase |
| RSAs | 82 |
| Unique negatives | 191 (×22 campaign rows) |
| Final URLs | `/us\|au` + `/us\|au/{category}` |
| US phone | 310-426-8776 (env override OK) |
| AU phone | None — form primary (locked) |
| Careers URL | `/ph` via `NEXT_PUBLIC_CAREERS_URL` (locked for Stage 1) |
| Lead QA | `ALLOW_LOG_ONLY_LEADS=true` — TEMPORARY logs only; Zoho not live |
| Budgets / CPC | Filled — see `DECISIONS.md` (George-decidable; still Paused) |

---

## Before any enable

- [ ] Lead delivery configured (**not** log-only)  
- [x] Careers URL decided (`/ph` — Stage 1 default)  
- [x] AU phone decision (form-primary)  
- [x] Budgets + Max CPC filled (defaults; George can change)  
- [ ] GTM maps `employer_inquiry_submitted` carefully  
- [ ] Human review matrix (`09`) signed off  
- [ ] Explicit George approval to enable  

---

## Enable order (after gates green)

1. US Brand + Core  
2. US role campaigns (admin/books/social/digital first)  
3. AU mirror (form-primary)  
4. HR / recruitment last  

Never: Broad, PMax, DSA, WP spray, fake Zoho success.
