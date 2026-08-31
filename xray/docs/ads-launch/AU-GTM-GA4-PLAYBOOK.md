# Checklist 15 — Australia website tags (GTM + GA4)

**When:** after the LA drive. Needs your Google login. Nobody else can create these.

**Already done in code:** `/au` loads `NEXT_PUBLIC_GTM_AU` + `NEXT_PUBLIC_GA4_AU` via `MarketGtm`. Empty env = no tags (correct). Do not paste fake IDs.

**Do not reuse:** US `GTM-M92DX9BJ` / `G-2V3V0BS6JW` (property `549075481`) · legacy WP `GTM-KNDLKVW`.

**Stop after this homework.** Ads conversion tags (phone-click, thank-you, website-call) are later — C, D, F, #16.

---

## 1. New GTM container

1. Open [tagmanager.google.com](https://tagmanager.google.com) on the same Google account as US GTM.
2. Open the Virtual Coworker **account** (not the US container).
3. **Create Container** → Web.
4. Name: `VC AU — virtualcoworker.app`.
5. Copy the ID (`GTM-XXXXXXX`). Close the install snippet — do **not** paste it into the website. Vision already loads GTM from env.

---

## 2. New GA4 property (not the US one)

1. Open [analytics.google.com](https://analytics.google.com) → **Admin**.
2. **Create Property** — a new property, not a stream on US `549075481`.
3. Name like `Virtual Coworker AU`. Time zone Australia (Sydney or Melbourne). Currency AUD.
4. Add a **Web** data stream. URL `https://www.virtualcoworker.app`. Stream name like `VC AU web`.
5. Copy the Measurement ID (`G-XXXXXXXX`).

---

## 3. Point GTM at that GA4 (visit tags only)

1. Back in the **new AU** container (check the ID in the header).
2. New tag: **Google Analytics: GA4 Configuration**.
3. Measurement ID = the `G-XXXX` from step 2.
4. Trigger: **All Pages**.
5. **Publish** (so page views can land). Do **not** add Google Ads conversion / call-forwarding tags yet.

---

## 4. Paste on Vercel — project **vision** (not xray)

`NEXT_PUBLIC_*` is baked at build time. Env on **vc-xray** does nothing for the website.

1. [vercel.com](https://vercel.com) → project **vision**.
2. **Settings → Environment Variables**.
3. Add `NEXT_PUBLIC_GTM_AU` = your `GTM-XXXX`. Production.
4. Add `NEXT_PUBLIC_GA4_AU` = your `G-XXXX`. Production.
5. **Deployments → Redeploy** Production (use the existing build, with the new env).

Do not invent IDs. Do not paste US or WP IDs “just to have something.”

---

## Done when

- Vercel **vision** has both keys on Production.
- Production has been redeployed after the paste.
- Checklist **ads33** can be checked.

Then C / D / F / #16 can use this container. Not before.

---

## Status (2026-08-12)

**Live on Production** — Vercel **vision**:
- `NEXT_PUBLIC_GTM_AU` = `GTM-5T6KPVSF`
- `NEXT_PUBLIC_GA4_AU` = `G-7X1K9V2LFE`

Verified: `https://www.virtualcoworker.app/au` HTML includes `GTM-5T6KPVSF` (no US GTM leak). Checklist **ads33** can be checked. Ads conversion tags still wait (C / D / F / #16).
