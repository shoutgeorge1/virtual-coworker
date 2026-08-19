# Social / Marketing VA expansion — research first

**19 August 2026. PREVIEW + PAUSED EDITOR ONLY. Nothing launched.**

No Keyword Planner / Ads API in this environment. No Ads mutations. Existing `VC_US_S_*` campaigns, live `/us` pages, and conversion tags were not rewritten.

## Which concepts deserve their own ad group and landing page?

| Concept | Decision | Why |
| --- | --- | --- |
| Social Media Virtual Assistant | **LAUNCH NOW** | Account keepers + USA ST + existing `/us/social-media` + ~1,300 global SEO volume. Tight VA language, not a new URL. |
| Digital Marketing Virtual Assistant | **LAUNCH NOW** | Stronger keeper terms than Social on some queries (`virtual marketing assistant` 84 clicks / 6 conv). Live `/us/digital-marketing` already exists. Soft GA4 engagement — fix the page, do not invent a second URL. |
| Instagram VA | **DO NOT LAUNCH YET** | No keeper ST. Only two paused PH keywords. No public volume in the VA keyword set. |
| LinkedIn VA / LinkedIn Lead Gen VA | **DO NOT LAUNCH YET** | No LinkedIn ST. `lead generation virtual assistant` (11 clicks / 5.3 conv, ~320 global) is sales/lead-gen, not LinkedIn. Do not mix it into a LinkedIn page. |
| Facebook / Meta VA | **DO NOT LAUNCH YET** | No ST, no volume evidence. |
| TikTok VA / TikTok Shop VA | **DO NOT LAUNCH YET** | Zero evidence. Shop/operator intent is noted only. |
| YouTube VA | **DO NOT LAUNCH YET** | Zero evidence. |
| Pinterest VA | **DO NOT LAUNCH YET** | Zero evidence. High training/job-seeker risk if ever tested. |

**Do not give every platform its own group.** Volume and account evidence only support two first-wave groups.

## 1. Keyword demand

Official US Keyword Planner fields (US volume, 3-month, YoY, competition, top-of-page bids) are **blocked**. Third-party **global** volumes from [SEOpital](https://www.seopital.co/blog/the-best-virtual-assistant-seo-keywords) plus this account’s search terms.

| Keyword | Global vol (3rd party) | Account clicks / conv / cost | Intent | Match | Group |
| --- | --- | --- | --- | --- | --- |
| virtual marketing assistant | 1,600 | 84 / 6.0 / $2,152 | Employer hire | Exact + Phrase | Digital_Marketing_VA_PH |
| social media virtual assistant | 1,300 | 49 / 3.2 / $1,346 | Employer hire | Exact + Phrase | Social_Media_VA_PH |
| digital marketing virtual assistant | 880 | 13 / 1.0 / $437 | Employer hire | Exact + Phrase | Digital_Marketing_VA_PH |
| marketing virtual assistant | — | 35 / 4.5 / $1,192 | Employer hire | Exact + Phrase | Digital_Marketing_VA_PH |
| marketing va | — | 18 / 2.0 / $639 | Employer, short | Exact | Digital_Marketing_VA_PH |
| social media va | — | 28 / 1.0 / $1,002 | Mixed | Exact + Phrase | Social_Media_VA_PH |
| virtual social media assistant | — | 28 / 4.0 / $806 | Employer hire | Exact + Phrase | Social_Media_VA_PH |
| social media assistant | — | 73 / 1.0 / $1,089 | Ambiguous | Do not Phrase | none |
| social media marketing virtual assistant | 140 | none | Thin employer | Exact only | inside Social |
| lead generation virtual assistant | 320 | 11 / 5.3 / $331 | Employer, not LinkedIn | leave with Sales | none here |
| instagram / linkedin / facebook / tiktok / youtube / pinterest VA | not listed | none in keepers | Unknown / thin | none | none |
| become a virtual assistant | 4,400 | — | Job-seeker | Campaign negative | — |

Full table: `keyword-demand.json`.

## 2. Existing-account evidence

USA ST (~2024-08-01 to 2026-08-04), keepers, GA4 10–16 Aug 2026.

**Qualified-looking employer queries (conversions ≠ Zoho quality):**

| Term | USA clicks | USA cost | USA conv | Class |
| --- | --- | --- | --- | --- |
| social media manager philippines | 44 | $1,155 | 3.0 | employer keep |
| filipino social media manager | 17 | $547 | 1.0 | employer keep |
| social media manager for hire | 14 | $335 | 1.0 | employer keep |
| hire a social media manager | 7 | $326 | 1.0 | employer keep |
| digital marketing philippines | 10 | $410 | 1.0 | employer keep |

Those PH **manager** terms already live in paused `Social_Media_Hire_PH` / `Digital_Marketing_Hire_PH`. This expansion does **not** copy them. New groups are the tighter **VA** language only.

**Job-seeker / junk already seen:**

- `social media virtual assistant jobs` (2 clicks, 1 Ads conv — do not treat as a good lead)
- `work from home social media manager` (already on `VC_Neg_JobSeekers_Live`)
- `upwork social media manager`

**GA4 role LPs (7 days, soft):**

- `/us/digital-marketing` — 17 sessions, 23.5% engaged
- `/us/social-media` — 15 sessions, 33.3% engaged

Page quality is the constraint, not missing platform URLs.

**Zoho:** no fresh lead-quality pull in this run. Do not count Ads conversions as employers.

**Winning paths to leave alone:** `VC_US_S_CORE`, live `/us`, existing role LPs, existing Social/Digital Hire and Outsource groups, Brand.

## 3. Recommended ad groups

First wave only:

1. `Social_Media_VA_PH` → Final URL `https://www.virtualcoworker.app/us/social-media`
2. `Digital_Marketing_VA_PH` → Final URL `https://www.virtualcoworker.app/us/digital-marketing`

Both sit under existing `VC_US_S_ROLES`. **Paused.** Do not enable them on the same terms as `Social_Media_Hire_PH` / `Digital_Marketing_Hire_PH`.

No Instagram, LinkedIn, Facebook, TikTok, YouTube, or Pinterest groups.

## 4. Exact / Phrase lists

**Social_Media_VA_PH**

Exact: social media virtual assistant · hire social media virtual assistant · social media va · hire social media va · virtual assistant for social media · social media management virtual assistant · virtual social media assistant · virtual assistant social media · social media manager virtual assistant · social media marketing virtual assistant · va for social media · virtual social media manager

Phrase: social media virtual assistant · hire social media virtual assistant · social media va · virtual social media assistant · social media management virtual assistant

**Digital_Marketing_VA_PH**

Exact: digital marketing virtual assistant · marketing virtual assistant · virtual marketing assistant · hire marketing virtual assistant · marketing va · virtual assistant for digital marketing · digital marketing va · virtual assistant digital marketing · marketing virtual assistants · hire digital marketing va · remote marketing assistant

Phrase: digital marketing virtual assistant · marketing virtual assistant · virtual marketing assistant · hire marketing virtual assistant · digital marketing va

No Broad. `social media assistant` and `remote marketing assistant` Phrase were left out (mixed intent).

## 5. Negatives

Audited Job Seekers / Competitors / Sniper and the Stage 1 `VC_US_S_ROLES` campaign list. Already present: job, jobs, salary, course, training, certification, how to become, upwork, fiverr, resume, work from home, indeed, linkedin jobs, job description.

**Do not add** `remote` or `work`.

**Add only** (campaign negative, ROLES):

- interview questions
- become a virtual assistant
- become a social media va
- become a social media manager
- social media interview questions
- social media va salary
- pinterest va jobs
- instagram va jobs
- tiktok va jobs
- youtube va jobs

## 6. RSA

One RSA per new group. No DKI. 15 / 4. Built from existing Social/Digital RSA language (staffing, interview, dedicated seat) without cloning platform-stuffed headlines.

See `google-ads-editor-social-marketing-va-us.csv`.

## 7. URLs + H1s

| Group | Live URL (unchanged) | Preview challenger | H1 |
| --- | --- | --- | --- |
| Social Media VA | `/us/social-media` | `/preview/trust-first/social-media` | Hire a Social Media Virtual Assistant From the Philippines |
| Digital Marketing VA | `/us/digital-marketing` | `/preview/trust-first/digital-marketing` | Hire a Digital Marketing Virtual Assistant From the Philippines |

`/us/social-media-virtual-assistant` and `/us/digital-marketing-virtual-assistant` were **not** created. That would split URLs that already have Ads + GA4 history. Same model as the Real Estate challenger.

Platform URLs were **not** built.

## 8. Pages created / modified

- **NEW (preview only):** `vision/config/trust-first.ts` social-media page
- **MODIFIED (preview only):** digital-marketing H1 / tasks / title
- **UNCHANGED:** live `/us/*`, `/au/*`, GTM, Ads conversion tags, Zoho, existing Editor imports

## 9. Google Ads changes created

- **NEW file:** `ads-launch/google-ads-editor-social-marketing-va-us.csv` (Paused add-on)
- **UNCHANGED:** `google-ads-editor-import-us.csv` and all live campaigns

Import is local draft only. Post still leaves rows Paused. George enable is a separate step.

## 10. Tracking / QA

Preview stays noindex, no MarketGtm, form → `/api/lead-preview`. Live `employer_inquiry_submitted` / `phone_cta_clicked` / thank-you / gclid / UTMs were not touched.

Desktop/mobile H1 wrap: `.tf-h1` uses `clamp` + `22ch` + `overflow-wrap`. Long H1s wrap; they are not stuffed into one line.

## 11. Blocked by permissions

- Google Ads Keyword Planner / Ads API: no credentials. Editor CSV only.
- Gmail MCP: needsAuth. Used the pasted brief.
- Zoho quality: no pull this run.
- Live `/us` swap: not done.

## Launch status (repeat)

1. **Social Media VA — LAUNCH NOW** (Paused import + preview page; enable only after George says so)
2. **Digital Marketing VA — LAUNCH NOW** (same)
3. **Instagram / LinkedIn / Facebook / TikTok / TikTok Shop / YouTube / Pinterest — DO NOT LAUNCH YET**
