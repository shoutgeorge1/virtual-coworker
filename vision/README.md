# Virtual Coworker — Vision Demo

Interview vision demo: **three market evolutions of the same brand family**, plus a hub to flip between them.

> Frame: “where we could go” — not “replacing WordPress on Monday.”

## Markets

| Path | Audience | Look |
|------|----------|------|
| `/` | Hub | Flip between all three |
| `/us` | US businesses hiring VAs | Dark navy evolution · Poppins + Century Gothic · gold CTAs |
| `/au` | AU businesses hiring VAs | Light coastal evolution · same palette · gold CTAs |
| `/ph` | PH talent / VA careers | Warmer opportunity energy · orange CTAs · EN/TL toggle |

Buyer sites (`/us`, `/au`) gate **hire vs job** on entry. Job seekers are sent to `/ph`. The PH site is talent-only and points buyers to US/AU.

## Brand source

Pulled from live Kadence sites (`virtualcoworker.com` / `.com.au` / `.com.ph`):

- Palette: `#214873` navy · `#33DED8` cyan · `#FAC056` gold · `#0071C9` blue · `#F7630C` orange
- Fonts: **Poppins** (body) + **Century Gothic Paneuropean** (display/nav, from their theme)
- Assets: logo-vc, Clutch badges, how-it-works, role photos, PH talent portraits

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

Live: https://vision-three-alpha.vercel.app

## Repo

Lives under [`shoutgeorge1/virtual-coworker`](https://github.com/shoutgeorge1/virtual-coworker) in `vision/` so it does not collide with the `xray/` audit package.
