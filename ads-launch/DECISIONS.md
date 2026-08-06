# Stage 1 decisions (locked 2026-08-05 · v6 + activation flip)

George asked for decisive defaults so QA / deploy can proceed. These are **operator defaults**, not “launch ready” and not Ads enable approval. Campaigns stay **Paused**. Change anytime.

## Launch sequencing (LOCKED — 2026-08-06 addendum)

**Do NOT make complete Zoho CRM, native Zoho↔Google Ads, offline conversions, or Google Ads API access prerequisites for the initial Maximize Clicks launch.**

### Three Launch Control statuses

| Status | Meaning | Required for first Max Clicks Enable? |
|--------|---------|---------------------------------------|
| **TRAFFIC READY** | Durable monitored lead delivery + named responder gate (see below) | **Yes** (plus George Enable approval) |
| **CRM READY** | Direct Zoho record write + verified field mapping | **No** — parallel workstream |
| **OPTIMIZATION READY** | GTM/Ads conversions, campaign-specific goals, downstream CRM feedback | **No** — after traffic is learning |

### TRAFFIC READY minimum (all verified)

1. Employer form accepted server-side  
2. One durable monitored channel works: real **email**, **webhook**, or **sheet** — **not** log-only  
3. Live-format test submission reaches that destination  
4. Named human responder + practical response process confirmed  
5. Market, landing URL, UTMs, GCLID/GBRAID/WBRAID when available, submission ID retained  
6. US/AU routing correct  
7. Campaigns remain **Paused** until George explicitly Approves Enable  

**Not required for TRAFFIC READY:** completed Zoho record, Zoho OAuth, native Ads auth, offline conversion upload, or working Google Ads conversion action.

### Initial bidding / activation (unchanged intent)

- Keep **Maximize Clicks**; CPC US **$8** / AU **A$6**  
- Exact + Phrase only; no Broad+ / PMax / DSA / Max Conv at launch  
- Start Tier **1A** explicit hire/outsource/staffing; add reviewed Tier **1B** PH/Filipino commercial for volume  
- Generic geo-category + generic VA Core later  
- No historical shared negs / audiences / conversions / account machinery on `VC_*`  
- Don’t switch Max Conv until new conversion action verified + meaningful data  

Zoho remains a **PARALLEL** workstream — **not** a traffic blocker. **Platform discovery + live inventory/API implementation are DEFERRED** (see `ads-launch/zoho/DEFERRED-PLATFORM-DISCOVERY.md`): George’s UI shows **no Leads**; visible spine includes Accounts / Contacts / Job Orders / Placements. May be Zoho Recruit or heavily customized CRM — **do not assume CRM API V8 or hardcode Leads**. Native Ads audit stays separate and does **not** assume George’s pending Ads developer token.

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
| **Domain model** | **One host + path markets** | `/us` · `/au` · `/ph` on the same domain (preview host OK). **Not** two country domains for Stage 1. Optional one paid domain later = polish, **not** TRAFFIC READY. When attached, same paths transfer — no AU subdomain. |
| **Core Final URL** | `…/us` · `…/au` | Generic VA/hire/offshore → market employer home. **Not** administrative-support. |
| **Roles Final URL** | Matching category slug | Admin AG → `/administrative-support`; HR → `/hr` (alias `/human-resources` → `/hr`). |
| **Measurement** | **Separate GTM + GA4 per market** | `GTM_US` / `GTM_AU` (+ `GTM_PH` if needed) even on one host — audiences/conversions must not contaminate. |
| **Activation priority** | **PH / Filipino / offshore long-tail first** | Source of truth: `PHASED-ACTIVATION.md`. Phase by **intent quality**, not “Core then Digital/Social/Admin.” Bookkeeping/accounting with strong PH long-tail = Phase 1. Generic Core heads = Phase 3 / later. |
| **AU phone** | Form-primary only | No `NEXT_PUBLIC_AU_PHONE`. No fake AU number. |
| **US phone** | `310-426-8776` via `NEXT_PUBLIC_US_PHONE` | Brief NA number. |
| **Careers URL** | `/ph` (PH microsite) | Internal job-seeker exit. **Never** WordPress. Env WP hosts rejected. |
| **Lead delivery** | Real channel required for **TRAFFIC READY** | `ALLOW_LOG_ONLY_LEADS=true` = **explicit blocked mode** — QA logs only, `conversion_eligible=false`, not TRAFFIC READY. Zoho CRM = **CRM READY** parallel track (not a traffic gate). |
| **Exit-intent** | Off unless `NEXT_PUBLIC_ENABLE_EXIT_INTENT=true` | Frequency-capped once/session. No fake live chat. |
| **Ads conversions (firing)** | `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false` | Observe-only until new GTM → new Ads actions tested. |
| **New conversion actions** | **Plan via new GTM** — do not replace old | Create **new** actions: (1) employer inquiry **delivered** (2) phone ~60s / qualified call when CallRail ready. Leave old Zoho/Zapier actions untouched for archive/reporting. |
| **Calendly / booking** | Wired on thank-you from live WP (2026-08-06) | US `calendly.com/cheyenne-virtualcoworker/30min` · AU `calendly.com/apac-virtualcoworker/30min`. Env override: `NEXT_PUBLIC_CALENDLY_US` / `_AU`. Confirm with VC. **Not** TRAFFIC READY. Booking CTA = Stage 1 **secondary / separate conversion candidate** — do **not** replace primary `employer_inquiry_submitted`. Booked-call event = OPTIMIZATION READY / later once GTM fires. |
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

### TRAFFIC READY gates (hard for Enable)

- Real lead email / webhook / sheet (**hard blocker** — log-only ≠ TRAFFIC READY)
- Live-format test submission reaches that destination
- Named responder + practical response process per market
- Explicit George approval to Enable any Search campaign

### Parallel / later (not traffic blockers)

- Optional **one** custom domain (path markets stay) + per-market GTM/GA4/GSC (`GTM_US` + `GTM_AU`) → **OPTIMIZATION READY** — domains are polish; separate containers are the measurement requirement
- **Zoho platform discovery** (product + API path) → then inventory / OAuth / adapter / field mapping → **CRM READY** — **deferred**; access ≠ integration complete; no Leads assumption
- Native Zoho↔Ads audit (observe only; separate from Ads developer token; do not authorize from repo work)
- **Offline conversion actions** (plan later — **not** Stage 1 primary / not TRAFFIC READY):
  - Job order — value TBD (range discussed **$200–$400**, **not approved**)
  - Job placement — value TBD (range discussed **$500–$800**, **not approved**)
  - Deduping: unique Zoho IDs as conversion IDs; don’t double-count order+placement on the same journey without rules; GCLID / offline import path
- Stage 1 primary conversion (when wired for optimization): **employer inquiry delivered**. Qualified call when CallRail ready. Job order / placement = later offline.
- Thank-you → **book hiring conversation** (Calendly): Stage 1 **secondary** or separate conversion candidate — **never** Primary replacing `employer_inquiry_submitted`. Confirm URLs with VC; booked-call event when GTM ready → OPTIMIZATION READY / later. **Not** required for TRAFFIC READY.
- CallRail / qualified-call tracking
- GTM Ads conversion mapping (tested) → **OPTIMIZATION READY**
- Brand Search (deferred — not in this CSV)
- Pause decision on legacy `PM_*` Brand campaigns still live outside this package

## Where applied

- Editor CSV budgets/CPC + Account stamps: `build_stage1_editor_package.py` → `google-ads-editor-import.csv`
- Vision prod env: vision-three-alpha (`vision` Vercel project)
