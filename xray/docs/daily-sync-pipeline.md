# Daily dashboard sync pipeline (vc-xray)

Read-only infrastructure. Does not change dashboard HTML/UI.

## Endpoints (Bearer CRON_SECRET)

- `GET|POST /api/cron/daily-sync` — Vercel Cron at 12:30 UTC (`30 12 * * *`)
- `GET|POST /api/sync/manual` — manual test trigger
- `GET /api/sync/status` — last sync, freshness by source, row counts, partial failures

## Window

Each run re-fetches the previous **14 complete UTC calendar days** (yesterday back)
and upserts into Postgres so delayed conversions / attribution changes land.

## Storage

Neon / Vercel Postgres via `DATABASE_URL`. Runtime sync never writes the Vercel filesystem.
Static HTML still bakes into `xray/` and is copied to `public/` at build time only.

## Join order (Zoho ↔ Ads)

1. GCLID (stored as fingerprint join key — raw GCLID never logged)
2. UTM campaign + ad group + keyword
3. Fallback: date + landing page (labeled weak)

## Credentials

See `.env.example`. Set secrets only in Vercel env — never `NEXT_PUBLIC_*`.
