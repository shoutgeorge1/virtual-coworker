# Virtual Coworker — FULL ChatGPT Debrief (Ads upload · Editor · Launch Control · conversion honesty)

**Paste this whole file into ChatGPT.** Ask it to stress-test honesty, architecture, Final URLs, conversion definitions, LP integrity, Ads package hygiene, isolation from the old account, and launch blockers — not to rewrite ads for vibes.

**Also:** paste `ads-launch/TEAM-UPDATE-EMAIL.md` (or the “Team update” section below) into ChatGPT to polish the stakeholder email George will send — keep the push-forward tone; do not soften into permission-to-stall.

| Field | Value |
|-------|-------|
| Generated | 2026-08-06 (audit + conversion/CRM stack lock + team email) |
| Branch | `vision-demo` |
| Commit SHA | `1a29f08b66da8423d8a60f98f0b2ff36ba82f82d` |
| Repo | `/Users/george/Developer/virtual-coworker` |
| Package | `lp_version=stage1-v7` · Editor hygiene + isolation + Phase 1 manifests |
| Builder | `ads-launch/build_stage1_editor_package.py` |
| Preferred imports | `google-ads-editor-import-us.csv` · `google-ads-editor-import-au.csv` |
| Preflight | `ads-launch/EDITOR-PREFLIGHT-REPORT.md` |
| Decisions | `ads-launch/DECISIONS.md` |
| Team email draft | `ads-launch/TEAM-UPDATE-EMAIL.md` |
| Activation | `ads-launch/PHASED-ACTIVATION.md` · `PHASE1-REVIEW.md` |
| Zoho docs | `ads-launch/zoho/` |
| LP host (production) | **https://www.virtualcoworker.app** (apex → www) |
| LP host (preview) | https://vision-three-alpha.vercel.app (QA only; **not** for Import) |
| Launch Control | **https://vc-xray.vercel.app/launch-control** |
| Ads package overview | **https://vc-xray.vercel.app/ads-package** |
| Corporate WP (untouched) | https://virtualcoworker.com · https://virtualcoworker.com.au |
| MCC | `119-318-9031` (Shout George) |
| Child accounts | USA `496-715-1855` · AU `573-539-1940` |
| Ads enable | **NOT approved** — all CSV entities **Paused** |
| TRAFFIC READY | **Not yet** — durable email/webhook/sheet + responder + live test |
| CRM READY | **Not yet** — Zoho access yes; lead-port path + Recruit vs CRM deferred |
| OPTIMIZATION READY | **Not yet** — build **new** form+phone actions; CallRail ~1–2 mo; offline later |
| Verdict | **SAFE TO IMPORT FOR REVIEW · SAFE TO POST WHILE PAUSED · NOT SAFE FOR PAID TRAFFIC** |

---

## 0. Operating locks (HARD)

| Lock | Rule |
|------|------|
| **Isolation** | Old account = historical archive. New `VC_*` = clean parallel system. Do not dig/delete/rewrite museum tonight. |
| **Brand deferred** | Do not center Stage 1 / checklist / next steps on old Brand remnants. Clean `VC_*` Editor package first. |
| **Ads API** | **Read-only / cheap probes only.** Package work = **Google Ads Editor CSV**. No create/update/enable via API. Stop on quota burn. |
| **Domain** | Production Final URLs = **https://www.virtualcoworker.app** (paths `/us` `/au` `/ph`). Not vision-three-alpha. Not two country domains. |
| **TRAFFIC READY gates** | Durable monitored delivery + live test arrives + named responder + still Paused until George Enable. Zoho **not** required. |
| **CRM READY** | Zoho lead port (API preferred). Recruit vs CRM deferred. No live Zoho write from repo until path locked. |
| **OPTIMIZATION READY** | **New** Ads conversions only — never reuse old account actions. Form→thank-you primary; phone basic; CallRail later; offline via Zoho later. |
| **One inquiry ≠ two Primaries** | Form + Calendly + Zoho offline must not all be Primary for the same event. |
| **Negatives** | Tight VC-only curated campaign negs (~172 unique). **No** mega shared / `PM_*` lists on `VC_*`. |
| **Match** | Positive keywords = **Exact + Phrase only**. Broad rows in CSV = campaign **negatives** (`Negative=True`). |

### Conversion / CRM stack (locked direction — 2026-08-06)

**Do NOT use old account conversions.** Build new, simple:

1. **Form fill → thank-you** (primary online) — employer inquiry + Calendly on thank-you (Calendly = secondary)
2. **Phone call** — basic/click-to-call now; CTA ≠ qualified until CallRail
3. Prefer **direct integrations** over complicated Zapier (document museum Zapier; don’t design around it)
4. **Zoho:** George has access — figure lead port (API preferred). Recruit vs CRM still deferred discovery. Ask VC who owns CRM/admin.
5. **Zoho ↔ Google Ads native** — audit/document; later for qualified lead / job order / placement — **not** duplicate Primary
6. **CallRail** ~1–2 months — not Stage 1 required
7. Offline / higher-value via Zoho **after** basic form + phone exist

---

## 1. Architecture

### Ads (Paused Editor package)

| Campaign | Account | Budget/day | Max CPC | Final URL job |
|----------|---------|----------:|--------:|---------------|
| `VC_US_S_CORE` | 496-715-1855 | $75 | $8 | → `/us` |
| `VC_US_S_ROLES` | 496-715-1855 | $50 | $8 | → `/us/{category}` |
| `VC_AU_S_CORE` | 573-539-1940 | A$75 | A$6 | → `/au` |
| `VC_AU_S_ROLES` | 573-539-1940 | A$50 | A$6 | → `/au/{category}` |

- Search · Maximize Clicks · **Exact + Phrase positives** · Brand **deferred** · all **Paused**
- RSA: **3** unique full RSAs (15H/4D) per main AG; city-test **1**
- Tracking template `{lpurl}` · Final URL suffix ValueTrack UTMs + `lp_version=stage1-v7`
- Max CPC = campaign-only `Maximum CPC bid limit` (blank on child rows)

### Package inventory (verified 2026-08-06)

| Metric | US | AU | Combined |
|--------|---:|---:|---------:|
| CSV rows | 1,230 | 1,230 | 2,460 |
| Account stamp | 496-715-1855 | 573-539-1940 | both |
| Campaigns | 2 | 2 | **4** |
| Ad groups | 20 | 20 | **40** |
| Positive keywords | 784 (Exact 591 · Phrase 193) | 784 | **1,568** |
| RSAs | 58 | 58 | **116** |
| Campaign negative rows | 344 (172 unique) | 344 | **688** (172 × 4) |
| Commercial holdouts (not imported) | — | — | **19** |
| Shared-list / audience / `PM_*` rows | **0** | **0** | **0** |
| Enabled statuses | **0** | **0** | **0** |
| Final URL hosts | **only** `www.virtualcoworker.app` | same | same |
| Broad **positives** | **0** | **0** | **0** |

Phase 1 review manifests (Paused, not enable files): 784 kw/market — Tier 1A 278 · 1B 321 · 2 146 · 3 39.

**Human display names** (dashboard only — Editor entity IDs stay technical): US/AU · Core Search / Role Search; AGs like “Virtual Assistant · Hire”, “Digital Marketing · Outsource”, etc. Source: `build_xray_ads_overview.py` → https://vc-xray.vercel.app/ads-package

### Core AGs (per market)

`Hire_VA_PH` · `Offshore_VA_PH` → Final URL market home (`/us` or `/au`)

### Roles AGs (per market · 18)

Hire/Outsource pairs for: Accounting · Bookkeeping · Digital Marketing · Social Media · Administration/EA · Customer Service · Human Resources · Recruitment · Sales · plus `Admin_City_Test`

Category Final URLs: `/administrative-support` · `/digital-marketing` · `/social-media` · `/accounting` · `/bookkeeping` · `/customer-service` · `/hr` · `/recruitment` · `/sales`  
HR alias: `/{us\|au}/human-resources` → 308 → `/{us\|au}/hr`

Sitelinks include market home, `#gate`, and sample category URLs — all www host. **Zero** WP / vision-three Final URLs in package.

---

## 2. Live LP audit (https://www.virtualcoworker.app — 2026-08-06)

| URL | Result |
|-----|--------|
| `/` | 200 → `/us` |
| apex `virtualcoworker.app` | 308 → www |
| `/us` · `/au` · `/ph` | **200** · hire/job gate present (“I’m hiring…” / “I’m looking for a job”) |
| Sample categories US+AU | **200** |
| `/ph/apply` | **200** |
| `/privacy` · `/terms` · `/thank-you` · `/how-it-works` · `/services` | **200** (root paths — not `/us/privacy`) |
| `/us/human-resources` | 200 → `/us/hr` |
| Thank-you Calendly | US `calendly.com/cheyenne-virtualcoworker/30min` · AU `calendly.com/apac-virtualcoworker/30min` |
| WP egress from microsite | Forbidden by design / CI |

**Note:** `/us/privacy` etc. 404 by design — legal/thank-you live at site root.

Domain ≠ TRAFFIC READY. Ads firing flag still off. Pilot noindex on.

---

## 3. X-ray dashboards (https://vc-xray.vercel.app)

| Page | Check |
|------|-------|
| `/launch-control` | TRAFFIC / CRM / OPTIMIZATION READY cards; domain-before-Enable; Brand deferred; Import≠Post≠Enable; www LP links |
| `/landing-pages` | www host links; preview noted as QA only |
| `/lead-routing` | Zoho ≠ TRAFFIC READY; named responder asks |
| `/tracking` | **New conversion stack** encoded — form→thank-you, phone basic, direct>Zapier, Zoho lead port, native offline later, CallRail ~1–2 mo |
| `/ads-package` | Counts match CSV; host www only; human display names |

Stale link **labels** fixed forward (`project-status` / `us` / `au` now show www text). Preview host may still be mentioned as QA — correct.

---

## 4. What shipped recently (compressed)

- Production domain **www.virtualcoworker.app** + Editor Final URLs regenerated on www  
- Calendly on thank-you (US/AU from live WP)  
- Public LP jargon cleanup (employer sales voice; hiring conversation language)  
- Launch Control checklist rebalance: TRAFFIC READY first; domain before Enable; Brand deferred  
- Ads package overview + human names (`build_xray_ads_overview.py`)  
- Isolation locks: no mega shared negs; VC-only curated  
- Editor P0s: Account stamps, US/AU split CSVs, campaign-only Max CPC, ValueTrack UTMs  
- Ads API editor-only rule (read-only probes; no mutate)  
- Zoho platform discovery deferred (Recruit suspicion; no Leads assumption)  
- Conversion/CRM stack lock (this debrief) + team update email draft  

**Not done (correctly):** Import / Post / Enable · Ads API mutate · live Zoho write · paid traffic

---

## 5. Import instructions (George)

1. Leave old account machinery alone (no museum rewrite binge).  
2. Google Ads Editor → download fresh USA + AU.  
3. Read `EDITOR-PREFLIGHT-REPORT.md`.  
4. **Import US:** `google-ads-editor-import-us.csv` → `496-715-1855`.  
5. **Import AU:** `google-ads-editor-import-au.csv` → `573-539-1940`.  
6. Prefer splits. Multi-account file only for manager import (Account column stamped).  
7. **Import ≠ Post ≠ Enable**  
   - **Import** = local Editor draft only  
   - **Post** = upload to live account — entities stay **Paused**  
   - **Enable** = separate explicit George decision after TRAFFIC READY  
8. Check changes · confirm www Final URLs · confirm curated campaign negs only.  
9. **Do NOT** attach shared mega negative lists.  
10. Post only after review (still Paused).  
11. After Post (Ads UI, OPTIMIZATION path): campaign-specific goals → **only new** actions. Leave old conversions alone.  
12. Stay Maximize Clicks. No Max Conv until new actions verified.  
13. Enable only per `PHASED-ACTIVATION.md` after TRAFFIC READY + explicit OK.

---

## 6. Blockers — NOT SAFE FOR PAID TRAFFIC

| # | Blocker | Gate |
|---|---------|------|
| 1 | No durable production lead path (log-only ≠ ready) | **TRAFFIC READY** |
| 2 | Named responder + live test lead proof | **TRAFFIC READY** |
| 3 | Explicit George Enable approval | **TRAFFIC READY** |
| 4 | Zoho lead-port path TBD (access yes; Recruit vs CRM open) | CRM READY parallel |
| 5 | New Ads conversion actions not built/live | OPTIMIZATION parallel |
| 6 | CallRail / qualified-call | Later (~1–2 mo) |
| 7 | Offline job order / placement values | TBD, not approved |
| 8 | Brand remnants may still trickle | Deferred — don’t center Stage 1 |

**Done / not substitutes for TRAFFIC READY:** www domain · LP 200s · Calendly · Paused Editor package · X-ray checklist

---

## 7. Team update (stakeholder firehose)

Full draft: **`ads-launch/TEAM-UPDATE-EMAIL.md`**

**Paste to ChatGPT to polish the team email** — keep push-forward tone; firehose ownership asks; do not ask permission to stall.

Asks for VC:

- Approve LPs on www (or flag changes)  
- Who answers leads (+ backup)  
- Durable monitored inbox  
- Confirm Calendly US/AU  
- Who owns Zoho/CRM admin + where inquiries should land  
- Optional RSA/creative feedback  

Not happening yet: Enable / paid traffic · Brand focus · old account rewrite · Zoho as traffic gate · CallRail Stage 1

---

## 8. Questions for ChatGPT to stress-test

1. Is Core → `/us`/`/au` correct vs category admin for “hire VA”?  
2. Is log-only acceptable for any paid click? (**Our answer: No.**)  
3. Are Max CPC $8 / A$6 and $75/$50 dailies sane vs historical CPC / $10–20k monthly story?  
4. Is PH long-tail-first activation correct?  
5. Isolation: does Post still risk inheriting account-default goals / shared negs unless George sets campaign-specific goals and refuses shared-list attach?  
6. Conversion stack: any risk of double Primaries (form + Calendly + Zoho offline)?  
7. Is “email/webhook first, Zoho API when product known” the right CRM sequencing?  
8. RSA×3 — invented savings, “top 1%”, SaaS consult language?  
9. Keyword hygiene — job-seeker / medical / Spanish leaks? Bare `hire` negatived by mistake?  
10. What must be true before first $1 of Enable — ordered checklist?  
11. Does the team email ask for the right ownership items without inviting stall?

### Do not invent requirements we never claimed

- Live Zoho writeback / assumed Leads+CRM V8 · CallRail as Stage 1 · WP redesign · Broad/PMax for volume · Fake AU phone · Brand in this CSV · Fake placement guarantees · Offline $ values as approved · Inheritance of 3000+ old negatives · Zoho as TRAFFIC READY gate · Reusing old account conversions

---

## 9. File map

| Path | Purpose |
|------|---------|
| `ads-launch/CHATGPT-DEBRIEF.md` | **This file** — canonical ChatGPT paste |
| `ads-launch/TEAM-UPDATE-EMAIL.md` | Stakeholder email draft |
| `ads-launch/DECISIONS.md` | Locked defaults + conversion/CRM stack + API/Brand locks |
| `ads-launch/EDITOR-PREFLIGHT-REPORT.md` | Import inventory + verdict |
| `ads-launch/PHASED-ACTIVATION.md` | Enable order (PH long-tail first) |
| `ads-launch/build_stage1_editor_package.py` | Builder + QA + CSV writers |
| `ads-launch/google-ads-editor-import-us.csv` | **Preferred** USA import |
| `ads-launch/google-ads-editor-import-au.csv` | **Preferred** AU import |
| `ads-launch/google-ads-editor-import.csv` | Multi-account (= multi twin) |
| `ads-launch/phase1-enable-manifest-{us,au}.csv` | Review-only enable ladder |
| `ads-launch/zoho/DEFERRED-PLATFORM-DISCOVERY.md` | Zoho product/API later |
| `vision/` | Next.js hiring microsite |
| `xray/launch-control.html` | Operator checklist |
| `xray/tracking.html` | Conversion / bidding ladder |
| `xray/ads-package.html` | Package overview UI |
| `xray/docs/ads-launch/*` | Mirrored docs for xray host |

Rebuild CSVs: `python3 ads-launch/build_stage1_editor_package.py`  
Rebuild ads overview: `python3 ads-launch/build_xray_ads_overview.py`

---

## 10. Conversion honesty

```
Ad click
  → employer_inquiry_submitted   (= server-accepted + durably delivered)
  → human follow-up
  → job order                    (CRM — not wired)
  → placement                    (ops — not wired)

form submit ≠ job order ≠ placement
log_only accept ≠ employer_inquiry_submitted
phone_cta_clicked ≠ qualified call
Calendly book ≠ replace primary inquiry
Editor "Conversions" / old Zoho/Zapier ≠ truth for VC_*
ZOHO_WEBHOOK_URL success ≠ Zoho CRM sync
```

---

## 11. Verdict

```
SAFE TO IMPORT INTO EDITOR FOR REVIEW
SAFE TO POST WHILE PAUSED (after Editor review — still Paused)
NOT SAFE FOR PAID TRAFFIC (TRAFFIC READY incomplete)
ADS REMAIN OFF
OLD ACCOUNT = ARCHIVE (do not rewrite tonight)
NEW VC_* = ISOLATED CLEAN SYSTEM (Paused)
BRAND = DEFERRED
ADS API = READ-ONLY / EDITOR BUILDS ONLY
CRM READY / OPTIMIZATION READY = PARALLEL (not traffic gates)
ZOHO = ACCESS YES · LEAD PORT TBD · NO LIVE WRITE YET
CONVERSIONS = BUILD NEW (form→thank-you · phone basic · offline later)
```

Operator next: clear **TRAFFIC READY** (inbox · test · named responder). Send team email for LP approval + lead ownership + Zoho/CRM owner. Import www CSVs for review when ready — still don’t Enable until TRAFFIC READY.

---

*End of FULL ChatGPT debrief. Canonical paste. Team email: `TEAM-UPDATE-EMAIL.md`. Preflight: `EDITOR-PREFLIGHT-REPORT.md`. Decisions: `DECISIONS.md`.*
