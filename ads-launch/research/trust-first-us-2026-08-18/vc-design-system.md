# Virtual Coworker trust-first design system

Preview only. Uses real VC brand tokens. Does not restyle live `/us`.

## Reuse

- Next.js app in `vision/` (not Astro)
- Poppins + Century Gothic Paneuropean
- Navy `#214873`, light blue `#0071c9` (`--vc-blue`, H1 sentence 2 + light-surface accents), cream `#f6f3ea`, ink `#1c2430`, paper `#f6f7f9`
- Cyan `#33ded8` only on the dark footer (logo / live `/us` on navy). Not the H1.
- Google stars only: `#fbbc04`. No orange. Gold is not the H1 or CTA.
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

White background. Dark readable text. Logo 42px. Phone present, not the whole page. 6px radius. Borders instead of shadows. Navy primary button. Hero H1: Century Gothic Paneuropean Bold (same as live `/us`), sentence 1 navy, sentence 2 light blue `#0071c9`. Cream check wells, navy checks. Light-blue section ticks. No quizzes, popups, chat on the form, AI portraits, or raw DKI.

## Live pages inspected (not replaced)

`/us`, `/us/staffing`, `/us/bookkeeping`, `/us/customer-service`, `/us/sales`, `/us/administrative-support`, `/us/digital-marketing`, `/us/real-estate`. Current production stays on `StaffingBaselineLanding` + `GuidedMatchGate`.
