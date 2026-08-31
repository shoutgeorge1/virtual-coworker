# Emotional RSA add — US · 2026-08-09

**Account:** `496-715-1855` · **Campaigns:** `VC_US_S_CORE` + `VC_US_S_ROLES` only (Brand not in this file).

**What this is:** one new **Paused** RSA per ad group, same Final URL / paths the AG already uses. Add-only. No keywords, no negatives, no campaign rewrite.

| | |
|--|--|
| Ad groups | **24** |
| New RSAs | **24** (1:1, all **Paused**) |
| CSV | `ads-launch/google-ads-editor-rsa-add-emotional-us.csv` |
| Regenerator | `python3 ads-launch/build_rsa_emotional_add_us.py` |

## Pause first (Chrome)

Google allows **3 RSAs per ad group**. Before Import/Post:

1. In each live AG, **pause the worst RSA only** — not winners, not Brand.
2. Leave the two better RSAs running.
3. Then import this file.

`Admin_City_Test` only has **1** RSA in the Editor package — no pause required there unless live already has 3.

## Appointment Setter

`Appointment_Setter_Hire_PH` already has **3 RSAs, all Paused** (semantic Exact add, 2026-08-09 — likely never enabled). This file still adds **one more emotional RSA, Paused**.

- If those 3 are already in the account: pause or remove the weakest setter RSA first so the new one can Post.
- Then enable **whichever setter RSA is better** (emotional vs old semantic). Leave the rest paused.

## LP mapping (reused — no new pages)

| Final URL | AGs |
|-----------|-----|
| `/us` | Hire_VA_PH · Offshore_VA_PH · Staffing_Agency_PH · VA_Agency_Firm_PH · Virtual_Staff_PH |
| `/us/administrative-support` | Administration_EA_PH · Admin_City_Test |
| `/us/digital-marketing` | Digital_Marketing_Hire_PH · Digital_Marketing_Outsource_PH |
| `/us/social-media` | Social_Media_Hire_PH · Social_Media_Outsource_PH |
| `/us/accounting` | Accounting_Hire_PH · Accounting_Outsource_PH |
| `/us/bookkeeping` | Bookkeeping_Hire_PH · Bookkeeping_Outsource_PH |
| `/us/customer-service` | Customer_Service_Hire_PH · Customer_Service_Outsource_PH |
| `/us/hr` | Human_Resources_Hire_PH · Human_Resources_Outsource_PH |
| `/us/recruitment` | Recruitment_Hire_PH · Recruitment_Outsource_PH |
| `/us/sales` | Sales_Hire_PH · Sales_Outsource_PH · Appointment_Setter_Hire_PH |

`~$8` admin rate is **only** on `/us` hub + admin AGs. Not on sales/setter or other role LPs.

Voice matches `/us`: dedicated Filipino teammate, you interview / you pick, we handle payroll, free consult, on your hours.

## Import → Post → Enable

1. Editor → USA account → **Get recent changes**.
2. Pause worst RSA per AG in Chrome (or Editor) first.
3. **Account → Import → From file…** → `google-ads-editor-rsa-add-emotional-us.csv`
4. Preview should show **24 Ad adds only**, all **Paused**, Campaign Status untouched.
5. **Post** (still Paused).
6. **Enable** the new RSA only after you like the preview — do not enable from this CSV.

Campaign Status is blank on purpose so live `VC_US_*` campaigns stay Enabled.
