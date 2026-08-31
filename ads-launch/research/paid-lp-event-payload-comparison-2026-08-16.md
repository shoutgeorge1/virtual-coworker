# Event / payload comparison — replacements vs current implementation

Mocks live under `ads-launch/mocks/paid-lp-replacements-2026-08-16/`. They **simulate** `/api/lead` locally (labeled MOCK). No Zoho. No production POST.

**Launch draft:** Version One (guided match). Version Two stays in the switcher as backup only.

| Item | Current `/us` `/au` LeadGate | Version One (guided match) | Version Two (proof-first, backup) |
|---|---|---|---|
| First PII interaction | `employer_form_started` + `form_start` once | **Same trigger:** first **name / email / phone** focus on the contact step. Never on a role click | Same, when the later form is focused |
| Guided-match start | — | `quiz_started` + `guided_match_started` (diagnostic, not Ads). Captures “they began” without spoiling the 2/355 form-start comparison | None |
| Role chips | Not on money form | Core: six Stage 1 roles, `quiz_step` `step: "1"`. Role pages skip chooser (Bookkeeping locked in headline) | None |
| Hours / seats | Optional, often hidden | `quiz_step` `step: "2"` on each chip; completing the step → `quiz_step_completed` (GA4 micro-event only) | Empty strings OK |
| Reaching contact step | Form already in hero | `quiz_completed` + `contact_step_reached` + `lead_magnet_completed` — **funnel diagnostic only** | Form further down |
| Validation | `employer_form_validation_error` | Same, same field names | Same |
| Submit | `POST /api/lead` then `employer_inquiry_submitted` + `form_submit_success` + `form_submit` | Same names; **MOCK local `/api/lead`** | Same |
| Thank-you | `/thank-you?market=&sid=` | Local `thank-you.html?market=&sid=` (same query keys). Production route unchanged | Same local dest |
| Phone | `phone_cta_clicked` + `phone_click` | Same | Same |
| Honeypot `website` | Hidden, empty | Same | Same |
| `company_website` | Optional | Optional on contact step | Optional after proof |
| Attribution | sessionStorage `vc_pilot_attribution` | Same merge (UTM + click IDs) | Same |
| `lp_version` | `stage1-v8` | `stage1-v8` | `stage1-v8` |
| `lp_surface` / `cta_mode` / `landing_type` | `form` / `form_primary` / `form_lp` | **Same** (replaces the money LP, not `/us/quiz`) | Same |
| New Ads conversions | — | **None** | **None** |
| Aliases removed | — | **None** | **None** |

## Payload keys Version One maps from quiz → existing schema

| Quiz choice | Lead JSON field | Allowed values |
|---|---|---|
| Staff type | `role` + `category` | formLabels / slugs already in `config/categories.ts`. On Bookkeeping LP: prefilled `Bookkeeping support` / `bookkeeping` |
| Full-time / part-time | `schedule` | `full-time`, `part-time`, `mix` |
| Number of positions | `positions_needed` | `1`, `2-3`, `4-10`, `11+` |
| Company size | `company_size` | `1-10`, `11-50`, `51-200`, `201+` |
| US or AU hours | `message` prefix (`Hours requested: …`) | **No new API field** — market stays the LP market |

Do **not** treat `quiz_started`, `quiz_step`, `quiz_step_completed`, `contact_step_reached`, or `guided_match_started` as Ads conversions. Primary Ads remain thank-you / `employer_inquiry_submitted` after durable accept, plus existing phone mapping.

Version Two may send empty qualification strings, which production already accepts.
