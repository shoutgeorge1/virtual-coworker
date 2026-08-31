# Admin RSA rewrite — US · 2026-08-12

**Account:** `496-715-1855`  
**Campaign:** `VC_US_S_ROLES` (this is the campaign, not an ad group)  
**Ad group:** `Administration_EA_PH`  
**CSV:** `ads-launch/google-ads-editor-rsa-add-admin-us.csv`  
**Regenerator:** `python3 ads-launch/build_rsa_admin_rewrite_us.py`

If you have not imported this yet, use the combined ROLES file instead so admin is not imported twice: `ads-launch/google-ads-editor-rsa-add-human-us.csv` (see `RSA-HUMAN-ADD-US-2026-08-12.md`).

George named `VC_US_S_ROLES` as a second ad group. In Editor it is the **campaign** that holds this admin group (plus marketing, books, sales, etc.). This file only rewrites **Administration_EA_PH**, whose old ads used EA / VA / PH and keyword insertion. Other role groups in that campaign are left alone — say the word if those should get the same treatment.

Brand untouched. No Ads API. Ads ship **Paused**.

## Landing page

Both ads go to the live admin role page:

`https://www.virtualcoworker.app/us/administrative-support`

Display paths: `admin/hire` and `assistant/philippines` (no “ea” in the green URL).

## What’s in the two ads

**Ad 1 — executive assistant** (inbox / calendar)

- Inbox Eating Your Week?
- Hire Executive Assistant
- Dedicated Filipino Admin
- Book a Free Strategy Call
- Admin Around $8 an Hour

Inbox eating your week? Hire a dedicated Filipino executive assistant.

**Ad 2 — virtual assistant** (admin support keywords)

- Hire a Virtual Assistant
- Dedicated Filipino Teammate
- Administrative Support Hire
- Still Doing Admin Yourself?
- Book a Free Strategy Call

Still doing the admin yourself? A dedicated Filipino virtual assistant on your hours.

No EA, VA, PH, or keyword insertion in the copy. $8 only because that page already says typical admin around $8 an hour.

## Import (Paused)

Google allows **3 ads per ad group**. This group already has old paused ads.

1. In Editor, open `Administration_EA_PH` and **remove the old paused ads** (the EA / VA / keyword-insertion ones).
2. **Account → Import → From file…** → `google-ads-editor-rsa-add-admin-us.csv`
3. Preview should show **2 Ad adds**, both **Paused**. Campaign status untouched.
4. **Post** (still Paused). Enable only after you like them.

Do not enable from this CSV.
