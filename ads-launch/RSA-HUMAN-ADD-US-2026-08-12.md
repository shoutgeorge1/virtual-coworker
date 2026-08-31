# Human RSA add — US ROLES · 2026-08-12

**Account:** `496-715-1855`  
**Campaign:** `VC_US_S_ROLES` only (Brand untouched. CORE skipped.)  
**CSV:** `ads-launch/google-ads-editor-rsa-add-human-us.csv`  
**Regenerator:** `python3 ads-launch/build_rsa_human_add_us.py`

New ads only. All **Paused**. No Ads API. Do **not** also import `google-ads-editor-rsa-add-admin-us.csv` — those two admin ads are already in this file.

**Import order (2026-08-12):** pause old weak RSAs first — see `RSA-HUMAN-PAUSE-ADD-US-2026-08-12.md` and `google-ads-editor-rsa-pause-weak-us.csv`. Then import this add file. Google’s 3-ad cap counts paused ads; remove the paused old rows in Editor before the add will fit.

## What was missing

Local Editor packages already have RSA rows on every CORE + ROLES ad group. The last on-disk live probe (`_us_rsa_probe.json`, before the 2026-08-10 human pass) showed **only `Administration_EA_PH` with 0 enabled RSAs**. We did not call the Ads API to re-count live ads.

George asked for new human copy (no abbreviations, no keyword insertion) after admin was rewritten and the rest of `VC_US_S_ROLES` was left alone. This file fills that gap: **new paused RSAs** for those role groups. Existing ads are not edited.

## New ads (19)

| Campaign | Ad group | Final URL | Sample headlines |
|----------|----------|-----------|------------------|
| `VC_US_S_ROLES` | `Administration_EA_PH` (2 ads) | `/us/administrative-support` | Inbox Eating Your Week? · Hire Executive Assistant · Dedicated Filipino Admin |
| `VC_US_S_ROLES` | `Accounting_Hire_PH` | `/us/accounting` | Month-End Piling Up? · Dedicated Accounting Seat · Filipino Accounting Support |
| `VC_US_S_ROLES` | `Accounting_Outsource_PH` | `/us/accounting` | Outsource Accounting Work · Dedicated Finance Seat · On Your Close Calendar |
| `VC_US_S_ROLES` | `Bookkeeping_Hire_PH` | `/us/bookkeeping` | Invoices Stacking Up? · Dedicated Filipino Bookkeeper · On Your US Hours |
| `VC_US_S_ROLES` | `Bookkeeping_Outsource_PH` | `/us/bookkeeping` | Outsource the Bookkeeping · Dedicated Books Seat · On Your Finance Hours |
| `VC_US_S_ROLES` | `Customer_Service_Hire_PH` | `/us/customer-service` | Customers Waiting Too Long · Dedicated Support Teammate · On Your Support Hours |
| `VC_US_S_ROLES` | `Customer_Service_Outsource_PH` | `/us/customer-service` | Outsource Customer Support · Dedicated Support Seat · On Your Customer Hours |
| `VC_US_S_ROLES` | `Digital_Marketing_Hire_PH` | `/us/digital-marketing` | Your Marketing Is Stalled · Dedicated Filipino Marketer · On Your US Hours |
| `VC_US_S_ROLES` | `Digital_Marketing_Outsource_PH` | `/us/digital-marketing` | Outsource Marketing Work · Dedicated Marketing Seat · On Your Hours Offshore |
| `VC_US_S_ROLES` | `Social_Media_Hire_PH` | `/us/social-media` | Brand Going Quiet? · Dedicated Social Teammate · On Your US Hours |
| `VC_US_S_ROLES` | `Social_Media_Outsource_PH` | `/us/social-media` | Outsource Social Media · Dedicated Social Seat · On Your Brand Hours |
| `VC_US_S_ROLES` | `Human_Resources_Hire_PH` | `/us/hr` | People Admin Stacking Up · Dedicated People Support · On Your US Hours |
| `VC_US_S_ROLES` | `Human_Resources_Outsource_PH` | `/us/hr` | Outsource People Admin · Dedicated People Seat · On Your People Hours |
| `VC_US_S_ROLES` | `Recruitment_Hire_PH` | `/us/recruitment` | Hiring Pipeline Slowing · Dedicated Recruiting Help · On Your US Hours |
| `VC_US_S_ROLES` | `Recruitment_Outsource_PH` | `/us/recruitment` | Outsource Recruiting Work · Dedicated Recruiting Seat · On Your Hiring Hours |
| `VC_US_S_ROLES` | `Sales_Hire_PH` | `/us/sales` | Follow-Ups Keep Slipping · Dedicated Sales Support · On Your Sales Hours |
| `VC_US_S_ROLES` | `Sales_Outsource_PH` | `/us/sales` | Outsource Sales Support · Dedicated Setter Seat · On Your Pipeline Hours |
| `VC_US_S_ROLES` | `Appointment_Setter_Hire_PH` | `/us/sales` | Calendar Still Empty? · Dedicated Filipino Setter · On Your Sales Hours |

Copy rules: no VA / EA / PH / keyword insertion. Spell out virtual assistant, executive assistant, Philippines. CTA is **Book a Free Strategy Call**. `$8` only on the admin page.

## Skipped

| Ad group | Why |
|----------|-----|
| `Hire_VA_PH`, `Offshore_VA_PH`, `Staffing_Agency_PH`, `VA_Agency_Firm_PH`, `Virtual_Staff_PH`, `Agency_PH` | CORE (plus live extra `Agency_PH`). Last probe showed enabled RSAs; some are winners. Not missing ads. |
| `Admin_City_Test` | Geo test group. Already has an RSA. |
| Brand | Deferred. |
| AU | Same Editor picture (every AG already has RSA rows). Not in this file. |

**Uncertainty:** live counts may have moved since the 2026-08-10 probe. Google allows **3 ads per ad group**. Most of these groups are already at 3.

## Import (Paused)

1. Editor → USA account (`496-715-1855`) → **Get recent changes**.
2. For each ad group in the table that already has 3 ads: **remove 1 old paused ad** (the abbreviated / keyword-insertion one). For `Administration_EA_PH`, remove the old paused ads so the **2** new ones fit.
3. **Account → Import → From file…** → `google-ads-editor-rsa-add-human-us.csv`
4. Preview should show **19 Ad adds**, all **Paused**. Campaign status untouched.
5. **Post** (still Paused). Enable only after you like them.

Do not enable from this CSV. Do not import the older admin-only CSV on top of this one.
