# Virtual Coworker trust-first design system

Preview only. Uses real VC brand tokens. Does not restyle live `/us`.

## Reuse

- Next.js app in `vision/` (not Astro)
- Poppins + Century Gothic Paneuropean
- Navy `#214873`, ink `#1c2430`, paper `#f6f7f9`, gold reserved and not used as a floating CTA
- `/brand/logo-vc.png`
- `SITE`, `TRUST_PROOF`, `PUBLIC_QUOTES`, `CLIENT_MARKS`, `COMPANY_IDENTITY`
- `validateEmployerLead`, `validateUsPhone`, `formatPhoneInput`
- PH careers exit `https://virtualcoworker.com.ph`
- Event names reserved for a later approved split: `employer_inquiry_submitted`, `phone_cta_clicked`, `form_start`, `lp_view`

## New presentation layer

- Light company page instead of the live dark navy PPC shell
- Isolated routes under `/preview/trust-first`
- Config-driven template (`vision/config/trust-first.ts`)
- Preview form POST `/api/lead-preview` (no Zoho, no email)
- Preview toolbar only inside the preview namespace

## Look

White background. Dark readable text. Normal header. Logo a little larger (42px). Phone present, not the whole page. 6px radius. Borders instead of shadows. One primary navy button. No gradients, no quizzes, no popups, no chat on the form, no AI portraits, no raw DKI.

## Live pages inspected (not replaced)

`/us`, `/us/staffing`, `/us/bookkeeping`, `/us/customer-service`, `/us/sales`, `/us/administrative-support`, `/us/digital-marketing`, `/us/real-estate`. Current production stays on `StaffingBaselineLanding` + `GuidedMatchGate`.
