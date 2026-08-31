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

## 18 Aug visual notes

- Removed mid-page client logo strip in CompanyProof. Hero logos stay.
- Google badge leads with 5.0 / 39 (West Hollywood). Clutch shows 4.9 + “Rated on Clutch” — no “7 reviews” headline.
- Soft paper/white section alternation + thin rules. No extra card chrome.
- People photos skipped: no approved named CEO/staff/client headshots. Role/va-face assets look like stock or AI LP art.

## 18 Aug default + hero polish

- Default variant is **proof-heavy**. Simple is `?v=simple` only.
- Hero: subtle warm-to-white wash (not a rainbow). Longer two-color H1 (ink + navy phrase). No extra ATF widgets.
- Compare table stays below the fold.
- CTA still white on navy.
- Did not fetch any utm/gclid URL. Clean look: `https://www.myoutdesk.com/lp/google-philippines-virtual-assistants/`
- Keyword ask: see `cannot-scrape-full-keyword-list.md`.

## 18 Aug ATF + compare pass

- CTA: header/form “Book a strategy call” is white on navy (`color` + `-webkit-text-fill-color`). Cause was `.tf a { color: inherit }` beating the button.
- Hero stayed tight after George’s look. No videos, extra CTAs, or chatbot in the ATF.
- Compare table is **below the fold** (after process / roles). Structure from live MyOutDesk PH LP; copy is Virtual Coworker’s.
- Looked at live clean URL `https://www.myoutdesk.com/lp/google-philippines-virtual-assistants/` (no utm). Cached 3-column table also in `cache/lp-google-virtual-assistants.html`.
- Refused to copy: 0.7%, one-week hire, free rematch, MyTimeIn, SOC 2, HIPAA, flat monthly rate, 70%, 8,500 clients.

## Known limits

- Screenshot gallery fills after local capture. Index links expect `{slug}-desktop.png` and `{slug}-mobile.png`.
- Preview assignment is toolbar-only (`TRUST_FIRST_SPLIT_LIVE = false`).
- No Vercel production deploy from this work.
- Live dark `/us` baseline is unchanged, so this challenger will look “more boring” on purpose.

## PREVIEW ONLY — NOTHING LAUNCHED
