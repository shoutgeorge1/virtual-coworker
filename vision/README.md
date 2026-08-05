# Virtual Coworker — Pilot microsite

Independent Next.js destinations for the **Google Search pilot** (US + Australia employers).

Not a WordPress replacement. Not an SEO site. Phase 1 only.

## Routes in pilot scope

| Path | Purpose |
|------|---------|
| `/us` | US employer landing page |
| `/au` | Australian employer landing page |
| `/thank-you` | Form confirmation |
| `/privacy` | Privacy notice |
| `/api/lead` | Lead intake (email / webhook fallback) |

Hub (`/`) and `/ph` remain as earlier concepts; they are not paid Search destinations for this pilot.

## Local

```bash
cd vision
cp ../.env.example .env.local   # fill when ready — never commit secrets
npm install
npm run dev   # http://localhost:4321
```

## Scripts

```bash
npm run typecheck
npm run build
```

## Tracking safety

- `NEXT_PUBLIC_PILOT_NOINDEX` defaults to noindex until launch is approved
- Ads conversions fire only when `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=true` **and** conversion IDs are set
- Temporary GTM/GA4 only — not Virtual Coworker’s legacy containers

## Lead delivery

See [`../docs/lead-routing.md`](../docs/lead-routing.md). Without `LEAD_EMAIL_*` + provider
(or a webhook), `/api/lead` returns a clear 503 — the UI shows a graceful error and
does **not** fire a primary conversion.

## Deploy

Vercel project root directory: `vision`.

Live concepts: https://vision-three-alpha.vercel.app
