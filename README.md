# Virtual Coworker — Paid Search Pilot

Compact operating center for a **$3,000 Google Search proof of concept** —
US and Australian employer leads on an independent microsite.

**Objective:** Can Google Search generate qualified US and AU employer leads at an acceptable cost?

WordPress, legacy analytics, and full CRM rebuilds are **not** required to launch.

---

## Open the command center

Local (port **8766**):

```bash
~/Developer/virtual-coworker/xray/serve.sh
open -a "Google Chrome" http://127.0.0.1:8766/
```

Deployed: **https://vc-xray.vercel.app** → opens the **Checklist** (Launch Control).

Landing pages (production): https://www.virtualcoworker.app/us · [/au](https://www.virtualcoworker.app/au) · preview still at vision-three-alpha.vercel.app

---

## Navigation (Stage 1)

| Page | Job |
|------|-----|
| **Checklist** (`/launch-control`) | **THE work list** — numbered do-this-now steps, gates, path markets + GTM |
| LP previews | Microsite URLs |
| Lead Routing | Email/webhook Stage 1 |
| Tracking | Minimal events |
| Archive (collapsed) | Overview, campaign pages, keywords, rebuild docs, later |

Old checklist / overview URLs redirect to `/launch-control`.

---

## Docs

| File | Purpose |
|------|---------|
| [`docs/pilot-scope.md`](./docs/pilot-scope.md) | What is in / out of the $3k pilot |
| [`docs/reduced-onboarding.md`](./docs/reduced-onboarding.md) | Short launch-blocker list |
| [`docs/keyword-strategy.md`](./docs/keyword-strategy.md) | Exact-match employer clusters |
| [`docs/keyword-page-map.md`](./docs/keyword-page-map.md) | Cluster → page · H1/title notes |
| [`docs/negative-keywords.md`](./docs/negative-keywords.md) | Job-seeker starter negatives |
| [`docs/access-requirements.md`](./docs/access-requirements.md) | Same list as reduced onboarding |
| [`docs/lead-routing.md`](./docs/lead-routing.md) | Email-first delivery + fields |
| [`docs/transfer-plan.md`](./docs/transfer-plan.md) | Asset handoff after validation |
| [`.env.example`](./.env.example) | Env placeholders — no secrets |

Status model: [`xray/data/pilot-status.js`](./xray/data/pilot-status.js)  
Market config: [`vision/config/markets.ts`](./vision/config/markets.ts)

---

## Layout

| Path | Purpose |
|------|---------|
| `xray/` | Pilot command center (static HTML) |
| `vision/` | Next.js microsite (US / AU + form API) |
| `docs/` | Pilot docs |
| `raw/` | Cached public HTML (reference) |
| `xray/archive/` | Earlier site-review notes |

---

## Commercial boundary

**PILOT STATUS: READY TO BEGIN UPON PAYMENT AND ACCESS**

- Preliminary concepts already exist
- Further implementation after the $3,000 payment
- Website rebuild, SEO, remarketing, CRM redevelopment = separate scope

---

## Hard rules

| NEVER | NEVER | NEVER |
|-------|-------|-------|
| Submit forms on live VC sites | Log into client systems without access | Invent Ads / CRM numbers |

Placeholders like `[US_LEAD_EMAIL]` stay until Virtual Coworker confirms values.
