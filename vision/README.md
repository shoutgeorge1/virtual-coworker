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

## Page composition (all three markets)

Each market hero is a **three-zone PPC layout** at ≥1160px — `copy · the VA · the form`:

- The VA gets her own grid column, so **no card ever lands on a face**. Below
  1160px the zones stack (`copy` / `va` / `form`) and the portrait switches to a
  4:3 crop biased to the upper body.
- Trust badges sit in the copy column, above the fold.
- A benefit band ("what you actually get") sells the offer in four short cards.
- Mobile gets a sticky bottom bar: phone + jump-to-form.

## Imagery rule

**Feature the VA, never the buyer.** Heroes and cards lead with attractive,
professional Filipino virtual assistants — they are what's being sold. Business-owner
stock is deliberately gone. Every crop keeps the head fully in frame with headroom.

## Brand source

Pulled from live Kadence sites (`virtualcoworker.com` / `.com.au` / `.com.ph`):

- Palette: `#214873` navy · `#33DED8` cyan · `#FAC056` gold · `#0071C9` blue · `#F7630C` orange
- Fonts: **Poppins** (body) + **Century Gothic Paneuropean** (display/nav, from their theme)
- Real trust badges: **Clutch** (Top VA Company, US 2026 / Australia), **Google
  5-Star Reviews**, **Forbes Business Council 2026**, plus "placing staff since 2011"
- Real offer facts used in the benefit cards: top 1% of applicants; hourly rates
  from `$7 USD` / `$8 AUD` with the fee inside the rate; recruitment, screening and
  payroll handled; time tracker with daily activity reports and 10-minute screenshots

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
