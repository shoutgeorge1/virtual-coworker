# Paid LP hours field UX nit — 16 Aug 2026

Live host: **https://www.virtualcoworker.app**  
Baseline: CRO V2 (no A/B, no redesign). No Ads API, GTM publish, Zoho writes, or email.

## What changed

George did not know what to type in “Different hours or time zone? (optional).” Helper/placeholder is now `e.g. 9–5 in my timezone` (same string on US and AU — not US hours copy on AU). One line under the field. Extra space before Continue on desktop.

Role LPs stay independent Final URLs. Core `/us` `/au` keep the role chooser. Role URLs lock the role. No role-to-role nav.

## Button audit (live)

First gold CTA → `#gate`. US `tel:+18889648644`, AU `tel:+611300886740`. How-it-works steps jump to `#gate`. Core role tiles advance the quiz. Continue reaches contact. Privacy/terms in page footer (`/privacy` `/terms` 200). Careers `https://virtualcoworker.com.ph` 200. `/us|au/human-resources` → 308 `/hr`. No production lead posted.

## Deploy

- Public: **https://www.virtualcoworker.app**
- Deployment: **`dpl_3iNcUq1btgGthm84Hnx5iu9WuNKm`**
- Inspector: https://vercel.com/shoutgeorge1s-projects/vision/3iNcUq1btgGthm84Hnx5iu9WuNKm
- Branch: `paid-lp-cro-v2-2026-08-16` (hours nit on top of CRO V2; not committed)

## Chrome this pass

Opened four US role LPs only. Remaining URLs listed in the chat for the next batch.
