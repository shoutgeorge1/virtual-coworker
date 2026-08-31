# Conversion QA — replacement mocks (16 Aug 2026)

**Harness:** `ads-launch/mocks/paid-lp-replacements-2026-08-16/qa.html`  
**Rules:** MOCK `/api/lead` only. No Zoho. No Ads mutate. No GTM publish. No production `/us` `/au` change.

Clean customer view: `index.html?preview=1#one-us-core` (Bookkeeping: `#one-us-bookkeeping`). Review chrome: `?review=1`.

## Contract checks (`qa.html`)

| Check | Result |
|---|---|
| Role select → `quiz_step` (+ `quiz_started` / `guided_match_started` once). **Not** `employer_form_started` | PASS |
| Completing hours/seats → `quiz_step_completed` only (not Ads) | PASS |
| Reaching contact step → `quiz_completed` / `contact_step_reached` diagnostic | PASS |
| First name / email / phone → `employer_form_started` + `form_start` once | PASS |
| Further field focus does not double-fire form start | PASS |
| Validation fail → `employer_form_validation_error` | PASS |
| Mock `/api/lead` success → `employer_inquiry_submitted` + `form_submit_success` + `form_submit` | PASS |
| Thank-you `?market=&sid=` (local thank-you.html) | PASS |
| Phone → `phone_cta_clicked` + `phone_click` | PASS |
| `bidding_primary: false` | PASS |
| Honeypot / too-fast / aliases / US+AU phones | PASS |
| Payload `lp_version=stage1-v8`, `lp_surface=form`, existing role/schedule/size enums | PASS |
| No Zoho | PASS |

## Visual / skip (manual)

| Check | Expected |
|---|---|
| Core US clean preview | Role chooser in hero. Spacious photo. Page continues well below the fold |
| Bookkeeping clean preview | **No** “What role are you hiring for?”. Headline is bookkeeping. First question is workload |
| Mobile | No hero overflow; phone and chips remain tappable |

Honest comparison to **2 / 355** still uses `employer_form_started` on contact fields, not role clicks.
