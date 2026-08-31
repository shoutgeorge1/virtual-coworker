# US_BASELINE_2026-08-18

Permanent freeze of the US paid landing-page experience used for measurement.
Not an A/B winner. Restore from this record, do not rebuild from memory.

| Field | Value |
| --- | --- |
| Label | `US_BASELINE_2026-08-18` |
| Live URL | https://www.virtualcoworker.app/us |
| Component | `StaffingBaselineLanding` + `GuidedMatchGate` |
| Authoritative `lp_version` | `baseline_v1_2026_08` (single source: `vision/config/lp-version.ts`) |
| Semantic label (events) | `US_BASELINE_2026-08-18` |
| Git HEAD at freeze (this repo) | `3a67bf8` — 18 Aug 2026 04:37 PDT — “Fix role H1s so RSA person nouns read as English.” |
| Production deploy named in the 18 Aug evidence brief | `dpl_GCevV6WPjn8Bkr1eMAWbV2QfoNz2` — 17 Aug 2026 16:06:47 PDT (SHA inferred `d8c6633`; inspect did not print a SHA) |
| Measurement-repair production deploy | `dpl_34uzqp6wzc4hkYDXRFkZ3U71TcG6` — 18 Aug 2026 09:36:20 PDT — inspector https://vercel.com/shoutgeorge1s-projects/vision/34uzqp6wzc4hkYDXRFkZ3U71TcG6 |
| Headline (current committed baseline) | Hire Dedicated Filipino Remote Staff From $7/Hour |
| Primary interaction | Guided match: role → hours → people → contact → `POST /api/lead` |
| Phone | (888) 964-8644 |
| Desktop / mobile evidence | Evidence brief 18 Aug 2026 (GuidedMatch snapshot) plus live `/us` after baseline v1 rollout (`e03d1dd`) |
| Known tracking limitations (before this repair) | `employer_inquiry_submitted` and phone events implemented in code but not arriving in GA4; Ads suffix still `lp_version=stage1-v7`; Zoho `utm_gclid` unconfirmed |
| Clean measurement start | **2026-08-18** (after this event-pipeline deploy is live). Do not score a page winner until events are verified in GA4. |

## Restore

Keep `StaffingBaselineLanding` on `/us` and role URLs. Do not silently replace with an older GuidedMatch-in-hero layout unless George explicitly asks.

Code stamp to restore: `BASELINE_LP_VERSION` / `AUTHORITATIVE_LP_VERSION` = `baseline_v1_2026_08`.

## What is not this baseline

- `/us/staffing` — unused staffing-agency **candidate** (`staffing_agency_candidate_2026_08_18`). Not an Ads Final URL.
- `/us/quiz`, `/us/offer`, retired aliases (`/us/start` etc.).
- Australian `/au` pages share the template but are **not** this US freeze.
