# Larger Exact keyword / ad group rollout — launch sheet

**SUPERSEDED 18 Aug 2026.** George asked to replace this 189-keyword / 12-group dump. Use **`keyword-rollout-narrow.md`** and **`keyword-rollout-narrow.csv`** (5 existing groups, ~10–20 kws each). Do not import this file.

**Do not import for George. Do not push to Google Ads. No Ads API. Brand deferred.**  
Launch CSV: `keyword-rollout-launch.csv` — every keyword is **Paused**. Campaign/Ad group status is blank on existing groups (live-account-safe). The one new ad group (`Real_Estate_Hire_PH`) is **Paused**.

George Posts/enables in Editor. Import ≠ live.

Evidence: `ads-launch/_rsa_challenger_review.json` (US keywords + search terms), `google-ads-editor-agency-intent-keywords-add.csv`, live `/us` trust-first URLs.

Final URLs in this sheet are the **live** paths on `https://www.virtualcoworker.app`.

## Index / robots (live pages)

Role LPs (`/us/bookkeeping` and the rest of the existing US category set) were already **indexable**. Live trust-first pages follow that same policy so we do not surprise-SEO:

| Path | Index |
| --- | --- |
| `/us` | index (same as previous US paid home) |
| `/us/philippines-virtual-assistants` | index (new; same policy as role LPs) |
| `/us/virtual-assistant-agency` | index (new; same policy as role LPs) |
| `/us/staffing` | index **now** (was noindex unused candidate; now a live paid LP) |
| `/us/real-estate` and other trust-first role URLs | index (unchanged) |
| `/preview/trust-first/*` | noindex (preview index + toolbar only) |

`robots.ts` already disallows `/preview/`.

## Rules used

- Exact first. No Broad. No new Phrase in this CSV.
- No Brand. No generic `virtual assistants` head-term group.
- Existing ad groups expanded in place. One new Paused AG: `Real_Estate_Hire_PH`.
- Job-seeker negatives documented only: `job`, `jobs`, `salary`, `career`, `careers`, `apply`, `application`, `resume`, `work from home`. Do not negative `hire` / `hiring`.

## Counts (this launch CSV)

| | Ad groups | Exact keywords |
| --- | ---: | ---: |
| Existing groups expanded | 11 | — |
| New Paused group | 1 (`Real_Estate_Hire_PH`) | — |
| **Total** | **12** | **189** |

Preview draft was 78 Exact. This sheet is larger Exact from RSA keywords/STs + agency-intent + employer long-tails, still quality-filtered.

## Clusters → live URLs

### 1. Philippines VA — expand `Offshore_VA_PH` + `Virtual_Staff_PH`

- Campaign: `VC_US_S_CORE`
- LP: `https://www.virtualcoworker.app/us/philippines-virtual-assistants`
- Job-seeker risk: medium

### 2. VA agency / firm / company — expand `VA_Agency_Firm_PH`

- LP: `https://www.virtualcoworker.app/us/virtual-assistant-agency`
- Job-seeker risk: low–medium

### 3. Remote staffing / PH outsourcing — expand `Staffing_Agency_PH`, preserve `Agency_PH`

- LP: `https://www.virtualcoworker.app/us/staffing`
- Job-seeker risk: medium (temp bleed)

### 4. Hire VA (long employer phrases) — preserve/expand `Hire_VA_PH`

- LP: `https://www.virtualcoworker.app/us`
- Do not add bare `virtual assistant` / `virtual assistants`.

### 5. Real estate — **new Paused AG** `Real_Estate_Hire_PH`

- Campaign: `VC_US_S_ROLES`
- LP: `https://www.virtualcoworker.app/us/real-estate`
- Status: Paused until George Posts. No Brand group.

### 6. Bookkeeping — expand `Bookkeeping_Hire_PH`

- LP: `https://www.virtualcoworker.app/us/bookkeeping`

### 7. Customer service — expand `Customer_Service_Hire_PH`

- LP: `https://www.virtualcoworker.app/us/customer-service`
- Reject CSR job titles.

### 8. Sales — preserve `Sales_Hire_PH`

- LP: `https://www.virtualcoworker.app/us/sales`
- Do **not** expand `Appointment_Setter_Hire_PH`.

### 9. Admin / EA — expand `Administration_EA_PH`

- LP: `https://www.virtualcoworker.app/us/administrative-support`

### 10. Digital marketing — expand `Digital_Marketing_Hire_PH`

- LP: `https://www.virtualcoworker.app/us/digital-marketing`

## Reject (not in CSV)

| Item | Why |
| --- | --- |
| New `Virtual_Assistants` AG / generic `virtual assistants` | Head term. ST already leaked jobs. |
| `Brand_VC` | Brand deferred. |
| `Appointment_Setter_Hire_PH` expansion | Job bleed. |
| `Recruitment_Hire_PH` | Talent queries. |

## Job-seeker negatives (document only)

`job`, `jobs`, `salary`, `career`, `careers`, `apply`, `application`, `resume`, `work from home`.

Not implemented in this CSV. Not uploaded.

## What George still does

1. Review `keyword-rollout-launch.csv` in Google Ads Editor.
2. Post when he is ready.
3. Enable keywords/ad groups himself. This sheet does not enable anything.
