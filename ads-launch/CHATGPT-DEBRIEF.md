# Virtual Coworker — FULL ChatGPT Debrief (Ads upload · Editor · Launch Control · conversion honesty)

**Paste this whole file into ChatGPT.** Ask it to stress-test honesty, architecture, Final URLs, conversion definitions, LP integrity, Ads package hygiene, isolation from the old account, and launch blockers — not to rewrite ads for vibes.

| Field | Value |
|-------|-------|
| Generated | 2026-08-06 (Zoho platform-discovery deferred addendum) |
| Branch | `vision-demo` |
| Commit SHA | _(set after commit)_ |
| Prior isolation SHA | `7b703c5` · Editor P0 `9cd37d0` |
| Repo | `/Users/george/Developer/virtual-coworker` |
| Package | `lp_version=stage1-v7` · Editor hygiene + isolation + Phase 1 manifests |
| Builder | `ads-launch/build_stage1_editor_package.py` |
| Preferred imports | `google-ads-editor-import-us.csv` · `google-ads-editor-import-au.csv` |
| Preflight | `ads-launch/EDITOR-PREFLIGHT-REPORT.md` |
| Decisions | `ads-launch/DECISIONS.md` |
| Activation | `ads-launch/PHASED-ACTIVATION.md` · `PHASE1-REVIEW.md` |
| Zoho docs | `ads-launch/zoho/` |
| Mega prompt source | `ads-launch/VC-CURSOR-MEGA-PROMPT-EDITOR-ZOHO.md` |
| LP host (preview) | **https://vision-three-alpha.vercel.app** |
| Launch Control | **https://vc-xray.vercel.app/launch-control** |
| Corporate WP (untouched) | https://virtualcoworker.com · https://virtualcoworker.com.au |
| MCC | `119-318-9031` (Shout George) |
| Child accounts | USA `496-715-1855` · AU `573-539-1940` |
| Ads enable | **NOT approved** — all CSV entities **Paused** |
| TRAFFIC READY | **Not yet** — need durable email/webhook/sheet + responder + live test |
| CRM READY | **Not yet** — platform discovery **deferred**; no Leads in UI; do not assume CRM V8 |
| OPTIMIZATION READY | **Not yet** — GTM/new Ads actions/goals parallel |
| Verdict | **SAFE TO IMPORT INTO EDITOR FOR REVIEW · SAFE TO POST WHILE PAUSED · NOT SAFE FOR PAID TRAFFIC** |

---

## 0. Launch sequencing (LOCKED addendum)

**Zoho (any product) / native Ads connector / offline conversions / Ads API are NOT prerequisites for initial Maximize Clicks Enable.**

| Status | Gate |
|--------|------|
| **TRAFFIC READY** | Durable monitored email/webhook/sheet (not log-only) + live test arrives + named responder + form retains market/UTMs/click IDs/submission id + US/AU routing + still Paused until George Enable |
| **CRM READY** | Direct Zoho record + verified field mapping — **parallel · deferred** until product/API known |
| **OPTIMIZATION READY** | GTM → new Ads conversions, campaign-specific goals, downstream CRM feedback — **parallel** |

Keep Max Clicks · Exact+Phrase · Tier 1A then 1B · no Broad+/PMax/DSA/Max Conv until optimization is real.

### Zoho platform discovery — **DEFERRED** (George UI observation)

| Finding | Lock |
|---------|------|
| No visible **Leads**; can start module exports; no full Data Backup | Prefer minimal exports; do not hardcode Leads |
| Visible: Accounts, Contacts, Job Orders, Placements, Campaigns, Calls, Meetings, Notes, Competitors | Inspect employer spine Account → Contact → Job Order → Placement |
| May be Zoho Recruit **or** heavily customized CRM | Do **not** assume CRM API V8 |
| Live inventory + API implementation | Labeled **deferred** — see `ads-launch/zoho/DEFERRED-PLATFORM-DISCOVERY.md` |
| Native Google Ads integration audit | Separate; do **not** assume it needs George’s pending Ads developer token |
| Max Clicks | Zoho/API stays parallel — **not** a TRAFFIC READY blocker if durable delivery + test + named responder verified |

Later-phase checklist (do not execute from this debrief): identify product/org → choose Recruit API V2 or CRM API V8 → inventory modules/layouts/fields/ownership/workflows → decide inquiry entry module → minimal exports (Accounts/Contacts/Job Orders/Placements only) → exclude Candidates/Notes/Calls/Meetings/emails/attachments unless later necessary → least-privilege auth instructions **after** platform ID.

---

## 1. Operating rule (locked tonight)

**Old account = historical archive. New `VC_*` campaigns = isolated clean system.**

| DO | DO NOT |
|----|--------|
| Import / review / Post **new paused `VC_*` only** | Dig / delete / rewrite / pause binge on old account-wide machinery tonight |
| Attach **tight curated** campaign negatives from Stage 1 builder (~175 unique, soft cap 220) | Inherit account shared / `PM_*` mega negative lists (3000+ dumps) onto `VC_*` |
| Plan **new** Ads conversion actions via **new** per-market GTM | Touch / replace / delete old Zoho/Zapier conversion actions or historical reporting |
| Set **campaign-specific goals** on each `VC_*` after Post (Ads UI) | Let `VC_*` optimize toward account-default junk conversion baskets |
| Keep audiences **off** for initial Search (Observation later) | Use audiences to restrict targeting at launch |
| Ignore customer-lifecycle / audience warnings until Zoho/first-party data | Treat those warnings as launch blockers |
| Keep every `VC_*` **Paused** — Import ≠ live | Enable / unpause from CSV or Import/Post alone |

**Plain English:** Leave the historical shit alone. Ship a clean parallel system. Do not “fix” the museum by inheriting its negatives, conversions, or goal baskets.

Sources: `DECISIONS.md` · `EDITOR-PREFLIGHT-REPORT.md` · builder isolation QA.

---

## 2. Accounts / money / access

| Item | Value |
|------|-------|
| MCC | `119-318-9031` |
| USA | `496-715-1855` |
| AU | `573-539-1940` |
| Access | Standard via MCC — enough for Stage 1 Editor import/review |
| Bid strategy | Maximize Clicks |
| Max CPC (campaign-only `Maximum CPC bid limit`) | US **$8** · AU **A$6** |
| Daily budgets | Core **$75 / A$75** · Roles **$50 / A$50** → **$125 / A$125 per day** ≈ **$3.8k / A$3.8k mo** Stage 1 pace (placeholders inside a $10–20k/account monthly story) |
| Phone US | **310-426-8776** (`NEXT_PUBLIC_US_PHONE`) |
| Phone AU | **None** — form-primary (no fake AU number) |
| Legacy live spenders (outside this CSV) | `PM_US_RSA_Brand` · `PM_AU_RSA_Brand` may still spend — pause decision separate; **do not rewrite old account tonight** |

**ADS REMAIN OFF.** Not **TRAFFIC READY** until durable lead delivery exists (real email/webhook/sheet — not log-only) + named responder + live test. Zoho CRM is **not** this gate.

---

## 3. Architecture shipped

### Ads (Paused Editor package)

| Campaign | Account | Budget/day | Max CPC | Final URL job |
|----------|---------|----------:|--------:|---------------|
| `VC_US_S_CORE` | 496-715-1855 | $75 | $8 | → `/us` market employer home |
| `VC_US_S_ROLES` | 496-715-1855 | $50 | $8 | → `/us/{category}` |
| `VC_AU_S_CORE` | 573-539-1940 | A$75 | A$6 | → `/au` market employer home |
| `VC_AU_S_ROLES` | 573-539-1940 | A$50 | A$6 | → `/au/{category}` |

- Search · **Exact + Phrase only** · Brand **deferred** · all entities **Paused**
- Package counts (current): **4** campaigns · **40** AGs · **1,568** positives (Exact 1,182 · Phrase 386) · **116** RSAs · **688** campaign-neg rows (**172** unique × 4) · **19** commercial holdouts not imported · Phase 1 manifests 784 kw/market · **0** shared-list / audience / `PM_*` rows
- RSA rule: **3 unique full RSAs (15H/4D) per main AG**; city-test **1**
- Tracking template: `{lpurl}` · Final URL suffix once with ValueTrack UTMs + `lp_version=stage1-v7`

### Phase 1 activation (enable order — not enable approval)

Source: `PHASED-ACTIVATION.md`

1. **PH / Filipino / offshore long-tail first** (Exact + tight Phrase) across Core **and** Roles — books/accounting OK when PH-shaped  
2. Broader category Exact/Phrase without PH geo  
3. Generic Core heads later (tighter CPC)  
4. US before AU · Brand deferred · never Broad/PMax/DSA/WP Final URLs

### Microsite (three separate identities)

| Surface | Role |
|---------|------|
| US employer `/us` + `/us/*` | Primary PPC micro-site |
| AU employer `/au` + `/au/*` | Separate AU employer micro-site |
| PH talent `/ph` (+ `/ph/apply`) | Careers — **never** employer conversion |
| Root `/` | Redirects → `/us` |
| WordPress | **Untouched** — zero egress from microsite nav/footer/CTAs |

- Preview: https://vision-three-alpha.vercel.app  
- Launch Control: https://vc-xray.vercel.app/launch-control  
- Hire-vs-job gate intentional: employer → form; job seeker → `/ph`  
- Tracking env placeholders: `NEXT_PUBLIC_GTM_US` / `_AU` / `_PH` (+ GA4 twins) — do **not** share one GTM across US+AU  
- Ads conversion firing: `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false`  
- Pilot: `NEXT_PUBLIC_PILOT_NOINDEX=true`

### Conversion honesty (locked — do not inflate)

```
Ad click
  → employer_inquiry_submitted   (= server-accepted + durably delivered employer inquiry)
  → human follow-up
  → job order                    (CRM — not wired)
  → placement                    (ops — not wired)

form submit ≠ job order ≠ placement
log_only accept ≠ employer_inquiry_submitted
phone_cta_clicked ≠ qualified call
Editor "Conversions" / "All conv" ≠ job orders
ZOHO_WEBHOOK_URL success ≠ Zoho CRM sync
```

Historical Ads “Conversions” in exports are **not** proof of placements.

---

## 4. Mega prompt P0s executed

Source prompt: `ads-launch/VC-CURSOR-MEGA-PROMPT-EDITOR-ZOHO.md`  
Shipped in commit `9cd37d0` — *Fix Editor import hygiene from mega prompt P0s.*  
Isolation locks shipped in commit `7b703c5` (see §5).

### Shipped (done)

| P0 | What |
|----|------|
| **Account routing** | Every row stamps `Account` = USA `496-715-1855` / AU `573-539-1940` |
| **US/AU split CSVs** | Preferred: `google-ads-editor-import-us.csv` · `…-au.csv` (1236 rows each) |
| **Multi-account CSV** | `google-ads-editor-import.csv` ≡ `…-multi-account.csv` (2472 rows) — manager import only |
| **Max CPC fix** | Campaign-only `Maximum CPC bid limit` (US 8 / AU 6); blank on child rows; old misused `Max CPC` removed |
| **ValueTrack UTMs** | Suffix uses `{campaignid}` `{adgroupid}` `{keyword}` `{matchtype}` `{device}` — **no** undefined `{_campaign}` / `{_adgroup}` |
| **Template** | `{lpurl}` only — no double UTM |
| **Commercial neg holdouts** | 16 terms held out of import (cost/review/pricing/cheap/filipina va etc.) — see preflight |
| **Preflight report** | `EDITOR-PREFLIGHT-REPORT.md` — SAFE TO IMPORT FOR REVIEW · IMPORT/POST/ENABLE NOT PERFORMED |
| **LC import copy** | Step 13 points at split files + Import≠Post≠Enable |
| **Webhook ≠ CRM honesty** | `vision/lib/lead-delivery.ts` documents channel `"zoho"` = generic `ZOHO_WEBHOOK_URL` POST, not CRM API |
| **Zoho gitignore** | `.local/zoho/` ignored — raw backups/PII never commit |
| **Account column stamp** | Earlier `8a3477e` + reinforced in P0 |
| **Plain-English LC** | `7be9f73` · account hygiene / Zapier audit steps `b741d6c` |
| **PH long-tail activation lock** | `544c127` · `PHASED-ACTIVATION.md` |
| **v7 Core→market home** | `7cf6ada` / `26bc35a` — Core Final URL `/us`/`/au` not administrative-support |

### Deliberately skipped / not complete (mega prompt Workstream D+)

| Item | Status |
|------|--------|
| Full Zoho API adapter (`vision/lib/zoho/*`) | **Deferred for live use** — CRM V8 stubs feature-flagged; product/API unknown; no live write |
| Zoho OAuth bootstrap + inventory (`npm run zoho:*`) | **Deferred** — CRM V8–oriented stubs; run only after platform discovery |
| Platform discovery runbook | **Shipped (docs)** — `ads-launch/zoho/DEFERRED-PLATFORM-DISCOVERY.md` |
| Native Zoho ↔ Google Ads audit doc | **Checklist shipped** — observe only; ≠ Ads developer token; do not authorize from repo |
| Offline conversion uploader / Data Manager path | **Skipped / planned later** — values TBD, not approved; not TRAFFIC READY |
| Phase 1 keyword review manifests | **Shipped** — `phase1-enable-manifest-{us,au}.csv` + `PHASE1-REVIEW.md` |
| Public-copy lint + commercial neg holdouts (pay/hourly rate, VA reviews) | **Shipped** |
| Standalone `validate_editor_package.py` | **Skipped** — QA lives inside builder `qa()` |
| Live OAuth / Ads API / Post / Enable / deploy / live Zoho write | **Forbidden** — not done |

---

## 5. Isolation repair (George’s latest instruction)

**Instruction:** Leave historical account alone. New campaigns = clean system. Own tight negatives only. New GTM conversion actions. Campaign-specific goals. Leave old conversions untouched. Audiences Observation later. Ignore customer-lifecycle warnings. All new campaigns Paused.

### Done (code + docs — commit `7b703c5`)

| Change | Where |
|--------|-------|
| Operating rule table locked | `DECISIONS.md` |
| Builder header: emit only VC_* + curated campaign negs; never shared mega lists | `build_stage1_editor_package.py` |
| `MAX_UNIQUE_NEGATIVES = 220` soft cap + QA fail if exceeded | builder |
| Isolation QA: forbid shared-list / audience / `PM_*` row types | builder `qa()` |
| Neg comment stamps “VC-only curated… NOT account shared” | builder |
| Preflight sections: operating rule, conversion goals after Post, audiences, operator path “do not attach shared lists” | `EDITOR-PREFLIGHT-REPORT.md` |
| Current package: **175** unique campaign negs (tight curated + holdouts) — **not** 3000+ inheritance | CSVs |

### Pending / partial

| Item | Status |
|------|--------|
| Launch Control checklist language for isolation + sequencing | **Updated** — steps 6–10 museum-safe; three statuses TRAFFIC/CRM/OPTIMIZATION READY; step 10 = do not attach shared mega lists |
| Campaign-specific goals in live Ads UI | **Operator after Post** — CSV cannot express; documented in preflight |
| New GTM → new Ads conversion actions | **Not built live** — plan only; firing flag false |
| Pause legacy `PM_*` Brand | **George decision in Ads UI** — outside CSV; do not binge-rewrite museum tonight |

---

## 6. Import instructions for George

1. Leave old account machinery alone tonight (no delete/rewrite/global pause binge).  
2. Open Google Ads Editor → download fresh USA + AU (sync).  
3. Read `ads-launch/EDITOR-PREFLIGHT-REPORT.md`.  
4. **Import US:** `ads-launch/google-ads-editor-import-us.csv` → account `496-715-1855`.  
5. **Import AU:** `ads-launch/google-ads-editor-import-au.csv` → account `573-539-1940`.  
6. Prefer splits. Use `google-ads-editor-import-multi-account.csv` / `google-ads-editor-import.csv` only for manager multi-account import (every row has Account).  
7. **Import ≠ Post ≠ Enable**  
   - **Import** = local Editor draft only — does **not** change live Ads  
   - **Post** = uploads to live account — entities stay **Paused**  
   - **Enable** = separate explicit George decision after gates green  
8. Run Editor **Check changes**. Review while **Paused**.  
9. Confirm negatives on `VC_*` are campaign-level curated only.  
10. **Do NOT attach** old shared / `PM_*` mega negative lists to `VC_*`.  
11. Post only after review (still Paused).  
12. **After Post (Ads UI):** each `VC_*` → Goals → **campaign-specific** → only **new** actions (employer inquiry delivered + qualified phone ~60s when ready). Leave old Zoho/Zapier actions untouched for archive.  
13. Keep Maximize Clicks. Do **not** switch to Max Conversions until new actions verified.  
14. Audiences off. Ignore customer-lifecycle warnings.  
15. Enable only per `PHASED-ACTIVATION.md` after durable leads + explicit approval.

---

## 7. Honest blockers

| # | Blocker | Notes |
|---|---------|-------|
| 1 | **No durable production lead path** | **TRAFFIC READY** hard gate. `ALLOW_LOG_ONLY_LEADS=true` = blocked (`conversion_eligible: false`). |
| 2 | **Named responder + live test lead** | **TRAFFIC READY** — who answers + proof a test arrives |
| 3 | **Explicit George Enable approval** | Required even when TRAFFIC READY |
| 4 | **Legacy Brand bleed** | `PM_*` Brand may still spend — separate UI decision |
| 5 | **Zoho access ≠ CRM READY** | Parallel + **deferred** discovery (Recruit vs CRM; no Leads). Webhook ≠ API. Not a traffic blocker. |
| 6 | **Zapier weird** | Document; don’t rip blind. Not a traffic blocker if durable email/webhook exists. |
| 7 | **Job order / placement offline values** | TBD, not approved. OPTIMIZATION / CRM later. |
| 8 | CallRail / qualified-call | Later; phone click ≠ qualified |
| 9 | GTM → Ads mapping tested | OPTIMIZATION READY; firing still off |
| 10 | US + AU custom paid domains | Nice-to-have; preview host OK for TRAFFIC READY |

---

## 8. File map

| Path | Purpose |
|------|---------|
| `ads-launch/CHATGPT-DEBRIEF.md` | **This file** — canonical ChatGPT paste |
| `ads-launch/DECISIONS.md` | Locked operator defaults + isolation rule |
| `ads-launch/EDITOR-PREFLIGHT-REPORT.md` | Import inventory + verdict |
| `ads-launch/PHASED-ACTIVATION.md` | Enable order (PH long-tail first) |
| `ads-launch/VC-CURSOR-MEGA-PROMPT-EDITOR-ZOHO.md` | Mega prompt that drove Editor/Zoho P0s |
| `ads-launch/zoho/DEFERRED-PLATFORM-DISCOVERY.md` | Later-phase Zoho product/API discovery + audit |
| `ads-launch/build_stage1_editor_package.py` | Builder + QA + CSV writers |
| `ads-launch/google-ads-editor-import-us.csv` | **Preferred** USA import |
| `ads-launch/google-ads-editor-import-au.csv` | **Preferred** AU import |
| `ads-launch/google-ads-editor-import.csv` | Multi-account (= multi-account twin) |
| `ads-launch/google-ads-editor-import-multi-account.csv` | Same as combined; manager-only |
| `ads-launch/TONIGHT-HANDOFF.md` | Earlier Account-column handoff note |
| `ads-launch/LAUNCH-SHEET.md` | Short launch sheet (some counts may lag; trust preflight) |
| `ads-launch/12-blocker-decision-list.md` | Blocker table |
| `ads-launch/10-tracking-event-spec.md` | Event definitions |
| `ads-launch/06-stage1-campaign-architecture.md` | Architecture notes |
| `ads-launch/07-phased-activation-recommendation.md` | Short activation checklist |
| `ads-launch/09-ads-human-review-matrix.md` | Human review matrix |
| `ads-launch/FULL-BUILD-REPORT.md` | Short index |
| `ads-launch/CHATGPT-MEGA-AUDIT.md` | Older deep companion (this debrief supersedes for tonight) |
| `ads-launch/historical-performance-summary.json` | ~2y ST machine summary |
| `vision/` | Next.js hiring microsite |
| `vision/lib/lead-delivery.ts` | Honest delivery channels; webhook≠CRM |
| `vision/lib/no-wp-links.test.ts` | WP egress CI |
| `vision/config/categories.ts` | Category copy + A/B |
| `xray/launch-control.html` | Operator checklist UI |
| `xray/docs/ads-launch/*` | Mirrored CSV/docs for xray host |

Rebuild: `python3 ads-launch/build_stage1_editor_package.py`

---

## 9. Conversion / microsite honesty detail

### Events (dataLayer / GTM-ready; Ads firing off)

| Event | Meaning |
|-------|---------|
| `employer_gate_selected` | Chose employer |
| `employer_form_started` | First form interaction |
| `employer_form_validation_error` | Client validation fail |
| `employer_inquiry_submitted` | **Server accepted + durable delivery** (candidate primary) |
| `employer_inquiry_submitted_deduped` | Refresh-safe block |
| `employer_inquiry_delivery_failed` | 502/503 / network |
| `employer_inquiry_log_only` | Log-only blocked mode (never primary) |
| `phone_cta_clicked` | tel: click — `is_qualified_call: false` |
| `job_seeker_redirected` | Divert to `/ph` — never primary Ads conv |

### Category LPs (Roles Final URLs)

digital-marketing · social-media · accounting · bookkeeping · administrative-support · customer-service · hr · recruitment · sales  
HR alias: `/{us|au}/human-resources` → 308 `/{us|au}/hr`

### Prior fuck-ups → fixed (compressed)

Double UTM · inert `?role=` URLs · boilerplate RSAs · fake AU phone · consult/demo SaaS language · plastic heroes · silent log-only as conversion · Core→admin mismatch → Core→market home · 22-campaign sprawl → 2/account · Account column missing → stamped · undefined `{_custom}` UTMs → ValueTrack · Max CPC on every row → campaign-only bid limit · commercial research negs → holdouts · isolation: no mega-list inheritance.

---

## 10. Historical evidence (context only — not conversion truth)

Sources: Editor exports ~2024-08-01 → 2026-08-04. Summary: `historical-performance-summary.json`

| Account | Cost | Clicks | Ads “Conversions” | Note |
|---------|-----:|-------:|------------------:|------|
| USA | ~$724k | ~87k | ~2.6k | Inflated vs placements |
| AU | ~$457k | ~49k | ~1.4k | Same caveat |

Informs keywords/negatives/RSA angles. Does **not** prove microsite ROI. Do not rewrite old conversions to “fix” history.

---

## 11. Recent git spine (vision-demo)

```
7b703c5 Lock VC_* isolation and ship full ChatGPT debrief.
9cd37d0 Fix Editor import hygiene from mega prompt P0s.
7be9f73 Rewrite Launch Control in plain PPC English.
b741d6c Add account hygiene and Zapier audits to Launch Control.
8a3477e Stamp Editor Account IDs and add Zoho offline checklist.
544c127 Lock PH long-tail first for Stage 1 activation.
26bc35a Stabilize Stage 1 v7 for review…
8bd8fe7 Sync xray Launch Control + docs mirrors to v7 Core→market-home.
7cf6ada Finalize v7 Core→market-home routing and honest conversion contract.
```

---

## 12. Questions for ChatGPT to stress-test

1. Is Core → `/us`/`/au` correct vs category admin for “hire VA”?  
2. Is log-only acceptable for any paid click? (**Our answer: No.**)  
3. Are Max CPC $8 / A$6 and $75/$50 dailies sane vs historical CPC / $10–20k monthly story?  
4. Is PH long-tail-first activation correct vs old “Core + Digital/Social/Admin only”?  
5. Isolation: any risk that Post still inherits account-default goals / shared negatives unless George sets campaign-specific goals and refuses shared-list attach?  
6. RSA×3 — invented savings, “top 1%”, consult language, clone-y noun swaps?  
7. Keyword hygiene — job-seeker / medical / Spanish / competitor leaks? Bare `hire` negatived by mistake?  
8. Double UTM / WP Final URL regressions?  
9. Webhook-labeled-as-zoho confusion risk for paid readiness?  
10. What must be true before first $1 of Enable — ordered checklist?

### Do not invent requirements we never claimed

- Live Zoho writeback / assumed Leads+CRM V8 · CallRail qualified calls · WP redesign · Broad/PMax for volume · Fake AU phone · Brand Search in this CSV · Fake placement guarantees · Offline $ values as approved · Inheritance of 3000+ old negatives as “best practice” · Zoho as TRAFFIC READY gate

---

## 13. Verdict

```
SAFE TO IMPORT INTO EDITOR FOR REVIEW
SAFE TO POST WHILE PAUSED (after Editor review — still Paused)
NOT SAFE FOR PAID TRAFFIC (TRAFFIC READY incomplete)
ADS REMAIN OFF
OLD ACCOUNT = ARCHIVE (do not rewrite tonight)
NEW VC_* = ISOLATED CLEAN SYSTEM (Paused)
CRM READY / OPTIMIZATION READY = PARALLEL (not traffic gates)
ZOHO PLATFORM DISCOVERY + LIVE INVENTORY/API = DEFERRED
```

Operator next: Import split CSVs → review Paused → Post Paused → clear **TRAFFIC READY** (durable channel + test + responder) → Enable Tier 1A/1B only with explicit George OK. Campaign-specific goals + Zoho discovery = parallel later.

---

*End of FULL ChatGPT debrief. Canonical paste for tonight. Companion history: `CHATGPT-MEGA-AUDIT.md`. Index: `FULL-BUILD-REPORT.md`. Preflight: `EDITOR-PREFLIGHT-REPORT.md`.*
