# Paid LP CRO V2 production rollout — 16 Aug 2026

Live host: **https://www.virtualcoworker.app**  
No Google Ads, GTM publish, GA4 admin, budget, keyword, or Final URL changes. No Zoho writes. No email sent. No A/B test.

Rollback SHA was recorded **before** this composition ship: `c82e253bd887454463ed28338c8255fcb251a204` (previous production guided-match, `dpl_BhrTHVswjxr96bJELWu5XySVYpRd`).

---

## 1. What changed

One version. Employer pages now follow the CRO Mega Prompt V2 rhythm: sell easy hiring, then the quiz, then name/email/phone.

- First gold button is **See how hiring works** (bookkeeping: **See how bookkeeping hires work**) and jumps to `#gate` / the hiring path, not a vague mid-page scroll
- Quiet hero: headline, difference, since 2011, outcome line, one gold button. Photo as its own beat on a phone; beside the hero on desktop
- Three statements, then 2011 + Google/Clutch stars, one quote, how-hiring-works steps, then guided-match
- Desktop tightens the path (three statements in one row, shorter bands) so the quiz is not under a long magazine. Mobile stays roomy
- Outcome copy: **Tell us who you need. We’ll build your hiring brief.** Specialist reviews recruiting path, timeline, hourly-rate structure
- Job-seeker line stays in the footer only
- Micro dataLayer / GA4 events for role tile, how-it-works step, hiring-path CTA, quiz start. Not `form_start`. Not Ads Primary. GTM not published

`/api/lead`, thank-you overlay (auto-open, × / dim / Esc, Schedule a call, phone, `eligible=0`), GTM containers, and `/us/quiz` `/au/quiz` were left as they were.

## 2. Routes

Same paid employer surfaces as the morning guided-match ship:

- https://www.virtualcoworker.app/us
- https://www.virtualcoworker.app/au
- US + AU role pages (including `/us/bookkeeping`)

Query strings still work: `gclid`, `gbraid`, `wbraid`, `utm_*`, `variant`, `focus=gate`, `#gate`.

**Not replaced:** `/us/quiz`, `/au/quiz`, privacy/terms, `/ph`, WordPress, Ads Editor CSVs.

## 3. Conversion contract (unchanged)

| Check | Result |
|---|---|
| Role tile / hours / See how hiring works ≠ `employer_form_started` | Code + unit tests. Micros are `lp_micro_*` only |
| First PII field → `employer_form_started` + `form_start` once | Same `shouldStartEmployerFormOnPii` helper |
| Validation fail → `employer_form_validation_error` | Unchanged |
| `/api/lead` success required before `employer_inquiry_submitted` | Same `trackValidEmployerSubmit` |
| Phone → `phone_cta_clicked` + `phone_click` | Unchanged |
| Thank-you `?market=&sid=` (+ `category`, `variant`, `eligible=0`) | Unchanged keys |
| Overlay auto-open, dismiss, Schedule a call, phone | Cherry-picked from the overlay ship onto this branch |
| `bidding_primary: false` on form success | Unchanged |
| Payload `lp_surface=form`, `cta_mode=form_primary`, `lp_version=stage1-v9` | Version bump so this composition is visible in analytics |

No production smoke lead was posted.

## 4. Build / tests

On the deploy tree:

- `npx vitest run` — 16 files, 97 tests pass
- `npx tsc --noEmit` — pass
- `npx next build` — pass (Vercel build also pass, 25s)

## 5. Production deployment

- Public: **https://www.virtualcoworker.app**
- Deployment URL: https://vision-lj8ctjs9q-shoutgeorge1s-projects.vercel.app
- Deployment ID: **`dpl_DBLW3Rjom1GjxazeTpFAPQQ9RQJ1`**
- Inspector: https://vercel.com/shoutgeorge1s-projects/vision/DBLW3Rjom1GjxazeTpFAPQQ9RQJ1
- Method: existing `vision/` Vercel CLI production deploy (not xray)

## 6. Git

- Ship SHA: **`2641f2075a0a8829c21f21cbba75c7c418d56a37`**
- Branch: `paid-lp-cro-v2-2026-08-16`
- Overlay included on this branch: `1733264` (cherry-pick of thank-you auto-open)

GitHub remote was not pushed. Live is the Vercel upload of this commit.

## 7. Rollback

- Git: **`c82e253bd887454463ed28338c8255fcb251a204`** (guided-match v1, quiz in the hero)
- Previous Vercel production: **`dpl_BhrTHVswjxr96bJELWu5XySVYpRd`**

Promote that deployment in Vercel, or redeploy that SHA. Do not mutate Ads to roll back.

## 8. Smoke

HTTP 200 on `/us`, `/au`, `/us/bookkeeping`, `/au/customer-service`, `/thank-you?market=us`.

Confirmed:

- US `(888) 964-8644` / AU `1300 886 740` + ABN
- First gold button + other hire CTAs use `href="#gate"`
- Core includes Other / Not sure (chooser still in the quiz, after the sell)
- Bookkeeping skips the role chooser
- No labeled production lead was submitted

Chrome opened to `/us`, `/au`, and `/us/bookkeeping`.

## 9. Timestamp

**2026-08-16T13:40:00Z** (16 Aug 2026, about 6:40 AM Pacific).

## 10. What was not done

- No live IGNORE / shoutgeorge+ lead
- GTM not published; Ads Primary actions not attached to micros
- `/us/quiz` and `/au/quiz` still the older MarketLanding form
- No screenshots captured into this note (look at the live URLs)

Keep Maximize Clicks. Do not change budget, CPC, keywords, or bidding off this ship.
