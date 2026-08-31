# One reported US employer conversion — reconstruction

**Window:** Google Ads last-7 complete days **10–16 August 2026** (executive snapshot generated 17 Aug 17:57 UTC).  
**Rule:** blank means not verified. Do not guess.

| Field | Verified value | Source | Notes |
| --- | --- | --- | --- |
| Conversion timestamp | | | Not in campaign-level snapshot. Nested windows: 0 conversions on 15–16 Aug; 1.0 conversions on 14–16 Aug. **Likely 14 Aug 2026** in the account timezone. Exact hour unknown. |
| Conversion action | | | Campaign snapshot does not name the action. Operator stack at the time: phone click, 60s calls from ads, 60s website calls, `VC_US_Thank_You` (GTM v5). Which of those produced the 1.0 is **unverified**. |
| Campaign | `VC_US_S_CORE` | `xray/data/executive-snapshot.json` | Last 7: 1.0 conversions / 2.0 all_conversions. `VC_US_S_ROLES` = 0. |
| Ad group | | | Not in the 2-call campaign snapshot. RSA 4–13 Aug file had 0 conversions on listed US RSAs. |
| Keyword | | | Not pulled (Ads API cap). |
| Search term | | | Not pulled for this conversion. |
| Match type | | | Not pulled. |
| RSA / ad ID | | | Not pulled. |
| Final URL | `https://www.virtualcoworker.app/us` (campaign Final URL) | Editor package + GA4 paid landings | CORE Final URL is `/us`. Not proven this click used that URL. |
| Landing-page path | | | Not joined to the Ads conversion. |
| Page version / git at that moment | If the conversion is 14 Aug: **not guided-match**. Guided-match shipped 16 Aug. 14 Aug was still the simplify/consult / form-in-hero family (chat/exit off that day). Exact SHA for the conversion click is **unverified**. | Git log vs brief chronology | Do not treat `stage1-v8` or `baseline_v1_2026_08` as the converting page. |
| Device | | | Not pulled. |
| GCLID presence | | | Zoho week census: 0 `usa_with_gclid`. Missing GCLID ≠ organic. This conversion is **unattributed** in CRM. |
| Classification | **Unresolved** | | Cannot prove genuine US employer vs job seeker vs QA vs sales test. GA4 `employer_inquiry_submitted` = 0 for 6–17 Aug. Ads 1.0 could be a phone/call action rather than a form. 11 Aug had heavy `experiment_convert` from 5 users (QA-contaminated). |

## What this is not

- Not a scored landing-page winner.
- Not a reason to roll `/us` back to an older layout.
- Not proof that Cheyenne’s labelled organic enquiries include this click.

## If it later verifies as an employer form

Preserve the **14 Aug** page family as a challenger candidate from git around 11–15 Aug (`MarketLanding` / `LeadGate` form-in-hero), not the 18 Aug guided-match or the later `StaffingBaselineLanding`. Do not auto-replace `US_BASELINE_2026-08-18`.
