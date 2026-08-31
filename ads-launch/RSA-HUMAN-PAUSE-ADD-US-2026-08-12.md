# Pause weak RSAs + add human RSAs — US ROLES · 2026-08-12

**Account:** `496-715-1855`  
**Campaign:** `VC_US_S_ROLES` only (Brand untouched. CORE skipped.)  
**Pause CSV:** `ads-launch/google-ads-editor-rsa-pause-weak-us.csv`  
**Add CSV:** `ads-launch/google-ads-editor-rsa-add-human-us.csv`  
**Regenerator:** `python3 ads-launch/build_rsa_human_pause_us.py`

No Ads API. New ads stay **Paused**. Do not Enable from these files.

## CTR source

Per-ad CTR from `ads-launch/_us_rsa_probe.json` (`LAST_14_DAYS`, pulled before the 2026-08-10 in-place human updates). Executive creative snapshot (last 7 days, 2026-08-10) matches the same ad ids where it has rows. No live API dump this pass.

Aug 10 rewrites kept the same ad ids, so their probe CTR is the **old** copy. Those rewritten ads are **not** in this pause file. Winners at or above 5% CTR are kept.

## 3-ad cap

Google allows **3 ads per ad group**, and **paused ads still count**. Importing pause then add will not fit until the paused old ads are **removed** in Editor. Pause first so you can see which rows to delete; then add.

Pause rows: **19**. Add rows: **19** (all Paused).

## Ads paused

| Ad group | Headline 1 | Probe CTR | Why |
|----------|------------|-----------|-----|
| `Administration_EA_PH` | Hire Executive Assistant | 4.0% (100 impr / 4 clicks) | CTR below 5% · old EA/VA copy |
| `Administration_EA_PH` | {KeyWord:Hire Virtual EA} | 4.7% (43 impr / 2 clicks) | CTR below 5% · old DKI + EA copy |
| `Accounting_Hire_PH` | Hire Accountant Philippines | 0.0% (2 impr / 0 clicks) | CTR below 5% · old PH abbrev copy |
| `Accounting_Outsource_PH` | Outsource Accounting PH | 0.0% (1 impr / 0 clicks) | CTR below 5% · old PH abbrev copy |
| `Bookkeeping_Hire_PH` | Hire Bookkeeper Philippines | 0.0% (11 impr / 0 clicks) | CTR below 5% · old PH abbrev copy |
| `Bookkeeping_Outsource_PH` | Outsource Bookkeeping PH | 3.1% (32 impr / 1 clicks) | CTR below 5% · old PH abbrev copy |
| `Customer_Service_Hire_PH` | Shortlist Support Agents | 0.0% (1 impr / 0 clicks) | CTR below 5% · old CS/abbrev copy |
| `Customer_Service_Outsource_PH` | Dedicated PH Support Seat | 0.0% (3 impr / 0 clicks) | CTR below 5% · old PH abbrev copy |
| `Digital_Marketing_Hire_PH` | {KeyWord:Hire Marketing VA} | 6.7% (15 impr / 1 clicks) | old copy / make room for human RSAs (above 5%; DKI/VA; 20% winner kept) |
| `Digital_Marketing_Outsource_PH` | Outsource Marketing to PH | 33.3% (3 impr / 1 clicks) | old copy / make room for human RSAs (3 impr noise; old PH; 50% seat kept) |
| `Social_Media_Hire_PH` | Hire Social Media VA | 0.0% (5 impr / 0 clicks) | CTR below 5% · old VA/SMM copy |
| `Social_Media_Outsource_PH` | PH Social Media Team | 5.6% (36 impr / 2 clicks) | old copy / make room for human RSAs (just over 5%; old PH/SMM; 20% winner kept) |
| `Human_Resources_Hire_PH` | Hire Virtual HR Assistant | 0.0% (5 impr / 0 clicks) | CTR below 5% · old HR/VA copy |
| `Human_Resources_Outsource_PH` | Outsource HR Support PH | 0% (0 impr) | CTR below 5% · old PH abbrev copy |
| `Recruitment_Hire_PH` | Hire Recruitment Assistant | 0.0% (6 impr / 0 clicks) | CTR below 5% · old VA/PH copy (18.6% DKI winner kept) |
| `Recruitment_Outsource_PH` | PH Recruiting Outsourcing | 0% (0 impr) | CTR below 5% · old PH abbrev copy |
| `Sales_Hire_PH` | Hire Lead Gen Specialist | 0.0% (14 impr / 0 clicks) | CTR below 5% · old PH abbrev copy (12.5% DKI winner kept) |
| `Sales_Outsource_PH` | Outsource Lead Generation | 0% (0 impr) | old copy / make room for human RSAs |
| `Appointment_Setter_Hire_PH` | Hire Appointment Setter | 0% (0 impr) | CTR below 5% · old PH/DKI copy |

## Kept (not paused)

- CTR winners in these groups (Recruiting DKI 18.6%, Sales DKI 12.5%, CS hire 13.3%, CS outsource 16%, social outsource 20%, marketing hire 20%, books outsource 7.9%, books hire DKI 7.1%, accounting hire DKI 25%, marketing outsource 50% on tiny sample, HR hire shortlist 50% on 2 impr).
- Aug 10 rewritten ads already serving (human-ish copy on the old ad ids).
- CORE and Brand. `Admin_City_Test`.

## Import (do not Enable)

1. Editor → USA account (`496-715-1855`) → **Get recent changes**.
2. **Account → Import → From file…** → `google-ads-editor-rsa-pause-weak-us.csv`
3. Preview should show **19 Ad changes** to **Paused** (not campaign/ad group status). Post.
4. In each ad group in the table, **remove** those paused old ads (3-ad cap). Admin needs **2** removed; every other group in the table needs **1**.
5. **Account → Import → From file…** → `google-ads-editor-rsa-add-human-us.csv`
6. Preview should show **19 Ad adds**, all **Paused**. Post. Enable only after you like them.

Do not import `google-ads-editor-rsa-add-admin-us.csv` on top — those two admin ads are already in the human add file.
