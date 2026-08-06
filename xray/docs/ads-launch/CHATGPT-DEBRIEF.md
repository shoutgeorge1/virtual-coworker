# Virtual Coworker Stage 1 — Complete ChatGPT Debrief (v6 · RSA×3)

**Paste this whole file into ChatGPT.** Ask it to stress-test honesty, architecture, Final URLs, conversion definitions, LP integrity, Ads package hygiene, and launch blockers — not to rewrite ads for vibes.

| Field | Value |
|-------|-------|
| Date | 2026-08-05 |
| Branch | `vision-demo` |
| Repo | `/Users/george/Developer/virtual-coworker` |
| Package | `ads-launch/google-ads-editor-import.csv` · `lp_version=stage1-v6` |
| Builder | `ads-launch/build_stage1_editor_package.py` |
| Decisions | `ads-launch/DECISIONS.md` |
| Short index | `ads-launch/FULL-BUILD-REPORT.md` |
| Deep companion | `ads-launch/CHATGPT-MEGA-AUDIT.md` (points here as canonical) |
| LP host (live) | **https://vision-three-alpha.vercel.app** |
| Launch Control | **https://vc-xray.vercel.app/launch-control** |
| Corporate WP (untouched) | https://virtualcoworker.com · https://virtualcoworker.com.au |
| Accounts | USA `496-715-1855` · AU `573-539-1940` |
| Ads enable | **NOT approved** — all CSV entities **Paused** |
| RSA rule (locked) | **3 unique full RSAs (15H/4D) per main AG**; city-test 1 |

---

## 1. Project goal / business model

Virtual Coworker is a **staffing partner**: US/AU employers hire dedicated Philippines-based teammates (VA, marketing, social, books, CS, sales, etc.). We recruit, vet, and shortlist; the employer interviews and decides.

**Paid Stage 1 goal:** Route high-intent Google Search traffic to a **new Next.js microsite** (not WordPress), capture **employer hiring inquiries**, and learn which RSA angles win — without pretending a form submit is revenue.

### Conversion truth (locked — do not inflate)

```
Ad click
  → employer_inquiry_submitted   (= server-accepted employer inquiry)
  → human follow-up
  → job order                    (CRM — not wired)
  → placement                    (ops — not wired)

form submit ≠ job order ≠ placement
phone_cta_clicked ≠ qualified call
Editor "Conversions" / "All conv" ≠ job orders
```

Historical Ads “Conversions” in exports are **not** proof of placements. Stage 1 tracking names match this honesty.

---

## 2. Architecture: paid microsite vs WordPress

| Surface | Role |
|---------|------|
| **Paid microsite** (`vision/` → Vercel `vision-three-alpha`) | Only Final URL host for Stage 1 Search |
| **WordPress** virtualcoworker.com / .com.au | **Untouched** — marketing site stays; **paid traffic must not use WP Final URLs** |
| **Launch Control** vc-xray | Operator dashboard / X-ray / launch checklist |
| **Careers** `/ph` on microsite | Job-seeker divert — **never** employer conversion |

Microsite is an **independent paid hiring path** with employer gate, category LPs, A/B variants, honest events, and pilot `noindex`.

---

## 3. Live URLs (everything ChatGPT should open)

### Control / ops

| Page | URL |
|------|-----|
| Launch Control | https://vc-xray.vercel.app/launch-control |
| Microsite home | https://vision-three-alpha.vercel.app/ |
| Services index | https://vision-three-alpha.vercel.app/services |
| How it works | https://vision-three-alpha.vercel.app/how-it-works |
| Privacy (microsite) | https://vision-three-alpha.vercel.app/privacy |
| Terms (microsite) | https://vision-three-alpha.vercel.app/terms |
| Thank you | https://vision-three-alpha.vercel.app/thank-you |
| Careers (PH) | https://vision-three-alpha.vercel.app/ph |
| Careers apply | https://vision-three-alpha.vercel.app/ph/apply |

### Market hubs

| Market | Hub | Gate deep-link |
|--------|-----|----------------|
| US | https://vision-three-alpha.vercel.app/us | https://vision-three-alpha.vercel.app/us#gate |
| AU | https://vision-three-alpha.vercel.app/au | https://vision-three-alpha.vercel.app/au#gate |

### Category LPs (9 × 2 markets) — Ads Final URLs use these paths

| Category slug | US | AU |
|---------------|----|----|
| digital-marketing | https://vision-three-alpha.vercel.app/us/digital-marketing | https://vision-three-alpha.vercel.app/au/digital-marketing |
| social-media | https://vision-three-alpha.vercel.app/us/social-media | https://vision-three-alpha.vercel.app/au/social-media |
| accounting | https://vision-three-alpha.vercel.app/us/accounting | https://vision-three-alpha.vercel.app/au/accounting |
| bookkeeping | https://vision-three-alpha.vercel.app/us/bookkeeping | https://vision-three-alpha.vercel.app/au/bookkeeping |
| administrative-support | https://vision-three-alpha.vercel.app/us/administrative-support | https://vision-three-alpha.vercel.app/au/administrative-support |
| customer-service | https://vision-three-alpha.vercel.app/us/customer-service | https://vision-three-alpha.vercel.app/au/customer-service |
| hr | https://vision-three-alpha.vercel.app/us/hr | https://vision-three-alpha.vercel.app/au/hr |
| recruitment | https://vision-three-alpha.vercel.app/us/recruitment | https://vision-three-alpha.vercel.app/au/recruitment |
| sales | https://vision-three-alpha.vercel.app/us/sales | https://vision-three-alpha.vercel.app/au/sales |

### A/B + compat

| Mechanism | Spec |
|-----------|------|
| Cookie | `vc_ab_variant` = `a` \| `b` |
| QA override | `?variant=a` or `?variant=b` on any market/category URL |
| Differs | H1, subhead, primary CTA, hero image (per `vision/config/categories.ts`) |
| Legacy query | `/us?role=bookkeeping` → **308** `/us/bookkeeping` (middleware) |
| Legacy consult | `/us/consult`, `/au/consult` → gate / hiring path (compat) |

Example QA:  
https://vision-three-alpha.vercel.app/us/administrative-support?variant=a  
https://vision-three-alpha.vercel.app/us/administrative-support?variant=b

### Ads Final URL mapping (this package)

| Campaign | Final URL pattern |
|----------|-------------------|
| `VC_*_S_CORE` | `…/{us\|au}/administrative-support` (VA / hire / offshore cluster) |
| `VC_*_S_ROLES` | Matching category slug per role AG |
| Brand | **Deferred** — no generic `/us` or `/au` Final URLs on ads |

Tracking template: `{lpurl}` only.  
Final URL suffix (once): UTMs + `lp_version=stage1-v6`. **No double UTM.**

---

## 4. Microsite product surface

### Casting / heroes

- Filipino aspirational brand assets (prod casting commit `8705ff0`).
- Plastic / white-HR stock heroes **killed**.
- Category A/B heroes pull from `/brand/*` (va-ph, talent-john, support, face series, etc.).

### Nav / footer (polish landed on `vision-demo`)

Shared `SiteNav` + `SiteFooter` (`vision/config/site.ts`):

- Nav: **Services · How it works · US · AU · Start hiring · Careers**
- Footer: corporate addresses from live WP contact page, privacy/terms links, copyright
- Trust quotes: public client quotes from virtualcoworker.com homepage (not invented)
- New routes: `/services`, `/how-it-works` (plus privacy/terms)

If something still feels mid-flight in UI polish, **do not block Ads package review** — Ads CSV is complete and Paused.

### Gate / form / phone

| Item | Spec |
|------|------|
| Gate | Employer vs job seeker → job seekers divert to `/ph` (no employer conversion) |
| Form | Employer hiring inquiry → `/api/lead` |
| US phone | **310-426-8776** (`NEXT_PUBLIC_US_PHONE`) |
| AU phone | **None** — form-primary (no fake AU number) |
| Lead delivery | **TEMPORARY log-only** (`ALLOW_LOG_ONLY_LEADS=true`) until real inbox/webhook |
| Zoho | **Not live** — do not pretend sync |
| Ads conversions | `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false` |
| Pilot SEO | `NEXT_PUBLIC_PILOT_NOINDEX=true` |

### Events (dataLayer / GTM-ready; Ads firing off)

| Event | Meaning |
|-------|---------|
| `employer_gate_selected` | Chose employer |
| `employer_form_started` | First form interaction |
| `employer_inquiry_submitted` | **Server accepted** inquiry (candidate primary) |
| `employer_inquiry_submitted_deduped` | Refresh-safe block |
| `phone_cta_clicked` | tel: click — `is_qualified_call: false` |
| `job_seeker_diverted` | Careers path — never primary Ads conv |
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

## 6. Ads structure (Paused package)

### Topology (locked)

**2 campaigns × 2 markets. Brand deferred.**

| Campaign | ~Budget share | Job |
|----------|--------------:|-----|
| `VC_{US\|AU}_S_CORE` | **~60%** | High-intent VA / hire / Philippines-offshore |
| `VC_{US\|AU}_S_ROLES` | **~40%** | Digital · Social · Admin · Controlled roles |

**Controlled** under Roles = accounting, bookkeeping, customer service, HR, recruitment, sales.

**Why 2 (not 22):** George approved collapsing Brand+Core+9 role campaigns into Core + Roles so budget is controllable (~60/40), Core owns the densest employer ST cluster, Roles keep role intent / Final URL hygiene without nine daily budgets.

### Settings (all campaigns)

Search · **Exact + Phrase only** · **Maximize Clicks** · Max CPC US **$8** / AU **A$6** · **Paused** · category Final URLs · tracking `{lpurl}` · UTMs once on suffix · employer CTAs · curated ST negatives · extensions microsite-only.

### Budgets (placeholders — not enable approval)

| Market | Core | Roles | Day total | ~Monthly |
|--------|-----:|------:|----------:|---------:|
| US | $75 | $50 | $125 | ≈ **$3.8k** |
| AU | A$75 | A$50 | A$125 | ≈ **A$3.8k** |

Inside a **$10–20k per account / month** budget story — Stage 1 pace, headroom to raise after inquiry quality is trusted.

### Ad group map

**CORE (×2 markets):** `Hire_VA_PH` · `Offshore_VA_PH`

**ROLES (×2 markets):**

| Tier | Ad groups |
|------|-----------|
| Digital | `Digital_Marketing_Hire_PH` · `Digital_Marketing_Outsource_PH` |
| Social | `Social_Media_Hire_PH` · `Social_Media_Outsource_PH` |
| Admin | `Administration_EA_PH` · `Admin_City_Test` (light geo; **1 RSA**) |
| Controlled | Accounting / Bookkeeping / CS / HR / Recruitment / Sales — each Hire + Outsource (HR/Recruitment Hire+Outsource) |

Fresh naming: **`VC_*`** — not legacy `PM_*`.

### RSA (locked decision)

| Rule | Value |
|------|-------|
| Main AGs | **3 unique full RSAs** each (15 headlines + 4 descriptions — **no blanks**) |
| City-test | **1 RSA** (may be 1–2 if tiny) |
| Angles | Distinct — **not** noun-swap clones of #1/#2 |
| Typical trio (Hire AGs) | A staffing/hire-intent · B role-outcome · C proof/speed (shortlist) |
| Typical trio (Outsource AGs) | A partner · B capacity · C dedicated-seat proof |
| Core example | `Hire_VA_PH`: hire · hire_b · hire_c (how-to-hire / shortlist speed) |
| Claims ban | No top 1%, $/hr, save X%, guaranteed, consult/demo SaaS language |

**Sample — `VC_US_S_CORE` / `Hire_VA_PH` (three angles):**

1. **hire** — Hire Virtual Assistant PH / Hire Filipino VA → staffing-partner hire path  
2. **hire_b** — Looking for a VA? / VA for Hire Philippines → agency / looking intent  
3. **hire_c** — How to Hire a VA Fast / VA Shortlist for Employers → shortlist-speed (ST: “how to hire a virtual assistant”)

### Negatives

**191 unique** campaign negatives × 4 campaigns = **764** rows. Curated from ST waste — **not** a wholesale dump of the old account. Intentionally **not** negatived: bare `hire` / `hiring`; `how to hire a virtual assistant`.

### Extensions

Callouts / sitelinks / structured snippets — **microsite URLs only** (no WP).

### Package counts (machine, after RSA×3)

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
- **Zoho / CallRail / real inbox** — not launch-ready (log-only is TEMPORARY)
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

---

## 9. Remaining blockers (still open)

1. Real lead email / webhook recipients (log-only ≠ paid-ready)  
2. Response-time SLA / who answers  
3. Zoho (optional — must not fake)  
4. CallRail / qualified-call tracking  
5. GTM → Ads conversion mapping  
6. Custom paid domain (optional host swap)  
7. Explicit George approval to enable any campaign  
8. Pause legacy `PM_*` Brand bleed  
9. Brand Search scope (when/if added later)

---

## 10. Exact questions for ChatGPT to stress-test

1. **Is 2-campaign topology sane** vs Brand + many role campaigns? Challenge Core → `administrative-support` Final URL for “hire VA.”  
2. **Is log-only acceptable for any paid click?** (Our answer: **No.**)  
3. **Are Max CPC $8 / A$6 and $75/$50 dailies sane** vs historical CPC / $10–20k monthly story?  
4. **Controlled-tier thin ST (HR/recruitment)** — keep Paused longer / strip from Stage 1?  
5. **RSA×3 angles** — sample three ads on one AG; any invented savings, “top 1%”, consult language, or clone-y noun swaps?  
6. **Keyword hygiene** — job-seeker / medical / Spanish / competitor leaks? Bare `hire` negatived by mistake?  
7. **Double UTM / WP Final URL / generic Brand URL** regressions in CSV.  
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
| `ads-launch/google-ads-editor-import.csv` | Editor import (Paused) |
| `ads-launch/build_stage1_editor_package.py` | Builder + QA |
| `ads-launch/DECISIONS.md` | Locked operator defaults |
| `ads-launch/FULL-BUILD-REPORT.md` | Short index |
| `ads-launch/CHATGPT-MEGA-AUDIT.md` | Deep companion |
| `ads-launch/01`–`12` | Audit / LP / activation docs |
| `ads-launch/historical-performance-summary.json` | ST machine summary |
| `vision/` | Microsite (Next.js) |
| `vision/config/categories.ts` | Category copy + A/B |
| `vision/config/site.ts` | Nav, footer, public quotes |
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
by=defaultdict(int)
for r in ads: by[(r['Campaign'], r['Ad Group'])]+=1
assert all(n==3 for (c,a),n in by.items() if 'City' not in a)
assert all(n==1 for (c,a),n in by.items() if 'City' in a)
assert all(r[f'Headline {i}'] and r.get(f'Description {j}')
           for r in ads for i in range(1,16) for j in range(1,5))
print('RSA', len(ads), 'main AGs ×3 OK; city ×1 OK')
PY
```

---

## 12. Operator next (not Ads enable)

1. Hostile audit of **this** debrief (optional MEGA companion).  
2. Replace log-only with real lead delivery.  
3. Import CSV **Paused**; human review matrix `09`.  
4. Pause legacy `PM_*` Brand if still bleeding.  
5. Enable only per `07-phased-activation-recommendation.md` after **explicit** George approval.

**Ads remain Off.**

---

*End of complete ChatGPT debrief (v6 · RSA×3). This file is the canonical paste. Companion: `CHATGPT-MEGA-AUDIT.md`. Index: `FULL-BUILD-REPORT.md`.*
