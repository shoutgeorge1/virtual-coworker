# Social / Marketing VA expansion — measured rollout

**19 August 2026. Research first. Two preview pages. Two new paused ad groups. Nothing enabled.**

Keyword Planner / Google Ads API: **blocked** (no credentials in this environment; Ads API stays read-only / Editor-only). Demand call is from **existing USA+AU search-term exports** (~2024-08-01 to 2026-08-04), the paused `VC_US_S_ROLES` package, and GA4 10–16 Aug. Conversions in Ads history are **not** Zoho-qualified employers.

## Which concepts deserve their own ad group and landing page?

| Concept | Decision | Why |
| --- | --- | --- |
| **Social Media Virtual Assistant** | **LAUNCH NOW** (paused import only) | Historical clicks and conversions on `social media virtual assistant`, `virtual social media assistant`, `virtual assistant social media`, plus PH SMM hire terms. Live LP `/us/social-media` already exists. |
| **Digital Marketing Virtual Assistant** | **LAUNCH NOW** (paused import only) | `virtual marketing assistant` is the strongest term in this family (84 clicks / 6 conv US+AU). `marketing va` and `digital marketing virtual assistant` also appear. Live LP `/us/digital-marketing` exists. |
| **Instagram Virtual Assistant** | **TEST LIGHTLY** — **no own group or page** | Package already has `instagram manager philippines` / `hire instagram virtual assistant philippines`. No converting ST row in the export. Two Instagram VA keywords are folded into `Social_Media_VA_PH`. |
| **LinkedIn Virtual Assistant** | **DO NOT LAUNCH YET** | No LinkedIn VA search-term evidence. Do not mix into Social. |
| **LinkedIn Lead Generation VA** | **TEST LIGHTLY later** | `lead generation virtual assistant` converted (11 clicks / 5.3 conv) but that belongs with **existing** `Sales_Hire_PH`, not a new LinkedIn group. |
| Facebook / Meta VA | **DO NOT LAUNCH YET** | No ST evidence. Thin, mixed intent. |
| TikTok VA | **DO NOT LAUNCH YET** | No ST evidence. |
| **TikTok Shop VA** | **DO NOT LAUNCH YET** — flag only | Ecommerce/operator intent could be cleaner than generic TikTok VA, but this account has **zero** evidence. Revisit only with Planner volume. |
| YouTube VA | **DO NOT LAUNCH YET** | No ST evidence. Stage1 already Broad-negatives `youtube`. |
| Pinterest VA | **DO NOT LAUNCH YET** | No ST evidence. High training / job-seeker risk. |

**Data overrode the four-group assumption.** Instagram and generic LinkedIn do not earn their own groups or pages yet.

## What was built

| Asset | Status |
| --- | --- |
| Preview `/preview/trust-first/social-media-virtual-assistant` | **NEW** |
| Preview `/preview/trust-first/digital-marketing-virtual-assistant` | **NEW** |
| Live `/us/social-media` and `/us/digital-marketing` | **UNCHANGED** |
| Existing `Social_Media_Hire_PH` / `Digital_Marketing_Hire_PH` / Outsource twins | **UNCHANGED** (still paused) |
| `Social_Media_VA_PH` + `Digital_Marketing_VA_PH` | **NEW**, paused Editor CSV |
| Production `/us/social-media-virtual-assistant` etc. | **Not created** (preview only; Ads would 404) |
| Google Ads account | **No API writes** |

Editor import (USA `496-715-1855` only):

- `ads-launch/google-ads-editor-social-marketing-va-us.csv`
- `ads-launch/google-ads-editor-social-marketing-va-negatives-us.csv` (optional extras)

Import ≠ Post ≠ Enable. No Campaign row. Campaign Status is blank on purpose so Import cannot pause a live `VC_US_S_ROLES`.

## H1 + URL map

| Group | Preview | Proposed prod (later) | Ads Final URL now |
| --- | --- | --- | --- |
| Social_Media_VA_PH | `/preview/trust-first/social-media-virtual-assistant` | `/us/social-media-virtual-assistant` | `https://www.virtualcoworker.app/us/social-media` |
| Digital_Marketing_VA_PH | `/preview/trust-first/digital-marketing-virtual-assistant` | `/us/digital-marketing-virtual-assistant` | `https://www.virtualcoworker.app/us/digital-marketing` |

H1s:

- Hire a Social Media Virtual Assistant From the Philippines
- Hire a Digital Marketing Virtual Assistant From the Philippines

## Tracking / QA

Preview forms post to `/api/lead-preview` (not Zoho). Preview is noindex. Live conversion events (`employer_inquiry_submitted`, `phone_cta_clicked`, thank-you, gclid/UTM) were **not** changed. Do not import preview URLs into Ads.

Existing job-seeker protection stays: Stage1 Broad `jobs` / `course` / `training` / `how to become` / `upwork` / `fiverr`, plus `VC_Neg_JobSeekers_Live` (already includes `work from home social media manager`). Do **not** negative `remote` or `work`.

## Blocked

- Keyword Planner US volume, 3-month trend, YoY, competition, bid ranges: **not retrieved**
- Fresh Ads impressions/clicks by RSA: **not pulled** (quota lock)
- Zoho lead quality for these queries: **not in this repo**
- Gmail MCP: needs auth; email body was already in the prompt
