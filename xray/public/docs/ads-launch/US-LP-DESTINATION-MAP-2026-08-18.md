# US landing destinations (not live until measurement is verified)

Do not change Google Ads Final URLs until `/us` events are confirmed in GA4 DebugView and a candidate URL is inspected on desktop and mobile.

| Ad group / intent | Intended path | Status 18 Aug 2026 |
| --- | --- | --- |
| `Hire_VA_PH` | `/us` current dedicated Filipino-staff baseline | Live Final URL |
| `Offshore_VA_PH`, `VA_Agency_Firm_PH`, `Brand_VC` | `/us` baseline | Live Final URL. Brand deferred. |
| `Staffing_Agency_PH`, `Agency_PH` | `/us/staffing` staffing-oriented candidate | **Candidate only.** Deployed noindex. Not an Ads destination. |
| Role `*_Hire_PH` / `*_Outsource_PH` | Existing role routes (`/us/bookkeeping`, `/us/customer-service`, …) | Live Final URLs. Do not merge onto `/us`. |
| Real-estate (when launched) | `/us/real-estate` | Page exists. Do not point ads until measurement works. |

Inspect candidate: https://www.virtualcoworker.app/us/staffing  
Baseline: https://www.virtualcoworker.app/us
