# Virtual Coworker Stage 1 — Complete ChatGPT Debrief (v7 · Core→market home)

**Paste this whole file into ChatGPT.** Ask it to stress-test honesty, architecture, Final URLs, conversion definitions, LP integrity, Ads package hygiene, and launch blockers — not to rewrite ads for vibes.

| Field | Value |
|-------|-------|
| Date | 2026-08-05 |
| Branch | `vision-demo` |
| Repo | `/Users/george/Developer/virtual-coworker` |
| Package | `ads-launch/google-ads-editor-import.csv` · `lp_version=stage1-v7` |
| Builder | `ads-launch/build_stage1_editor_package.py` |
| Decisions | `ads-launch/DECISIONS.md` |
| Short index | `ads-launch/FULL-BUILD-REPORT.md` |
| Deep companion | `ads-launch/CHATGPT-MEGA-AUDIT.md` (points here as canonical) |
| LP host (preview) | **https://vision-three-alpha.vercel.app** |
| Launch Control | **https://vc-xray.vercel.app/launch-control** |
| Corporate WP (untouched) | https://virtualcoworker.com · https://virtualcoworker.com.au |
| Accounts | USA `496-715-1855` · AU `573-539-1940` |
| Ads enable | **NOT approved** — all CSV entities **Paused** |
| Paid status | **NOT READY FOR PAID TRAFFIC** (no durable lead delivery) |
| RSA rule (locked) | **3 unique full RSAs (15H/4D) per main AG**; city-test 1 |

---

## 1. Project goal / business model

Virtual Coworker is a **staffing partner**: US/AU employers hire dedicated Philippines-based teammates (VA, marketing, social, books, CS, sales, etc.). We recruit, vet, and shortlist; the employer interviews and decides.

**Paid Stage 1 goal:** Route high-intent Google Search traffic to a **new Next.js microsite** (not WordPress), capture **employer hiring inquiries**, and learn which RSA angles win — without pretending a form submit is revenue.

### Conversion truth (locked — do not inflate)

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
```

Historical Ads “Conversions” in exports are **not** proof of placements. Stage 1 tracking names match this honesty.

---

## 2. Architecture: three micro-sites (not a hub + WP)

| Surface | Role |
|---------|------|
| **US employer** `/us` + `/us/*` | Primary PPC micro-site |
| **AU employer** `/au` + `/au/*` | Separate AU employer micro-site |
| **PH talent** `/ph` (+ `/ph/apply`) | Separate careers micro-site — **never** employer conversion |
| **Root `/`** | **Redirects → `/us`** (no multi-market “choose your adventure” hub) |
| **WordPress** virtualcoworker.com / .com.au | **Untouched** — **zero egress** from microsite nav/footer/CTAs |
| **Launch Control** vc-xray | Operator dashboard / X-ray / launch checklist |

**Hard rule — no WordPress egress:** Privacy/Terms are local `/privacy` and `/terms` only. Soft cross-links stay inside US ↔ AU ↔ PH microsite routes. PPC traffic must not leak to WP. Automated audit: `vision/lib/no-wp-links.test.ts` (+ `npm run audit:wp-links`).

**Tracking separation:** three identities — `NEXT_PUBLIC_GTM_US` / `_AU` / `_PH` (+ GA4 twins). dataLayer always carries `market` / `site_surface` (`us` \| `au` \| `ph`). Do **not** assume one shared GTM for everything. Legacy `NEXT_PUBLIC_GTM_ID` is US-only fallback.

### Domains + measurement infra (ops implication)

| Identity | Custom domain | GTM | GA4 | Search Console | Ads conversions |
|----------|---------------|-----|-----|----------------|-----------------|
| **US employer** | Buy on Vercel (~$10) — attach to vision US | Separate container | Separate property | Separate property on US domain | Point at US microsite events only |
| **AU employer** | Buy on Vercel (~$10) — separate from US | Separate container | Separate property | Separate property on AU domain | Point at AU microsite events only |
| **PH talent** | **Can wait** — no Stage 1 domain required | Optional later (`GTM_PH`) | Optional later | Optional later | Never employer conversions |

**Implication:** three microsite identities ⇒ **do not share one GTM/GA4 across US+AU**. Wire env placeholders after containers exist. Launch Control checklist steps 7–11 cover buy domains + stand up measurement. Preview host until domains attach: `vision-three-alpha.vercel.app`.

Microsite is an **independent paid hiring path** with employer gate, category LPs, A/B variants, sticky CTA, optional exit-intent (flag), honest events, and pilot `noindex`.

---

## 3. Live URLs (everything ChatGPT should open)

### Control / ops

| Page | URL |
|------|-----|
| Launch Control | https://vc-xray.vercel.app/launch-control |
| Root (→ US) | https://vision-three-alpha.vercel.app/ → `/us` |
| Services (market-scoped) | https://vision-three-alpha.vercel.app/services?market=us |
| How it works (market-scoped) | https://vision-three-alpha.vercel.app/how-it-works?market=us |
| Privacy (microsite) | https://vision-three-alpha.vercel.app/privacy |
| Terms (microsite) | https://vision-three-alpha.vercel.app/terms |
| Thank you | https://vision-three-alpha.vercel.app/thank-you |
| Careers (PH) | https://vision-three-alpha.vercel.app/ph |
| Careers apply | https://vision-three-alpha.vercel.app/ph/apply |

### Market homes (three sites) — **Core Ads Final URLs**

| Market | Home (Core Final URL) | Gate deep-link |
|--------|----------------------|----------------|
| US | https://vision-three-alpha.vercel.app/us | https://vision-three-alpha.vercel.app/us#gate |
| AU | https://vision-three-alpha.vercel.app/au | https://vision-three-alpha.vercel.app/au#gate |
| PH | https://vision-three-alpha.vercel.app/ph | https://vision-three-alpha.vercel.app/ph/apply |

### Category LPs (9 × 2 markets) — Roles Ads Final URLs

| Category slug | US | AU |
|---------------|----|----|
| digital-marketing | …/us/digital-marketing | …/au/digital-marketing |
| social-media | …/us/social-media | …/au/social-media |
| accounting | …/us/accounting | …/au/accounting |
| bookkeeping | …/us/bookkeeping | …/au/bookkeeping |
| administrative-support | …/us/administrative-support | …/au/administrative-support |
| customer-service | …/us/customer-service | …/au/customer-service |
| hr | …/us/hr | …/au/hr |
| recruitment | …/us/recruitment | …/au/recruitment |
| sales | …/us/sales | …/au/sales |

**HR alias:** `/{us\|au}/human-resources` → **308** `/{us\|au}/hr` (preserves GCLID/WBRAID/GBRAID/UTMs/variant).

### A/B + compat

| Mechanism | Spec |
|-----------|------|
| Cookie | `vc_ab_variant` = `a` \| `b` |
| QA override | `?variant=a` or `?variant=b` on any market/category URL |
| Differs | H1, subhead, primary CTA, hero image (per `vision/config/categories.ts`) |
| Legacy query | `/us?role=bookkeeping` → **308** `/us/bookkeeping` (middleware) |
| Legacy consult | `/us/consult`, `/au/consult` → gate / hiring path (compat) |

### Ads Final URL mapping (v7 — corrected)

| Campaign | Final URL pattern |
|----------|-------------------|
| `VC_*_S_CORE` | `…/{us\|au}` — **market employer home** (NOT administrative-support) |
| `VC_*_S_ROLES` | Matching category slug per role AG |
| Brand | **Deferred** — no Brand campaign in CSV |

Tracking template: `{lpurl}` only.  
Final URL suffix (once): UTMs + `lp_version=stage1-v7`. **No double UTM.**

---

## 4. Microsite product surface

### Casting / heroes

- Filipino aspirational brand assets (prod casting commit `8705ff0`).
- Plastic / white-HR stock heroes **killed**.
- Category A/B heroes pull from `/brand/*` (va-ph, talent-john, support, face series, etc.).

### Nav / footer / IA (three micro-sites)

- **`/` → `/us`** (primary paid market). No corporate hub.
- **Market-scoped nav:** US pages = Services · How it works · Start hiring (US only). AU same for AU. PH = Careers · Apply. **Not** “US · AU · Careers” as peer equals.
- **Footer:** market address/phone · local Privacy/Terms · soft cross-links only (US↔AU↔PH). **Zero WP links. Zero dead links.**
- Trust quotes: published client wording as text — **no WP deep-links**
- Shared content routes: `/services?market=us|au`, `/how-it-works?market=us|au`, `/privacy`, `/terms`

### Conversion tools (employer microsites only)

| Tool | Spec |
|------|------|
| Gate + form | Employer vs job seeker → `/ph` divert (internal) |
| Phone CTA | US only (`310-426-8776`) |
| Sticky mobile CTA | Form (+ phone on US) |
| Exit-intent / timed soft offer | **Off** unless `NEXT_PUBLIC_ENABLE_EXIT_INTENT=true`; once/session; **never on `/ph`** |
| Fake live chat | **Disabled** — no delivery owner |
| Events | See §4 events table |

### Gate / form / phone

| Item | Spec |
|------|------|
| Gate | Employer vs job seeker → job seekers divert to `/ph` (no employer conversion) |
| Form | Employer hiring inquiry → `/api/lead` |
| US phone | **310-426-8776** (`NEXT_PUBLIC_US_PHONE`) |
| AU phone | **None** — form-primary (no fake AU number) |
| Lead delivery | **Hard blocker for paid.** `ALLOW_LOG_ONLY_LEADS=true` = explicit **blocked mode** (`conversion_eligible: false`). Real email/webhook/sheet required. |
| Zoho | **Not live** — do not pretend sync |
| Ads conversions | `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false` |
| Pilot SEO | `NEXT_PUBLIC_PILOT_NOINDEX=true` |
| Tracking | Separate GTM/GA4 env placeholders per `us` / `au` / `ph` |

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
| `conversion_assist_opened` | Exit-intent / timed assist shown |
| `conversion_assist_cta_clicked` | Assist CTA clicked |
| `job_seeker_redirected` | Clicked through to `/ph` — never primary Ads conv |
| `spam_or_applicant_rejected` | Validation reject |

---

## 5. Historical evidence (informed keywords, negatives, RSA angles)

**Sources:** Editor exports ~2024-08-01 → 2026-08-04 (`audit-data/performance/`, UTF-16).  
**Machine summary:** `ads-launch/historical-performance-summary.json`

| Account | Cost | Clicks | Conversions | All conv | ST raw → deduped |
|---------|-----:|-------:|------------:|---------:|-----------------:|
| USA | $723,838.59 | 87,060 | 2,597.32 | 4,629.39 | 66,869 → 66,465 |
| AU | $457,489.46 | 49,457 | 1,412.66 | 3,505.46 | 26,211 → 26,132 |

**Keep examples (employer intent → package):** virtual assistant / hire VA / PH·filipino VA · how to hire a virtual assistant (**not** negatived) · social media manager philippines · virtual marketing assistant · philippines bookkeeper · lead gen VA · CS VA · PH accounting outsourcing.

**Kill / negative clusters:** onlinejobs.ph · free/reviews/pricing · VA jobs/salary/careers · bare WFH · Spanish/LATAM · Upwork/Fiverr/competitors · DSA bleed brands.

**RSA angle design uses ST:** hire-intent · Philippines-offshore · role-outcome · proof/speed-of-staffing (shortlist pipeline — **no** fake timelines, $/hr, “top 1%”, or savings %).

**Limitations:** ST cost &lt; campaign cost; Conversions inflated vs business outcomes; HR/recruitment thin (curated, not proven winners); historical brand conversion ≠ proof current microsite converts.

---

## 6. Ads structure (Paused package · v7)

### Topology (locked)

**2 campaigns × 2 markets. Brand deferred.**

| Campaign | ~Budget share | Job | Final URL |
|----------|--------------:|-----|-----------|
| `VC_{US\|AU}_S_CORE` | **~60%** | High-intent VA / hire / Philippines-offshore | **`/{us\|au}`** |
| `VC_{US\|AU}_S_ROLES` | **~40%** | Digital · Social · Admin · Controlled roles | Matching category |

**Roles AGs** include Digital · Social · Admin · Accounting · Bookkeeping · CS · HR · Recruitment · Sales.  
**Activation is not “Digital/Social/Admin first, hold books.”** See `PHASED-ACTIVATION.md`: enable by **PH/Filipino/offshore long-tail intent** first (books/accounting included when PH-shaped); generic Core heads later.

### Settings (all campaigns)

Search · **Exact + Phrase only** · **Maximize Clicks** · Max CPC US **$8** / AU **A$6** · **Paused** · tracking `{lpurl}` · UTMs once on suffix · employer CTAs · curated ST negatives · extensions microsite-only.

### Budgets (placeholders — not enable approval)

| Market | Core | Roles | Day total | ~Monthly |
|--------|-----:|------:|----------:|---------:|
| US | $75 | $50 | $125 | ≈ **$3.8k** |
| AU | A$75 | A$50 | A$125 | ≈ **A$3.8k** |

### Ad group map

**CORE (×2 markets):** `Hire_VA_PH` · `Offshore_VA_PH` → market home

**ROLES (×2 markets):**

| Intent tier (enable order) | Ad groups | Activation |
|----------------------------|-----------|------------|
| **Phase 1 — PH long-tail** | Any Core/Roles AG with Philippines/Filipino/offshore + hire/role Exact (+ tight Phrase) | **Enable first** (incl. Bookkeeping/Accounting when PH-shaped) |
| **Phase 2 — category w/o PH** | Broader role Exact/Phrase | After Phase 1 CTR/quality look sane |
| **Phase 3 — generic Core heads** | Bare VA / hire-a-VA without geo | Later, tighter CPC/budget |
| Built / structure labels | Digital · Social · Admin · Accounting · Books · CS · HR · Recruitment · Sales | Structure only — **not** the enable order |

Source of truth: `ads-launch/PHASED-ACTIVATION.md`.

### RSA (locked)

| Rule | Value |
|------|-------|
| Main AGs | **3 unique full RSAs** each (15 headlines + 4 descriptions — **no blanks**) |
| City-test | **1 RSA** |
| Claims ban | No top 1%, $/hr, save X%, guaranteed, consult/demo SaaS language |

### Negatives

**191 unique** campaign negatives × 4 campaigns = **764** rows. Intentionally **not** negatived: bare `hire` / `hiring`; `how to hire a virtual assistant`.

### Package counts (machine)

| Entity | Count | Status |
|--------|------:|--------|
| Campaigns | **4** | Paused |
| Ad groups | **40** | Paused |
| Positive keywords | **1,568** (Exact 1,182 · Phrase 386) | Paused |
| RSAs | **116** (38 main AGs × 3 + 2 city × 1) | Paused |
| Unique campaign negatives | **191** × 4 = 764 rows | Broad |
| Callouts / sitelinks / snippets | 24 / 16 / 4 | |
| CSV rows | **2,536** | |

Rebuild: `python3 ads-launch/build_stage1_editor_package.py`

---

## 7. What’s paused / not enabled / not claimed

- **Everything in the CSV** — Campaign, Ad group, Keyword, Ad status = **Paused**
- **No Google Ads enable** from this work
- **No Ads conversion firing**
- **Brand Search** — deferred (not imported)
- **WordPress** — untouched for paid Final URLs
- **Zoho / CallRail / real inbox** — not launch-ready
- **Log-only** — explicit blocked mode; **not** paid-ready; **not** conversion-eligible
- **Legacy outside CSV:** `PM_US_RSA_Brand` / `PM_AU_RSA_Brand` may still spend — pause in Ads UI separately
- We are **not** claiming: launch-ready, Zoho sync, job-order ROI, or that historical conversions = placements

---

## 8. Prior fuck-ups → fixed

| Era | Mistake | Fix |
|-----|---------|-----|
| Early | Double UTM (template **and** suffix) | Template `{lpurl}` only; suffix once |
| Early | Final URLs `?role=` inert on LP | Real `/us\|au/{slug}` + middleware 308 |
| Early | Template / boilerplate RSAs | Unique RSAs; builder QA rejects spam + blanks |
| Early | Fake AU phone placeholder | No AU phone UI; form primary |
| Early | “Consult” / “book a demo” SaaS language | Employer staffing CTAs |
| Early | Plastic / white-HR heroes | Recast Filipino aspirational assets |
| Early | Silent log-only accept by default | 503 unless channel **or** explicit flag |
| Early | Dishonest event names | `employer_inquiry_submitted` etc. |
| v4→v5 | Brand deferred while Core thin; role sprawl | Category URLs + Brand+Core attempt (22 campaigns) |
| **v5→v6** | 22 campaigns too many for Stage 1 | **2/account**; Brand deferred; Core $75 / Roles $50 |
| **v6 RSA** | Only 2 RSAs/AG — less learning | **3 unique full RSAs/main AG** (city stays 1) |
| **v6→v7** | Core generic VA → administrative-support (intent mismatch) | **Core → `/us` / `/au`**; Admin stays Roles category |
| **v7** | Log-only fired primary conversion | `conversion_eligible: false`; thank-you honest |
| **v7** | No WP-link CI | `no-wp-links.test.ts` fails on WP hrefs |
| **v7** | Exit-intent always on | Behind `NEXT_PUBLIC_ENABLE_EXIT_INTENT` |
| **Activation flip** | Docs said Core first then Digital/Social/Admin; hold books | **PH/Filipino/offshore long-tail first** across Core+Roles; books/accounting OK in Phase 1 when PH-shaped (`PHASED-ACTIVATION.md`) |

---

## 9. Remaining blockers (still open)

1. Real lead email / webhook recipients (**hard** — log-only ≠ paid-ready)  
2. Response-time SLA / who answers  
3. End-to-end delivery success + failure verified  
4. Zoho (optional — must not fake)  
5. CallRail / qualified-call tracking  
6. GTM → Ads conversion mapping (tested)  
7. US + AU custom paid domains + per-market GTM/GA4/GSC  
8. Explicit George approval to enable any campaign  
9. Pause legacy `PM_*` Brand bleed  
10. Brand Search scope (when/if added later)

---

## 10. Exact questions for ChatGPT to stress-test

1. **Is Core → `/us`/`/au` correct** vs category admin for “hire VA”?  
2. **Is log-only acceptable for any paid click?** (Our answer: **No.**)  
3. **Are Max CPC $8 / A$6 and $75/$50 dailies sane** vs historical CPC / $10–20k monthly story?  
4. **Activation by intent quality** — is PH long-tail first (incl. books) correct vs old “Core + Digital/Social/Admin only”?  
5. **RSA×3 angles** — sample three ads on one AG; any invented savings, “top 1%”, consult language, or clone-y noun swaps?  
6. **Keyword hygiene** — job-seeker / medical / Spanish / competitor leaks? Bare `hire` negatived by mistake?  
7. **Double UTM / WP Final URL** regressions in CSV.  
8. **Conversion mapping risk** if GTM maps wrong events before Max Conv.  
9. **Legacy PM_* Brand still Enabled** — parallel bleed.  
10. **Careers `/ph` divert** — real careers product or Stage 1 placeholder risk?  
11. **Microsite completeness** — gate, A/B, category coverage, nav/footer honesty vs corporate WP claims.  
12. **What must be true before first $1 of enable** — ordered checklist.

### Do **not** invent requirements we never claimed

- Live Zoho writeback · CallRail qualified calls · WP redesign · Broad/PMax “for volume” · Fake AU phone · Brand Search in this CSV · Fake placement guarantees in RSAs

---

## 11. Package file map

| Path | What |
|------|------|
| `ads-launch/google-ads-editor-import.csv` | Editor import (Paused · v7) |
| `ads-launch/build_stage1_editor_package.py` | Builder + QA |
| `ads-launch/DECISIONS.md` | Locked operator defaults |
| `ads-launch/PHASED-ACTIVATION.md` | Enable order source of truth (PH long-tail first) |
| `ads-launch/FULL-BUILD-REPORT.md` | Short index |
| `ads-launch/CHATGPT-MEGA-AUDIT.md` | Deep companion |
| `ads-launch/01`–`12` | Audit / LP / activation docs |
| `ads-launch/historical-performance-summary.json` | ST machine summary |
| `vision/` | Microsite (Next.js) |
| `vision/config/categories.ts` | Category copy + A/B |
| `vision/config/site.ts` | Nav, footer, public quotes |
| `vision/lib/no-wp-links.test.ts` | WP egress audit |
| `vision/scripts/validate-routes.mjs` | Route inventory check |
| `xray/` | Launch Control / X-ray (CSV mirrored under `xray/docs/ads-launch/`) |

### Spot-check

```bash
python3 ads-launch/build_stage1_editor_package.py

python3 - <<'PY'
import csv
from collections import Counter, defaultdict
rows=list(csv.DictReader(open('ads-launch/google-ads-editor-import.csv',encoding='utf-8-sig')))
print('campaigns', sorted({r['Campaign'] for r in rows}))
print(Counter(r['Row Type'] for r in rows))
assert {r['Campaign'] for r in rows} == {
  'VC_US_S_CORE','VC_US_S_ROLES','VC_AU_S_CORE','VC_AU_S_ROLES'}
ads=[r for r in rows if r['Row Type']=='Ad']
core=[r for r in ads if r['Campaign'].endswith('_S_CORE')]
assert all(r['Final URL'].rstrip('/').endswith(('/us','/au')) for r in core)
assert all(not r['Final URL'].rstrip('/').endswith(('/us','/au')) for r in ads if r['Campaign'].endswith('_S_ROLES'))
by=defaultdict(int)
for r in ads: by[(r['Campaign'], r['Ad Group'])]+=1
assert all(n==3 for (c,a),n in by.items() if 'City' not in a)
assert all(n==1 for (c,a),n in by.items() if 'City' in a)
print('RSA', len(ads), 'CORE→market home OK; Roles→category OK')
PY

cd vision && npm test && npm run validate:routes && npm run typecheck && npm run build
```

---

## 12. Operator next (not Ads enable)

1. Hostile audit of **this** debrief (optional MEGA companion).  
2. Replace log-only with real lead delivery — **hard gate**.  
3. Import CSV **Paused**; human review matrix `09`.  
4. Pause legacy `PM_*` Brand if still bleeding.  
5. Enable only per `PHASED-ACTIVATION.md` after **explicit** George approval — **PH/Filipino/offshore long-tail first** (Core + Roles; books OK when PH-shaped), not generic Core heads first.

**Ads remain Off.**  
**Paid status: NOT READY FOR PAID TRAFFIC.**

---

*End of complete ChatGPT debrief (v7 · Core→market home). This file is the canonical paste. Companion: `CHATGPT-MEGA-AUDIT.md`. Index: `FULL-BUILD-REPORT.md`.*
