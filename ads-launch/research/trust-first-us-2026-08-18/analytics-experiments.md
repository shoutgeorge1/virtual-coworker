# Analytics and experiment readiness

## Preview behavior (now)

- No `MarketGtm` on `/preview/trust-first`
- No production `lp_view`, `form_start`, `employer_inquiry_submitted`, or `phone_cta_clicked`
- Hidden fields still collect `gclid`, `gbraid`, `wbraid`, UTMs, match type, landing URL, LP key, variant
- `TRUST_FIRST_SPLIT_LIVE = false`
- Toolbar / `?v=simple|proof` only
- Preview submits return `preview: true` and are logged as `[lead-preview-accept]`

## When George approves a later test

Reuse the existing event names. Stamp `lp_version=trust_first_preview_2026_08_18`, `landing_page_type=trust_first_preview`, `experiment_id=us_trust_first_lp`. Filter those out of Ads primary conversions and the US baseline report until the split is approved.

Do not double-fire `gtag` and dataLayer. Do not count preview visits as `/us` baseline traffic.

Deterministic simple vs proof_heavy assignment is written and disabled.
