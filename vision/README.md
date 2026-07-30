# Virtual Coworker — Vision Demo

Interview vision demo: **three sharply different market experiences** for Virtual Coworker, plus a hub to flip between them.

> Frame: “where we could go” — not “replacing WordPress on Monday.”

## Markets

| Path | Audience | Look |
|------|----------|------|
| `/` | Hub | Flip between all three |
| `/us` | US businesses hiring VAs | Steel navy + teal · Syne / Outfit |
| `/au` | AU businesses hiring VAs | Coastal light · Fraunces / Plus Jakarta |
| `/ph` | PH talent / VA careers | Sunrise energy · Unbounded / Sora · EN/TL toggle |

Buyer sites (`/us`, `/au`) gate **hire vs job** on entry. Job seekers are sent to `/ph`. The PH site is talent-only and points buyers to US/AU.

## Local

```bash
cd vision
npm install
npm run dev   # http://localhost:4321
```

Port **4321** on purpose — does not clash with DIME (:3000), CEC (:4350), or the xray static server (:8765).

## Deploy

This folder is a Next.js App Router app. On Vercel, set the project **Root Directory** to `vision`.

```bash
cd vision
npx vercel --yes --prod
```

## Repo

Lives under [`shoutgeorge1/virtual-coworker`](https://github.com/shoutgeorge1/virtual-coworker) in `vision/` so it does not collide with the `xray/` audit package.
