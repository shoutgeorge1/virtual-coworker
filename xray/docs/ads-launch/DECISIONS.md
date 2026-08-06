# Stage 1 decisions (locked 2026-08-05 · v6)

George asked for decisive defaults so QA / deploy can proceed. These are **operator defaults**, not “launch ready” and not Ads enable approval. Campaigns stay **Paused**. Change anytime.

| Decision | Locked value | Notes |
|----------|--------------|-------|
| **Architecture** | **2 campaigns × 2 markets** | `VC_{US\|AU}_S_CORE` (~60%) + `VC_{US\|AU}_S_ROLES` (~40%). Brand **deferred**. |
| **Core Final URL** | `…/us` · `…/au` | Generic VA/hire/offshore → market employer home. **Not** administrative-support. |
| **Roles Final URL** | Matching category slug | Admin AG → `/administrative-support`; HR → `/hr` (alias `/human-resources` → `/hr`). |
| **AU phone** | Form-primary only | No `NEXT_PUBLIC_AU_PHONE`. No fake AU number. |
| **US phone** | `310-426-8776` via `NEXT_PUBLIC_US_PHONE` | Brief NA number. |
| **Careers URL** | `/ph` (PH microsite) | Internal job-seeker exit. **Never** WordPress. Env WP hosts rejected. |
| **Lead delivery** | Real channel required for paid | `ALLOW_LOG_ONLY_LEADS=true` = **explicit blocked mode** — QA logs only, `conversion_eligible=false`, not paid-ready. Zoho not live. |
| **Exit-intent** | Off unless `NEXT_PUBLIC_ENABLE_EXIT_INTENT=true` | Frequency-capped once/session. No fake live chat. |
| **Ads conversions** | `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false` | Observe-only; no Ads conversion firing. |
| **Pilot indexing** | `NEXT_PUBLIC_PILOT_NOINDEX=true` | Keep pilot out of organic index. |
| **LP version** | `stage1-v7` | Core→market-home routing stamp. |
| **US daily budgets** | Core **$75** · Roles **$50** | USD. ≈ **$125/day** ≈ **$3.8k/mo** — placeholders inside a **$10–20k/account** monthly budget story (room to scale). George-decidable. |
| **AU daily budgets** | Core **A$75** · Roles **A$50** | AUD. Same ~60/40 split. ≈ **A$3.8k/mo** Stage 1 pace. George-decidable. |
| **Max CPC** | US **$8** · AU **A$6** | Maximize Clicks cap. George-decidable. |
| **RSA count** | **3 unique full RSAs (15H/4D) per main AG** | Distinct angles (hire-intent / role or PH-offshore / proof-speed). City-test AGs stay 1–2. No fake claims. |
| **Google Ads Post / enable** | **Not approved** | Package ships Paused. No live campaign enable from this decision set. |

## Still open (not faked)

- Real lead email / webhook recipients (**hard blocker** — log-only ≠ paid)
- Named responder + response-time SLA per market
- US + AU custom domains + per-market GTM/GA4/GSC
- Zoho CRM sync
- CallRail / qualified-call tracking
- GTM Ads conversion mapping (tested)
- Explicit George approval to enable any Search campaign
- Brand Search (deferred — not in this CSV)
- Pause decision on legacy `PM_*` Brand campaigns still live outside this package

## Where applied

- Editor CSV budgets/CPC: `build_stage1_editor_package.py` → `google-ads-editor-import.csv`
- Vision prod env: vision-three-alpha (`vision` Vercel project)
