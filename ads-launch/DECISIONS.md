# Stage 1 decisions (locked 2026-08-05 · v6)

George asked for decisive defaults so QA / deploy can proceed. These are **operator defaults**, not “launch ready” and not Ads enable approval. Campaigns stay **Paused**. Change anytime.

| Decision | Locked value | Notes |
|----------|--------------|-------|
| **Architecture** | **2 campaigns × 2 markets** | `VC_{US\|AU}_S_CORE` (~60%) + `VC_{US\|AU}_S_ROLES` (~40%). Brand **deferred**. |
| **AU phone** | Form-primary only | No `NEXT_PUBLIC_AU_PHONE`. No fake AU number. |
| **US phone** | `310-426-8776` via `NEXT_PUBLIC_US_PHONE` | Brief NA number. |
| **Careers URL** | `NEXT_PUBLIC_CAREERS_URL=/ph` | Existing PH apply/careers path on microsite. No better confirmed external careers URL in repo. |
| **Lead delivery (QA)** | `ALLOW_LOG_ONLY_LEADS=true` on Vercel production | **TEMPORARY** until real inbox (`LEAD_EMAIL_*` / Resend / webhook). Forms accept validated leads to **server logs only**. Zoho is **not** live — do not pretend sync. |
| **Ads conversions** | `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false` | Observe-only; no Ads conversion firing. |
| **Pilot indexing** | `NEXT_PUBLIC_PILOT_NOINDEX=true` | Keep pilot out of organic index. |
| **US daily budgets** | Core **$75** · Roles **$50** | USD. ≈ **$125/day** ≈ **$3.8k/mo** — placeholders inside a **$10–20k/account** monthly budget story (room to scale). George-decidable. |
| **AU daily budgets** | Core **A$75** · Roles **A$50** | AUD. Same ~60/40 split. ≈ **A$3.8k/mo** Stage 1 pace. George-decidable. |
| **Max CPC** | US **$8** · AU **A$6** | Maximize Clicks cap. George-decidable. |
| **Google Ads Post / enable** | **Not approved** | Package ships Paused. No live campaign enable from this decision set. |

## Still open (not faked)

- Real lead email / webhook recipients (log-only is QA only)
- Zoho CRM sync
- CallRail / qualified-call tracking
- GTM Ads conversion mapping
- Explicit George approval to enable any Search campaign
- Brand Search (deferred — not in this CSV)
- Pause decision on legacy `PM_*` Brand campaigns still live outside this package

## Where applied

- Editor CSV budgets/CPC: `build_stage1_editor_package.py` → `google-ads-editor-import.csv`
- Vision prod env: vision-three-alpha (`vision` Vercel project)
