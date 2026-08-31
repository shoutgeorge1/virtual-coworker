# Virtual Coworker — Pilot microsite

Independent Next.js destinations for the **Google Search pilot** (US + Australia employers).

Not a WordPress replacement. Not an SEO site. Phase 1 only.

## Routes in pilot scope

| Path | Purpose |
|------|---------|
| `/us` | US employer landing page (restored live baseline) |
| `/us/tf/hire` | Trust-first hire test only — not live CORE ads |
| `/us/philippines-virtual-assistants` | Trust-first PH VA test (new URL) |
| `/us/tf/real-estate` | Trust-first real-estate test |
| `/us/tf/bookkeeping` | Trust-first bookkeeping test |
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
npm run test
npm run build
```

## Stage 1 events (dataLayer)

| Event | Alias | Role |
|-------|-------|------|
| `employer_inquiry_submitted` | `form_submit_success` | Durable form delivery — **funnel only**, not Ads bidding Primary |
| `phone_cta_clicked` | `phone_click` | Phone CTA click — not a qualified call |
| `calendly_cta_clicked` | `calendly_click` | Book CTA — secondary / separate |
| `employer_form_started` | — | Funnel |
| `job_seeker_redirected` | — | Never Ads conversion |
| `spam_or_applicant_rejected` | — | Diagnostic |

**Ads steering:** duration-qualified phone calls (Ads UI Calls from ads / website, ~60s+) + Zoho **Qualified lead** offline import. Paste `NEXT_PUBLIC_GTM_US` / `NEXT_PUBLIC_GA4_US` when containers exist — empty = no GTM load.

Quiz / modal gate variants are **not** implemented (inline baseline only).

## Tracking safety

- `NEXT_PUBLIC_PILOT_NOINDEX` defaults to noindex until launch is approved
- Ads conversions fire only when `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=true` **and** conversion IDs are set (prefer GTM mapping)
- Temporary GTM/GA4 only — not Virtual Coworker’s legacy containers
- Leave GTM/GA4 env empty until real IDs exist — do not invent “live” status

## Lead delivery

See [`../docs/lead-routing.md`](../docs/lead-routing.md). Without `LEAD_EMAIL_*` + provider
(or a webhook), `/api/lead` returns a clear 503 — the UI shows a graceful error and
does **not** fire a primary conversion.

## Deploy

Vercel project root directory: `vision`.

Live concepts: https://vision-three-alpha.vercel.app
