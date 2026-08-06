# 11 — QA report

**Date:** 2026-08-05 · Local only · No deploy · No Ads enable

---

## Commands + exact results

| Check | Command | Result |
|-------|---------|--------|
| Typecheck | `cd vision && npm run typecheck` | **PASS** (exit 0) |
| Lint | `npm run lint` (= `tsc --noEmit`) | **PASS** (same as typecheck) |
| Unit tests | `npm test` | **PASS** — 4 files, **25/25** tests |
| Production build | `npm run build` | **PASS** — Next.js 15.5.22; 31 pages; middleware 34.5 kB |
| Editor package builder | `python3 ads-launch/build_stage1_editor_package.py` | **PASS** — QA OK; 6198 rows |
| Historical analyzer | `python3 ads-launch/analyze_historical_performance.py` | **PASS** — JSON written |

### Vitest detail

```
✓ lib/tracking-dedupe.test.ts (1)
✓ lib/lead-delivery.test.ts (5)
✓ lib/ab-variant.test.ts (7)
✓ lib/lead-validation.test.ts (12)
Test Files  4 passed (4)
Tests  25 passed (25)
```

### Build routes confirmed

- `/us`, `/au`
- `/us/[category]` × 9 (SSG)
- `/au/[category]` × 9 (SSG)
- `/us/consult`, `/au/consult` (redirect)
- `/api/lead`, `/thank-you`, `/ph`, `/privacy`

---

## Functional validation (code / build level)

| Item | Result |
|------|--------|
| 9 US + 9 AU category routes | Generated in build |
| Category H1s / titles | From `categories.ts` variants A/B |
| Form preselect | `LeadGate` preselectedRole = category formLabel |
| A/B cookie + `?variant=` | middleware + `resolveLpVariant` |
| Gate employer/job | Retained; events renamed |
| US phone | Defaults to 310-426-8776 when env empty |
| AU phone | Hidden when unset (form primary) |
| CSV all Paused | Campaigns 22, Ads 82, Keywords 1604 — all Paused |
| Final URLs category paths | Yes; `?role=` absent |
| Double UTM | Tracking template `{lpurl}` only |
| Consult language in RSAs | 0 ads contain “consult” |

---

## Not run (by design / blockers)

- Live browser click-through on production host (no deploy this pass)
- Real lead email delivery (recipients unset — API correctly 503 without `ALLOW_LOG_ONLY_LEADS`)
- Google Ads Editor import / enable
- CallRail / Zoho live tests
- Tag Assistant against live GTM

---

## Residual QA risks

1. Careers fallback `/ph` is not a production careers destination.  
2. Badge assets are recognition badges — not quote testimonials.  
3. A/B lift unmeasured until analytics wired.  
4. Human must still replace `[APPROVAL_*]` before any enable.
