# Virtual Coworker Stage 1 — MEGA AUDIT for ChatGPT

**Paste this whole file into ChatGPT.** Ask it to challenge honesty, conversion definitions, Final URL/path integrity, Ads package hygiene, and remaining launch blockers — not to rewrite copy for vibes.

| Field | Value |
|-------|-------|
| Date | 2026-08-05 |
| Branch | `vision-demo` |
| Repo | `/Users/george/Developer/virtual-coworker` |
| LP host (preview) | `https://vision-three-alpha.vercel.app` |
| Launch Control | `https://vc-xray.vercel.app/launch-control` |
| Ads package | `ads-launch/google-ads-editor-import.csv` · `lp_version=stage1-v5` |
| LP engine | `vision/config/categories.ts` + `MarketLanding` / `LeadGate` |
| Casting commit | `8705ff05a92ffd89225294c02eb514f5ec1b445c` — **deployed** to vision production |
| Mega-audit commit | `b3c8542` (full: resolve via `git rev-parse b3c8542` on `vision-demo`) |
| WordPress | **Untouched** — paid traffic must not use WP Final URLs |
| Ads enable | **NOT approved** — all Stage 1 CSV entities **Paused** |

---

## 0. Executive honesty

We built a **paid Search microsite + Paused Editor package** so US/AU employer hiring intent can land on category-specific LPs with honest inquiry tracking.

We did **not**:

- Enable any Stage 1 campaign
- Wire Zoho CRM as live sync
- Wire CallRail qualified-call tracking
- Fire Google Ads conversions from the app (`NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false`)
- Prove that Ads “Conversions” historically equaled job orders (they do **not**)
- Buy/attach a custom paid domain (still on `vision-three-alpha.vercel.app`)

**Conversion truth (locked language):**

```
Ad click
  → employer_inquiry_submitted   (= qualified inquiry attempt; server accepted)
  → human follow-up
  → job order                    (CRM — not wired)
  → placement                    (ops — not wired)

form submit ≠ job order ≠ placement
phone_cta_clicked ≠ qualified call
Editor "Conversions" / "All conv" ≠ job orders
```

If ChatGPT treats inquiry count as revenue or placement proof, reject that reading.

---

## 1. Architecture

### 1.1 Systems

| System | Role | Status |
|--------|------|--------|
| **vision** (Next.js on Vercel) | Paid landing microsite: `/us`, `/au`, 9 category routes each, gate, lead API, A/B | Live preview host |
| **ads-launch/** | Stage 1 Google Ads Editor CSV + audits + DECISIONS | Local package; import Paused only |
| **xray** (`vc-xray.vercel.app`) | Operator Launch Control checklist | Live |
| **WordPress (virtualcoworker.com)** | Legacy marketing site | **Out of Stage 1 paid path** — do not spray ads there |
| **Zoho / CallRail / GTM Ads convert** | Downstream | Not launch-ready |

### 1.2 Why a microsite

Historical Ads Final URLs and WP paths mixed brand, DSA, PMax, and generic service pages. Stage 1 forces:

1. Exact/Phrase Search only (no Broad positives, no PMax, no DSA in this CSV)
2. Category Final URLs that match real LP routes
3. Employer gate (job seekers diverted — no employer conversion)
4. Honest event names + delivery honesty (no fake Zoho success)

### 1.3 Key repo paths

```
vision/                          # Next.js LP app
  app/us/page.tsx
  app/au/page.tsx
  app/us/[category]/page.tsx
  app/au/[category]/page.tsx
  app/api/lead/route.ts
  app/components/MarketLanding.tsx
  app/components/LeadGate.tsx
  config/categories.ts           # 9 categories × A/B heroes/copy
  middleware.ts                  # A/B cookie + ?role= → category redirect
  lib/ab-variant.ts
  lib/lead-delivery.ts
  lib/lead-validation.ts
ads-launch/
  google-ads-editor-import.csv   # v5 Paused package
  build_stage1_editor_package.py
  analyze_historical_performance.py
  historical-performance-summary.json
  DECISIONS.md
  LAUNCH-SHEET.md
  01–12 audit docs
  CHATGPT-MEGA-AUDIT.md          # THIS FILE
  FULL-BUILD-REPORT.md           # shorter v5 index
xray/launch-control.html         # operator checklist
audit-data/performance/          # ~2y Editor exports (UTF-16)
```

---

## 2. Business model / Stage 1 conversion truth

Virtual Coworker is an **offshore staffing partner** (Philippines talent) for **employers** — not a freelance marketplace, not a job board, not SaaS “book a demo.”

Stage 1 paid funnel sells **hiring inquiries**:

1. Employer lands on market or category LP
2. Gate: employer vs job seeker
3. Job seeker → careers divert (`NEXT_PUBLIC_CAREERS_URL=/ph` for Stage 1) — **never** primary Ads conversion
4. Employer → role + details → `POST /api/lead`
5. Server validates → delivery channel OR (QA only) log-only
6. Thank-you page; dataLayer event `employer_inquiry_submitted`

**What success is *not*:** form submit counted as job order, phone click counted as qualified call, or historical Ads conversions treated as placements.

---

## 3. Live LP URLs (Stage 1)

**Host:** `https://vision-three-alpha.vercel.app`  
**Casting / category heroes:** commit `8705ff05a92ffd89225294c02eb514f5ec1b445c` on production (alias `vision-three-alpha`).

### 3.1 Generics

| URL | Market | Phone |
|-----|--------|-------|
| https://vision-three-alpha.vercel.app/us | US | `310-426-8776` (`NEXT_PUBLIC_US_PHONE`) |
| https://vision-three-alpha.vercel.app/au | AU | **None** — form primary |

### 3.2 US categories (9)

| URL |
|-----|
| https://vision-three-alpha.vercel.app/us/digital-marketing |
| https://vision-three-alpha.vercel.app/us/social-media |
| https://vision-three-alpha.vercel.app/us/accounting |
| https://vision-three-alpha.vercel.app/us/bookkeeping |
| https://vision-three-alpha.vercel.app/us/administrative-support |
| https://vision-three-alpha.vercel.app/us/customer-service |
| https://vision-three-alpha.vercel.app/us/hr |
| https://vision-three-alpha.vercel.app/us/recruitment |
| https://vision-three-alpha.vercel.app/us/sales |

### 3.3 AU categories (9)

Same slugs under `/au/…` — form primary, no phone UI.

### 3.4 A/B QA overrides

| URL | Purpose |
|-----|---------|
| `…/us/digital-marketing?variant=a` | Force variant A |
| `…/us/digital-marketing?variant=b` | Force variant B |

Middleware sets cookie `vc_ab_variant` for 90 days. SSR reads same cookie → no hydration mismatch.

### 3.5 Compat / legacy

| Route | Behavior |
|-------|----------|
| `/us?role=bookkeeping` (etc.) | **308** → `/us/bookkeeping` |
| `/us/consult`, `/au/consult` | Redirect to `#gate` (no demo booking page) |
| Launch Control | https://vc-xray.vercel.app/launch-control |

### 3.6 Casting map (before → after)

George approved: **“all hot / beer-with dude / variety good.”**  
Plastic/blue-shirt stock and white-HR casting removed from category heroes.

| Category | Variant A hero | Variant B hero | Killed (before) |
|----------|----------------|----------------|-----------------|
| digital-marketing | `/brand/va-au.jpg` (DM desk guy) | `/brand/talent-john.jpeg` | `marketing.webp`, mixed `va-us`/`va-au` |
| social-media | `/brand/va-ph.jpg` | `/brand/va-face-3.jpg` | `marketing.webp`, `va-team.webp` |
| accounting | `/brand/va-face-2.jpg` | `/brand/support.jpg` | workstation reuse / `va-us` |
| bookkeeping | `/brand/va-face-1.jpg` | `/brand/va-face-2.jpg` | `support.jpg` / `ea.jpg` |
| administrative-support | `/brand/va-ph.jpg` | `/brand/va-face-1.jpg` | `va-us` / `ea.jpg` |
| customer-service | `/brand/support.jpg` | `/brand/va-face-2.jpg` | `va-team.webp` |
| hr | `/brand/va-face-1.jpg` | `/brand/va-face-3.jpg` | **`hire-talent.webp` (white HR)** |
| recruitment | `/brand/va-face-2.jpg` | `/brand/talent-john.jpeg` | `hire-talent.webp`, `va-team.webp` |
| sales | `/brand/va-us.jpg` (sales woman) | `/brand/va-face-1.jpg` | `marketing.webp` |

**Spot-check (do not trust this table alone):** open LP → view hero `src` in Network/Img → must be one of  
`va-au.jpg | talent-john.jpeg | va-ph.jpg | va-face-1|2|3.jpg | support.jpg | va-us.jpg`  
Must **not** be `marketing.webp`, `hire-talent.webp`, `ea.jpg`, `va-team.webp`.

Live preload check (examples observed 2026-08-05):

- `/us/digital-marketing?variant=a` → `va-au.jpg`
- `/us/digital-marketing?variant=b` → `talent-john.jpeg`
- `/us/hr?variant=a` → `va-face-1.jpg`
- `/us/hr?variant=b` → `va-face-3.jpg`

---

## 4. A/B behavior

| Item | Spec |
|------|------|
| Cookie | `vc_ab_variant` = `a` \| `b` |
| Assignment | ~50/50 from seed when unset; query overrides |
| Differs | H1, subhead, primary CTA, hero image |
| Captured | Submit payload + dataLayer events include `variant` |
| Not | Server experiment platform; not proof of lift until GA4/GTM sample exists |

See `ads-launch/05-ab-matrix.md`.

---

## 5. Form / gate / tracking / lead delivery

### 5.1 Events (`ads-launch/10-tracking-event-spec.md`)

| Event | When | Ads primary? |
|-------|------|--------------|
| `employer_gate_selected` | Employer chosen | No |
| `employer_form_started` | First form interaction | No |
| `employer_inquiry_submitted` | Server accepted employer lead | **Candidate** (not job order) |
| `employer_inquiry_submitted_deduped` | Refresh/dedupe | No |
| `phone_cta_clicked` | tel: click | Secondary; `is_qualified_call: false` |
| `job_seeker_diverted` | Job seeker gate | **Never** primary |
| `spam_or_applicant_rejected` | Validation reject | No |

Legacy names retired: `employer_form_valid_submit`, `phone_click`, `employer_gate_pass`.

Attribution fields: UTMs, gclid/gbraid/wbraid, landing URL, referrer, market, category, variant, `lp_version=stage1-v5`.

### 5.2 Lead delivery honesty (critical)

| Condition | API |
|-----------|-----|
| No email/webhook/sheet/zoho + no log-only flag | **503** `delivery_not_configured` |
| `ALLOW_LOG_ONLY_LEADS=true` (prod QA) | Accept → **server logs only** |
| Zoho URL missing | `zoho_synced: false` (not fake success) |
| All configured channels fail | **502** |

**Current prod env (vision):**

- `ALLOW_LOG_ONLY_LEADS` = true (**TEMPORARY QA**)
- `NEXT_PUBLIC_CAREERS_URL` = `/ph`
- `NEXT_PUBLIC_US_PHONE` set
- `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS` = false
- `NEXT_PUBLIC_PILOT_NOINDEX` = true
- **No** `NEXT_PUBLIC_AU_PHONE`
- **No** real `LEAD_EMAIL_*` / Resend / webhook for paid

**Do not claim leads land in a human inbox today.** Log-only is QA scaffolding.

---

## 6. Historical ST evidence summary

**Sources:** `audit-data/performance/*_2026-08-05.csv` (UTF-16 Editor exports)  
**Window:** ~2024-08-01 → 2026-08-04  
**Machine summary:** `ads-launch/historical-performance-summary.json`

| Account | Cost | Clicks | Conversions | All conv | ST raw → deduped |
|---------|-----:|-------:|------------:|---------:|-----------------:|
| USA `496-715-1855` | $723,838.59 | 87,060 | 2,597.32 | 4,629.39 | 66,869 → 66,465 |
| AU `573-539-1940` | $457,489.46 | 49,457 | 1,412.66 | 3,505.46 | 26,211 → 26,132 |

**All conv ≫ Conversions** — treating either as job orders is false.

### Keep examples (employer intent → package)

- virtual assistant / hire virtual assistant / PH·filipino VA
- how to hire a virtual assistant (**not** negatived)
- social media manager philippines
- virtual marketing assistant
- philippines bookkeeper
- lead generation virtual assistant
- customer service virtual assistant
- philippines accounting outsourcing

### Kill / negative clusters

- onlinejobs.ph + pricing research
- free VA · reviews · top 10
- VA jobs / salary / careers
- bare WFH fluff
- Spanish/LATAM · marketplace · competitors (upwork/fiverr/etc.)
- DSA bleed brands

### Limitations ChatGPT must not ignore

1. ST cost &lt; campaign cost (missing ST rows; PMax/DSA mix in history)
2. Conversions inflated vs business outcomes
3. HR/recruitment thin — curated keywords, not “proven winners”
4. Historical brand conversion ≠ proof current microsite converts

See `02-historical-data-audit.md`, `03-search-term-category-findings.md`.

---

## 7. Ads package inventory (all Paused)

**File:** `ads-launch/google-ads-editor-import.csv`  
**Builder:** `ads-launch/build_stage1_editor_package.py`  
**Accounts:** USA `496-715-1855` · AU `573-539-1940`

| Entity | Count | Status |
|--------|------:|--------|
| Campaigns | 22 | Paused |
| Ad groups | 46 | Paused |
| Positive keywords | 1,604 (Exact 1,218 · Phrase 386) | Paused |
| RSAs | 82 | Paused |
| Campaign negative rows | 4,202 (191 unique × 22) | Broad negatives |
| Callouts | 132 | |
| Sitelinks | 88 | microsite only |
| Structured snippets | 22 | |
| **CSV rows** | **6,198** | |

### Campaign shape (per market)

```
VC_{MKT}_S_BRAND
VC_{MKT}_S_CORE_hire_va
VC_{MKT}_S_ROLE_digital_marketing
VC_{MKT}_S_ROLE_social_media
VC_{MKT}_S_ROLE_accounting
VC_{MKT}_S_ROLE_bookkeeping
VC_{MKT}_S_ROLE_administration
VC_{MKT}_S_ROLE_customer_service
VC_{MKT}_S_ROLE_hr
VC_{MKT}_S_ROLE_recruitment
VC_{MKT}_S_ROLE_sales
```

### Final URLs (must match live routes)

| Layer | Final URL |
|-------|-----------|
| Brand | `https://vision-three-alpha.vercel.app/{us\|au}` |
| Core | `…/{us\|au}/administrative-support` |
| Role | `…/{us\|au}/{category-slug}` |

Tracking: template `{lpurl}` only · Final URL suffix carries UTMs + `lp_version=stage1-v5` (**once** — no double UTM).

### Budgets / CPC in CSV (machine-checked)

| Market | Brand | Core | Role | Max CPC |
|--------|------:|-----:|-----:|--------:|
| US | $40 | $60 | $25 | $8 |
| AU | A$40 | A$40 | A$20 | A$6 |

No `[APPROVAL_*]` tokens remain in the CSV.

**Still live outside this CSV (Aug 5 Ads UI read):** legacy `PM_US_RSA_Brand` / `PM_AU_RSA_Brand` spending small with 0 conversions — recommend pause before/with import (George clicks in Ads).

---

## 8. Decisions locked (`ads-launch/DECISIONS.md`)

| Decision | Locked value |
|----------|--------------|
| AU phone | Form-primary only — no fake AU number |
| US phone | `310-426-8776` |
| Careers URL | `/ph` via `NEXT_PUBLIC_CAREERS_URL` |
| Lead delivery (QA) | `ALLOW_LOG_ONLY_LEADS=true` — **TEMPORARY** logs |
| Ads conversions | Observe-only (`false`) |
| Pilot indexing | `noindex` |
| US budgets | Brand $40 · Core $60 · Role $25 |
| AU budgets | Brand A$40 · Core A$40 · Role A$20 |
| Max CPC | US $8 · AU A$6 |
| Google Ads enable | **Not approved** |

### Still open (not faked)

- Real lead email / webhook recipients
- Zoho CRM sync
- CallRail / qualified-call tracking
- GTM Ads conversion mapping
- Custom paid domain
- Explicit George approval to enable any Search campaign
- Pause decision on legacy PM_* Brand campaigns

---

## 9. Known fuck-ups we fixed

| Fuck-up | Fix |
|---------|-----|
| **Double UTM** (Tracking template `?utm…` **and** Final URL suffix `utm…`) | Template `{lpurl}` only; suffix once |
| **Inert `?role=`** Final URLs (LP ignored query) | Category routes `/us\|au/{slug}` + middleware 308 from `?role=` |
| **Template / boilerplate RSAs** | Unique RSAs; builder QA rejects spam headlines |
| **Fake AU phone** (`[AU_BUSINESS_PHONE]`) | No AU phone UI when unset; form primary |
| **Consult / SaaS language** (“hiring consult”, “book a demo”) | Employer staffing CTAs; `/consult` → `#gate` |
| **Brand deferred while Core needed** | Brand + Core campaigns added in v5 |
| **Plastic / blue-shirt / white-HR heroes** | Recast to Filipino aspirational brand assets (`8705ff0`); George approved |
| **Log-only leads by default (silent accept)** | 503 unless channel configured **or** explicit `ALLOW_LOG_ONLY_LEADS` |
| **Dishonest event names** | Renamed to inquiry / phone_cta / divert |

---

## 10. Remaining blockers / what ChatGPT should challenge

### Challenge these hard

1. **Is log-only lead delivery acceptable for any paid click?** (Our answer: **No** — QA only.)
2. **Does careers `/ph` divert job seekers to a real careers product?** (Stage 1 default; may be wrong long-term.)
3. **Are Max CPC $8 / A$6 and role budgets ($25 / A$20) sane vs historical CPC?** Challenge with export reality — defaults are George-decidable, not proven optimal.
4. **Do RSA headlines invent savings/credentials?** Builder rejects some patterns; human still must sample ads in Editor.
5. **Is Core → administrative-support Final URL correct for “hire VA”?** Intentional; challenge if Brand/Core should split further.
6. **HR/recruitment campaigns with thin ST** — should they stay Paused longer / be removed from Stage 1?
7. **Legacy PM_* Brand still Enabled** — package does not pause them; ops risk of parallel bleed.
8. **Conversion mapping** — if GTM maps wrong events, Max Conv later will poison bidding.
9. **Custom domain missing** — preview host in Final URLs is temporary; host swap must preserve category paths.
10. **Casting variety** — George approved; still challenge whether every category hero reads “employer staffing” vs stock lifestyle.

### Do **not** challenge as “missing” if you invent requirements we never claimed

- Live Zoho writeback
- CallRail qualified calls
- WordPress redesign
- Broad match / PMax “for volume”
- Fake AU phone to mirror US

---

## 11. Exact commits / how to spot-check

### Commits (key)

| Hash | What |
|------|------|
| `8705ff05a92ffd89225294c02eb514f5ec1b445c` | Recast category heroes (casting) — **on vision prod** |
| `9b549d01d942885fc3370d256e9ff129510d918d` | Ship Stage 1 category LPs + locked QA defaults + budgets in CSV |
| `d8962fcc014508b757be8f148a99878449a25f44` | v4 ST evidence fold |
| `58c6eac…` / `eeadc7f…` | Earlier RSA/role-first package remediation |

### Spot-check commands (do not trust row counts alone)

```bash
# Casting on live host
curl -sI 'https://vision-three-alpha.vercel.app/us/hr?variant=a' | grep -i link
# Expect va-face-1.jpg preload — not hire-talent.webp

# CSV Final URLs = category paths only
python3 - <<'PY'
import csv
from collections import Counter
rows=list(csv.DictReader(open('ads-launch/google-ads-editor-import.csv',encoding='utf-8-sig')))
print(Counter(r['Final URL'] for r in rows if r.get('Final URL')))
assert not any('?role=' in (r.get('Final URL') or '') for r in rows)
assert not any('[APPROVAL_' in (r.get('Budget') or '')+(r.get('Max CPC') or '') for r in rows)
print('campaigns', len({r['Campaign'] for r in rows}))
print('paused campaigns', Counter(r['Campaign Status'] for r in rows)['Paused'])
PY

# Builder regen (optional)
python3 ads-launch/build_stage1_editor_package.py

# Vision QA
cd vision && npm run typecheck && npm test && npm run build
```

### Human spot-check in Chrome (opened for George)

- All `/us`, `/au`, 9 US + 9 AU categories
- `variant=a` and `variant=b` on US digital-marketing
- Launch Control on xray
- Confirm hero faces, employer CTA language, AU has no phone, US shows 310 number, gate works

### Editor spot-check after import

- 22 campaigns, all Paused
- Sample RSA: no “consult”, no `$/hr`, no “top 1%”
- Final URL host/path match matrix above
- Tracking template = `{lpurl}` only
- Negatives present; bare `hire` / `hiring` / `how to hire a virtual assistant` not blanket-killed

---

## 12. Operator next (not Ads enable)

1. George pastes **this file** into ChatGPT for hostile audit.
2. Replace log-only with real lead delivery before any enable.
3. Optional: buy/attach paid domain → rewrite Final URL **host** only.
4. Import CSV **Paused**; review matrix `09-ads-human-review-matrix.md`.
5. Pause legacy PM_* Brand if still bleeding.
6. Enable only per `07-phased-activation-recommendation.md` after **explicit** George approval.

**Ads remain Off.**

---

*End of mega audit. Shorter index: `ads-launch/FULL-BUILD-REPORT.md`.*
