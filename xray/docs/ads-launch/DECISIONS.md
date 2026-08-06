# Stage 1 decisions (locked 2026-08-05 · v6 + activation flip)

George asked for decisive defaults so QA / deploy can proceed. These are **operator defaults**, not “launch ready” and not Ads enable approval. Campaigns stay **Paused**. Change anytime.

## Operating rule (locked — judgment over busywork)

**Old account = historical archive. New campaigns = isolated clean system.**

| Do | Do not |
|----|--------|
| Import / review / Post **new paused `VC_*` only** | Dig / delete / rewrite / pause binge on old account-wide machinery tonight |
| Attach **tight curated** campaign negatives from the Stage 1 builder (~175 terms) | Inherit account shared / `PM_*` mega negative lists (3000+ dumps) onto `VC_*` |
| Plan **new** Ads conversion actions via **new** per-market GTM | Touch / replace / delete old Zoho/Zapier conversion actions or historical reporting |
| Set **campaign-specific goals** on each `VC_*` after Post (Ads UI) | Let `VC_*` optimize toward account-default junk conversion baskets |
| Keep audiences off for initial Search launch (Observation later) | Use audiences to restrict targeting at launch |
| Keep every `VC_*` **Paused** — Import ≠ live | Enable / unpause from CSV or Import/Post alone |

Editor may not fully express goals — see Launch Control + `EDITOR-PREFLIGHT-REPORT.md` for Ads UI steps.

| Decision | Locked value | Notes |
|----------|--------------|-------|
| **Architecture** | **2 campaigns × 2 markets** | `VC_{US\|AU}_S_CORE` (~60%) + `VC_{US\|AU}_S_ROLES` (~40%). Brand **deferred**. |
| **Core Final URL** | `…/us` · `…/au` | Generic VA/hire/offshore → market employer home. **Not** administrative-support. |
| **Roles Final URL** | Matching category slug | Admin AG → `/administrative-support`; HR → `/hr` (alias `/human-resources` → `/hr`). |
| **Activation priority** | **PH / Filipino / offshore long-tail first** | Source of truth: `PHASED-ACTIVATION.md`. Phase by **intent quality**, not “Core then Digital/Social/Admin.” Bookkeeping/accounting with strong PH long-tail = Phase 1. Generic Core heads = Phase 3 / later. |
| **AU phone** | Form-primary only | No `NEXT_PUBLIC_AU_PHONE`. No fake AU number. |
| **US phone** | `310-426-8776` via `NEXT_PUBLIC_US_PHONE` | Brief NA number. |
| **Careers URL** | `/ph` (PH microsite) | Internal job-seeker exit. **Never** WordPress. Env WP hosts rejected. |
| **Lead delivery** | Real channel required for paid | `ALLOW_LOG_ONLY_LEADS=true` = **explicit blocked mode** — QA logs only, `conversion_eligible=false`, not paid-ready. Zoho not live. |
| **Exit-intent** | Off unless `NEXT_PUBLIC_ENABLE_EXIT_INTENT=true` | Frequency-capped once/session. No fake live chat. |
| **Ads conversions (firing)** | `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false` | Observe-only until new GTM → new Ads actions tested. |
| **New conversion actions** | **Plan via new GTM** — do not replace old | Create **new** actions: (1) employer inquiry **delivered** (2) phone ~60s / qualified call when CallRail ready. Leave old Zoho/Zapier actions untouched for archive/reporting. |
| **Campaign goals** | **Campaign-specific on each `VC_*`** | After Post in Ads UI: Goals → campaign-specific → only the new actions. Editor CSV cannot fully express this. |
| **Negatives** | **VC-only curated campaign negs** | Builder emits campaign-level Broad rows from `NEGATIVES` only. Soft cap ~220 unique. Never attach account shared mega lists to `VC_*`. |
| **Audiences** | **Off at launch** | Observation later; ignore customer-lifecycle warnings until Zoho/first-party data. Not launch-critical. |
| **Pilot indexing** | `NEXT_PUBLIC_PILOT_NOINDEX=true` | Keep pilot out of organic index. |
| **LP version** | `stage1-v7` | Core→market-home routing stamp. |
| **US daily budgets** | Core **$75** · Roles **$50** | USD. ≈ **$125/day** ≈ **$3.8k/mo** — placeholders inside a **$10–20k/account** monthly budget story (room to scale). George-decidable. |
| **AU daily budgets** | Core **A$75** · Roles **A$50** | AUD. Same ~60/40 split. ≈ **A$3.8k/mo** Stage 1 pace. George-decidable. |
| **Max CPC** | US **$8** · AU **A$6** | Maximize Clicks cap. George-decidable. |
| **RSA count** | **3 unique full RSAs (15H/4D) per main AG** | Distinct angles (hire-intent / role or PH-offshore / proof-speed). City-test AGs stay 1–2. No fake claims. |
| **Google Ads Post / enable** | **Not approved** | Package ships Paused. No live campaign enable from this decision set. |
| **Editor CSV Account column** | **Required** | Every row stamps Customer ID: USA `496-715-1855` · AU `573-539-1940`. Needed for USA+AU multi-account Editor import so rows don’t land in the wrong account. |

### Import vs Post (plain English — do not confuse)

| Step | What it does | Live Ads? |
|------|--------------|-----------|
| **Import** into Editor | Loads entities into a **local Editor draft** | **No** — does not change the live account |
| **Post** from Editor | Uploads those draft entities to the **live** Google Ads account | **Yes** — creates/updates live entities (still Paused if Status=Paused) |

- Our `VC_*` campaigns are **new names**. They **add alongside** existing `PM_*` museum campaigns. They do **not** wipe account-level settings (conversions, billing, users, linking).
- They do **not** delete old campaigns unless we explicitly remove / post removals.
- Account-level conversion actions are **separate** — the campaign CSV does not replace those.
- Without the **Account** column, multi-account import can fail or apply to the wrong account — fixed in builder as of this decision.

## Still open (not faked)

- Real lead email / webhook recipients (**hard blocker** — log-only ≠ paid)
- Named responder + response-time SLA per market
- US + AU custom domains + per-market GTM/GA4/GSC
- **Zoho access audit** (George has some access now — level unknown): modules · fields · ownership · download/export OK for later review. **Access ≠ integration complete.**
- **Offline conversion actions** (plan later — **not** Stage 1 primary):
  - Job order — value TBD (range discussed **$200–$400**, **not approved**)
  - Job placement — value TBD (range discussed **$500–$800**, **not approved**)
  - Deduping: unique Zoho IDs as conversion IDs; don’t double-count order+placement on the same journey without rules; GCLID / offline import path
- Stage 1 primary conversions remain **employer inquiry** + **qualified call** (when wired). Job order / placement = later offline.
- CallRail / qualified-call tracking
- GTM Ads conversion mapping (tested)
- Explicit George approval to enable any Search campaign
- Brand Search (deferred — not in this CSV)
- Pause decision on legacy `PM_*` Brand campaigns still live outside this package

## Where applied

- Editor CSV budgets/CPC + Account stamps: `build_stage1_editor_package.py` → `google-ads-editor-import.csv`
- Vision prod env: vision-three-alpha (`vision` Vercel project)
