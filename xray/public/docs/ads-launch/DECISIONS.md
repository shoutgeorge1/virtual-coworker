# Stage 1 decisions (locked 2026-08-05 · v6 + activation flip)

George asked for decisive defaults so QA / deploy can proceed. These are **operator defaults**, not “launch ready” and not Ads enable approval. Campaigns stay **Paused**. Change anytime.

## Google Ads API lock (HARD — permanent)

**API = read-only / cheap probes ONLY.** Stage 1 package work = **Google Ads Editor CSV only**.

| Allowed | Forbidden |
|---------|-----------|
| `list_accessible_customers` or one tiny Search `LIMIT 1` | Create / update / enable campaigns, AGs, ads, keywords, budgets via API |
| Max **1–2** API calls unless George explicitly authorizes more | Bulk mutate, inventory dumps, pagination loops |
| Stop immediately on quota / `RESOURCE_EXHAUSTED` | Treat “API is live” as permission to Post or Enable |

Past burn: agents launched ~8 campaigns + many AGs via API and burned developer-token quota on ELA — do not repeat. Durable agent rule: `~/.cursor/rules/google-ads-api-editor-only.mdc`.

## Keyword intent priority — agency-hire (2026-08-09)

- **Highest intent:** employer searching for a **Philippines VA / staffing agency · firm · company · outsourcing** provider (not a job board, not “I need a job”).
- Plain **hire / hiring / recruit** stays useful as support but is messier (employer vs job-seeker). Do not lead strategy with ambiguous head terms alone.
- Package add-on: `ads-launch/google-ads-editor-agency-intent-keywords-add.csv` (Exact, **Paused**). `va workers ph` stays watch/pause — not a claimed win.
- Strategy = intent quality. Do **not** invent that these Exact adds are already converting without Ads evidence.

## Brand deferred (HARD — 2026-08-06 · paused 2026-08-07)

- Old agencies wasted money; live accounts are on **trickle mode**. Whatever is still Enabled (including Brand) is **obvious from the Ads UI** — not an agent “discovery.” Do **not** surface it unprompted.
- Do **not** center strategy, probes, checklists, or next steps on Brand.
- Stage 1 priority: build the real clean **`VC_*` Editor package** first. Brand = tap later after that system exists.
- Optional API “what’s spending now” probes = **low value**; don’t push them.
- Durable agent rule: `~/.cursor/rules/vc-ads-brand-deferred.mdc`.

### Brand paused by George (2026-08-07) — DONE / deferred

- George **turned Brand OFF** (paused). Cost per conversion was in the very expensive range (~**$1,000 per lead** order of magnitude). **SEO owns brand**; people searching the name usually find organic. Other advertisers may still bid brand; rebuild a clean Brand campaign later only when George asks.
- If VC ever sees a **competitor using “Virtual Coworker” in their ads**, tell George immediately — possible policy issue.
- **Do not re-enable** Brand. **Do not** center strategy, probes, or checklist next-steps on Brand.
- Aligns with Brand deferred hard rule above.
- Stakeholder follow-up email (**Brand paused + phone tracking**) **sent** 2026-08-07 to Braden / Caitlin / Cheyenne (CC George).

### Planning exception (2026-08-13) — George asked

- George sent a **medium** checklist: **US Brand Defense Campaign — .com + Target Impression Share**.
- This is a **planning / checklist** project. It does **not** become this week’s #1. Tracking, form simplify, daily search terms, and the forensic audit stay first.
- Live `Brand_VC` inside CORE: **do not pause / split / edit** in this pass.
- Recommendation: **B prepare paused Editor `VC_US_S_BRAND`**; keep A live until George Approves Enable. Do not Post. Do not email Braden.
- Audit: `ads-launch/BRAND-US-DEFENSE-AUDIT-2026-08-13.md`. Checklist: Launch Control `#brand-defense`.
- Historical $803 / ~$1k CPA remains **untrusted** (not a qualified-lead number).

## Zoho + offline conversions — DEFERRED DURING COLD START (HARD — 2026-08-14)

Zoho is **not cancelled**. It is **not** an active Google Ads optimization project right now. Campaigns are about one week into cold start. Immediate priority: generate and improve **verified employer conversion signal** (search terms, ads, landing pages, forms, bookings, calls).

Full lock: `ads-launch/ZOHO-COLD-START-DEFERRED-2026-08-14.md`. Checklist: Launch Control `#zoho-deferred-cold-start`.

| Keep | Do not |
|------|--------|
| Zoho API **read-only** | Build a new Zoho → Google Ads offline-conversion integration |
| `.app` → Zoho production writes **OFF** | Add Zapier |
| Front-end Ads conversion tracking | Change existing Zoho records, workflows, fields, users, or permissions |
| GCLID / GBRAID / WBRAID / UTMs / campaign / landing / submission ID on `.app` enquiries | Make any existing Zoho-related Google Ads conversion **Primary** |
| Email delivery of employer leads | Alter bidding or campaign settings through the API |
| Dashboard read-only Zoho monitoring for business context | Use unverified CRM outcomes as bidding signals |
| Maximize Clicks | Treat missing `VC_*` / `.app` stamps on current Zoho rows as a Zoho failure |

**Why:** Historical Google click IDs were not consistently preserved; most enquiries sit under broad sources such as “Website”; legacy “Zoho JO Submitted,” “Standard OCI,” and possible Zapier uploads may overlap or be incomplete slices; Job Order uploads/values do not reconcile cleanly enough to bid on. Missing `VC_*` / `.app` attribution on new records is **expected** — new forms are not connected yet.

**Revisit only after:** (1) enough qualified employer enquiries (2) VC names the Zoho owner (3) existing Zoho / Zapier / Google Ads uploads are documented and reconciled (4) one `.app` Sales Enquiry can be tested safely end to end (5) CRM outcome definitions and values are consistent enough to validate.

### Communication record (2026-08-14)

George emailed **Braden** and **Amanda** with subject **Stage 1 conversion strategy and Zoho next steps**. George supports offline conversions long term, but recommends slowing that work during cold start and validating the previous agency’s implementation before adding another feedback system.

## US phone / Call assets (LOCKED — 2026-08-10 · George restore)

**Phone = guiding light** during cold start. Zoho offline “qualified lead” is **deferred** (2026-08-14 lock) — not this week’s Ads optimization work. USA Search stays **Maximize Clicks** while campaigns season. Primary: ~60s call from ads. Secondary: website phone taps. Forms useful but not driving the account (spam/bot risk).

**George restore 2026-08-10 (later):** verified US line is **888-964-8644** / `tel:+18889648644`. The same-day 310 swap is **superseded**. 888-954 and 888-864 are wrong — never publish.

| Number | Role | Do | Do not |
|--------|------|----|--------|
| **888-964-8644** | US site + Call asset (**primary**, George 2026-08-10 restore) | Use on website (`NEXT_PUBLIC_US_PHONE` / site defaults `(888) 964-8644` / `tel:+18889648644`) **and** on `VC_US_S_CORE` / `VC_US_S_ROLES` Call assets. Reuse existing asset `49435983302`. | Do not publish 888-864-8644 or 888-954-8644. |
| **310-730-9126** | **Not public** (mistaken morning swap) | Leave library asset; unlink from VC_US_* serving scopes. | Do not use as the public US number on microsite or ads. |
| **888-954-8644** | **Wrong — never publish** | Leave unlinked. | Do not treat as the live buyer number. |

### Later / ops (open)

- **888-964-8644** is the live US line on pages we control (George 2026-08-10 restore).
- Stakeholder emails **sent** 2026-08-07 (phone-tree ask + Brand/phone follow-up) — historical.

### Measurement (2026-08-07)

- Fresh **GTM + GA4** on the new microsite so this test’s data stays separate from older WordPress/tagging. Not a judgment on the past — don’t mix signals.
- Sniper negatives: campaign-level list **`VC_US_S_🚫_Sniper`** attached by George to CORE + ROLES (manual). Repo: `ads-launch/VC_US_S_Sniper_Negatives.*`.
- **Next session:** site A/B tests → GA4 wiring on Site tests dashboard.
- **Zoho “qualified lead” → Ads offline conversion:** **superseded 2026-08-14** — deferred during cold start. See HARD lock above. Do not treat the old “early next week” aim as live work.
- **Australia:** confirm/add the AU number in Ads before launch — don’t assume answering is ready.

## Conversion / CRM stack (LOCKED direction — 2026-08-06)

**Do NOT use old account conversions** (old Zoho/Zapier micros, junk Primaries). Build **new, simple** actions for `VC_*`. Leave museum actions untouched for archive/reporting.

### Stage 1 / soon (OPTIMIZATION path — **not** a TRAFFIC READY blocker)

1. **Form fill → thank-you** — primary online signal. Employer inquiry delivered (`employer_inquiry_submitted` after durable delivery). Calendly already on thank-you (US/AU) = **secondary / separate** candidate — never a second Primary for the same inquiry.
2. **Phone call** — basic click-to-call OK to observe; **phone CTA ≠ qualified** until CallRail (or equivalent) exists. Plan a real call conversion later.
3. Prefer **direct integrations** (form → email/webhook/sheet) over complicated Zapier architecture. Zapier may exist in the museum — document only. **Do not add Zapier.**
4. **Zoho (2026-08-14):** **deferred during cold start** — not cancelled, not an active Ads optimization project. API read-only. `.app` writes OFF. No new Zoho→Ads offline integration. No Zoho record/workflow/field/user/permission changes. Ask VC who owns CRM only when the revisit gate is met.
5. **Zoho ↔ Google Ads native integration** — do **not** make existing Zoho-related conversions Primary. Use later only after the revisit gate. **Not** a duplicate Primary for the same inquiry.
6. **CallRail:** layer in ~1–2 months when they get serious — **not** Stage 1 required.
7. Offline / higher-value conversions via Zoho **after** the 2026-08-14 revisit gate — not during this cold start.

### Still true

| Lock | Meaning |
|------|---------|
| **TRAFFIC READY** | Durable delivery + named responder (email/webhook/sheet OK first). Zoho **not** required to start Max Clicks. |
| **One inquiry ≠ two Primaries** | Don’t double-count form + Calendly + Zoho offline on the same event as multiple Primaries. |
| **Brand deferred** | Clean `VC_*` Editor package first. |
| **Editor for package / API read-only** | No Ads API mutate; no Enable from CSV. |
| **Host** | `www.virtualcoworker.app` Final URLs. |

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

- Keep **Maximize Clicks**; CPC US CORE **$12** / ROLES **$10** · AU **A$6**  
 
- Exact + Phrase only; no Broad+ / PMax / DSA / Max Conv at launch  
- Start Tier **1A** explicit hire/outsource/staffing; add reviewed Tier **1B** PH/Filipino commercial for volume  
- Generic geo-category + generic VA Core later  
- No historical shared negs / audiences / conversions / account machinery on `VC_*`  
- Don’t switch Max Conv until new conversion action verified + meaningful data  

Zoho remains a **PARALLEL** workstream — **not** a traffic blocker and **not** an active Ads optimization project during this cold start (2026-08-14 HARD lock). **Platform discovery + live inventory/API implementation stay DEFERRED** (see `ads-launch/zoho/DEFERRED-PLATFORM-DISCOVERY.md` and `ZOHO-COLD-START-DEFERRED-2026-08-14.md`): George’s UI shows **no Leads**; visible spine includes Accounts / Contacts / Job Orders / Placements. May be Zoho Recruit or heavily customized CRM — **do not assume CRM API V8 or hardcode Leads**. Native Ads audit stays separate and does **not** assume George’s pending Ads developer token. No new offline-conversion build until the revisit gate.

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
| **Domain model** | **One host + path markets** | **Production:** `www.virtualcoworker.app` (apex `virtualcoworker.app` → 308 → www) on Vercel project `vision`. Paths `/us` · `/au` · `/ph`. **Not** two country domains. Preview `vision-three-alpha.vercel.app` still exists for QA. Editor package default Final URL host = `www.virtualcoworker.app`. Domain ≠ durable leads / ≠ TRAFFIC READY. Same paths transfer — no AU subdomain. |
| **Core Final URL** | `…/us` · `…/au` | Generic VA/hire/offshore → market employer home. **Not** administrative-support. |
| **Roles Final URL** | Matching category slug | Admin AG → `/administrative-support`; HR → `/hr` (alias `/human-resources` → `/hr`). |
| **Measurement** | **Separate GTM + GA4 per market** | `GTM_US` / `GTM_AU` (+ `GTM_PH` if needed) even on one host — audiences/conversions must not contaminate. |
| **Activation priority** | **PH / Filipino / offshore long-tail first** | Source of truth: `PHASED-ACTIVATION.md`. Phase by **intent quality**, not “Core then Digital/Social/Admin.” Bookkeeping/accounting with strong PH long-tail = Phase 1. Generic Core heads = Phase 3 / later. |
| **AU phone** | Form-primary only | No `NEXT_PUBLIC_AU_PHONE`. No fake AU number. |
| **US phone (site + Ads)** | `(888) 964-8644` / `tel:+18889648644` | **Primary (George 2026-08-10 restore).** Never 888-864 or 888-954. 310 is not the public US number. AU stays **1300 886 740**. |
| **Careers URL** | `/ph` (PH microsite) | Internal job-seeker exit. **Never** WordPress. Env WP hosts rejected. |
| **Lead delivery** | Real channel required for **TRAFFIC READY** | `ALLOW_LOG_ONLY_LEADS=true` = **explicit blocked mode** — QA logs only, `conversion_eligible=false`, not TRAFFIC READY. Zoho CRM = **CRM READY** parallel track (not a traffic gate). |
| **Exit-intent / chat widgets** | **Hold** (2026-08-14) | Off unless `NEXT_PUBLIC_ENABLE_EXIT_INTENT=true` / `NEXT_PUBLIC_ENABLE_CHAT=true`. They obscure the LP, especially mobile. A/B vs clean LP later. No fake live chat. |
| **Ads conversions (firing)** | `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false` | Observe-only until new GTM → new Ads actions tested. |
| **New conversion actions** | **Build new — never reuse old account actions** | Stage 1 OPTIMIZATION: (1) form fill → thank-you / employer inquiry **delivered** (2) phone (basic now; qualified ~60s when CallRail). Prefer direct integrations. Leave old Zoho/Zapier actions untouched for archive. One inquiry ≠ two Primaries. |
| **Calendly / booking** | Wired on thank-you from live WP (2026-08-06) | US `calendly.com/cheyenne-virtualcoworker/30min` · AU `calendly.com/apac-virtualcoworker/30min`. Env override: `NEXT_PUBLIC_CALENDLY_US` / `_AU`. Confirm with VC. **Not** TRAFFIC READY. Booking CTA = Stage 1 **secondary / separate conversion candidate** — do **not** replace primary `employer_inquiry_submitted`. Booked-call event = OPTIMIZATION READY / later once GTM fires. |
| **Zoho lead port** | **Deferred during cold start** (2026-08-14) | Not cancelled. API read-only. Writes OFF. No new OCI, no Zapier, no Primary Zoho conversions, no Ads API bidding changes. Revisit only after the five-item gate in `ZOHO-COLD-START-DEFERRED-2026-08-14.md`. |
| **CallRail** | ~1–2 months | Not Stage 1 / not TRAFFIC READY. Until then phone CTA ≠ qualified call. |
| **Campaign goals** | **Campaign-specific on each `VC_*`** | After Post in Ads UI: Goals → campaign-specific → only the new actions. Editor CSV cannot fully express this. |
| **Negatives** | **VC-only curated campaign negs** | Builder emits campaign-level Broad rows from `NEGATIVES` only. Soft cap ~220 unique. Never attach account shared mega lists to `VC_*`. |
| **Audiences** | **Off at launch** | Observation later; ignore customer-lifecycle warnings until Zoho/first-party data. Not launch-critical. |
| **Pilot indexing** | `NEXT_PUBLIC_PILOT_NOINDEX=true` | Keep pilot out of organic index. |
| **LP version** | `stage1-v7` | Core→market-home routing stamp. |
| **US daily budgets** | Core **$75** · Roles **$50** | USD. ≈ **$125/day** ≈ **$3.8k/mo** — placeholders inside a **$10–20k/account** monthly budget story (room to scale). George-decidable. |
| **AU daily budgets** | Core **A$75** · Roles **A$50** | AUD. Same ~60/40 split. ≈ **A$3.8k/mo** Stage 1 pace. George-decidable. |
| **Max CPC** | US CORE **$12** / ROLES **$10** · AU **A$6** both | Maximize Clicks cap (live USA Editor 2026-08-07). AU stays conservative. George-decidable. |
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

### Domain / Final URLs (done — not a TRAFFIC READY substitute)

- **Live:** `www.virtualcoworker.app` — LPs confirmed; Editor CSVs regenerated with www Final URLs. Import should use those CSVs. Preview host remains for QA only. Still **Paused / not paid-ready** until TRAFFIC READY + George Enable.

### Parallel / later (not traffic blockers)

- Per-market GTM/GA4/GSC (`GTM_US` + `GTM_AU`) → **OPTIMIZATION READY** — separate containers are the measurement requirement
- **Zoho + offline conversions — DEFERRED DURING COLD START** (2026-08-14 HARD lock). Not cancelled. Not an active Ads optimization project. Full: `ZOHO-COLD-START-DEFERRED-2026-08-14.md`
- **Zoho platform discovery** (product + API path) → then inventory / OAuth / adapter / field mapping → **CRM READY** — parked behind the revisit gate; access ≠ integration complete; no Leads assumption
- Native Zoho↔Ads audit (observe only; separate from Ads developer token; do not authorize from repo work)
- **Offline conversion actions** (plan later — **not** Stage 1 primary / not TRAFFIC READY / not this cold start):
  - Job order — value TBD (range discussed **$200–$400**, **not approved**)
  - Job placement — value TBD (range discussed **$500–$800**, **not approved**)
  - Deduping: unique Zoho IDs as conversion IDs; don’t double-count order+placement on the same journey without rules; GCLID / offline import path
- Stage 1 primary conversion (when wired for optimization): **employer inquiry delivered** on the front end. Keep those values separate from unverified CRM outcomes. Job order / placement = later offline after the revisit gate.
- Thank-you → **book hiring conversation** (Calendly): Stage 1 **secondary** or separate conversion candidate — **never** Primary replacing `employer_inquiry_submitted`. Confirm URLs with VC; booked-call event when GTM ready → OPTIMIZATION READY / later. **Not** required for TRAFFIC READY.
- CallRail / qualified-call tracking
- GTM Ads conversion mapping (tested) → **OPTIMIZATION READY**
- **888 paused** on microsite (George 2026-08-10). WP 964 landmine remains (medical-alert IVR). Phone-tree ask on 888 is moot for pages we control.
- Brand Search (deferred — **paused by George 2026-08-07**; ~$1k/lead range; SEO owns brand; notify if competitor uses brand in ads; see **Brand deferred** hard lock — do not re-enable)
- Legacy `PM_*` Brand: **paused by George 2026-08-07** — leave off; rebuild later only when George asks
- Stakeholder follow-up (**Brand paused + phone tracking**) **sent** 2026-08-07

## Where applied

- Editor CSV budgets/CPC + Account stamps: `build_stage1_editor_package.py` → `google-ads-editor-import.csv`
- Vision production host: `www.virtualcoworker.app` (`vision` Vercel project; preview `vision-three-alpha.vercel.app` still exists)
