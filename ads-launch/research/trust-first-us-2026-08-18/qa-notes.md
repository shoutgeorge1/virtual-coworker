# Visual QA notes

Preview family QA. Not a production sign-off.

## What was checked

- Isolated namespace `/preview/trust-first`
- Simple and proof-heavy share H1 / URL / intent
- Toolbar only on preview paths
- No MarketGtm on preview layout
- Form posts to `/api/lead-preview`
- Live `/us` files were not rewritten
- AU / PH pages not touched
- Screenshots (32): `vision/public/preview/trust-first/screenshots/` and a copy at `ads-launch/research/trust-first-us-2026-08-18/screenshots/`
  - Index: `index-desktop.png`, `index-mobile.png`
  - Each page: `{slug}-desktop.png`, `{slug}-mobile.png`
  - Proof-heavy desktop: `{slug}-proof-desktop.png`

## Known limits

- Screenshot gallery fills after local capture. Index links expect `{slug}-desktop.png` and `{slug}-mobile.png`.
- Preview assignment is toolbar-only (`TRUST_FIRST_SPLIT_LIVE = false`).
- No Vercel production deploy from this work.
- Live dark `/us` baseline is unchanged, so this challenger will look “more boring” on purpose.

## PREVIEW ONLY — NOTHING LAUNCHED
