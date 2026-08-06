# Virtual Coworker Stage 1 — MEGA AUDIT for ChatGPT (v6)

**Canonical paste:** `ads-launch/CHATGPT-DEBRIEF.md` — **complete whole-package brief** (LPs, URLs, Ads, tracking, blockers).  
This file is the deep companion. Prefer the debrief first; use MEGA for extra depth. Ask ChatGPT to challenge honesty, conversion definitions, Final URL/path integrity, Ads package hygiene, and remaining launch blockers — not to rewrite copy for vibes.

| Field | Value |
|-------|-------|
| Date | 2026-08-05 |
| Branch | `vision-demo` |
| Repo | `/Users/george/Developer/virtual-coworker` |
| LP host (preview) | `https://vision-three-alpha.vercel.app` |
| Launch Control | `https://vc-xray.vercel.app/launch-control` |
| Ads package | `ads-launch/google-ads-editor-import.csv` · `lp_version=stage1-v6` · **RSA×3/main AG** |
| LP engine | `vision/config/categories.ts` + `MarketLanding` / `LeadGate` |
| Casting commit | `8705ff05a92ffd89225294c02eb514f5ec1b445c` — **deployed** to vision production |
| Architecture | **2 campaigns × 2 markets** — Brand **deferred** |
| WordPress | **Untouched** — paid traffic must not use WP Final URLs |
| Ads enable | **NOT approved** — all Stage 1 CSV entities **Paused** |

---

## 0. Executive honesty

We built a **paid Search microsite + Paused Editor package** so US/AU employer hiring intent can land on category-specific LPs with honest inquiry tracking.

**v6 architecture (George-approved):** per account, **Core (~60%) + Roles (~40%)** only. Brand deferred.

We did **not**:

- Enable any Stage 1 campaign
- Include Brand Search in this CSV
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
| **WordPress (virtualcoworker.com)** | Legacy marketing site | **Out of Stage 1 paid path** |
| **Zoho / CallRail / GTM Ads convert** | Downstream | Not launch-ready |

### 1.2 Campaign shape (v6 — locked)

```
VC_{MKT}_S_CORE     (~60%)  Hire_VA_PH · Offshore_VA_PH
VC_{MKT}_S_ROLES    (~40%)  Digital · Social · Admin · Controlled
                            Controlled = accounting, bookkeeping, CS, HR, recruitment, sales
```

**Why not 22 campaigns:** Stage 1 ops/budget control. v5 had Brand + Core + 9 role campaigns; George approved collapse to 2/account with Brand deferred.

### 1.3 Key repo paths

```
vision/                          # Next.js LP app
ads-launch/
  google-ads-editor-import.csv   # v6 Paused package
  build_stage1_editor_package.py
  CHATGPT-DEBRIEF.md             # primary paste
  CHATGPT-MEGA-AUDIT.md          # THIS FILE
  DECISIONS.md · LAUNCH-SHEET.md · FULL-BUILD-REPORT.md
xray/launch-control.html
audit-data/performance/          # ~2y Editor exports (UTF-16)
```

---

## 2. Business model / Stage 1 conversion truth

Virtual Coworker is an **offshore staffing partner** (Philippines talent) for **employers** — not a freelance marketplace, not a job board, not SaaS “book a demo.”

Stage 1 paid funnel sells **hiring inquiries**:

1. Employer lands on category LP
2. Gate: employer vs job seeker
3. Job seeker → careers divert (`NEXT_PUBLIC_CAREERS_URL=/ph`) — **never** primary Ads conversion
4. Employer → role + details → `POST /api/lead`
5. Server validates → delivery channel OR (QA only) log-only
6. Thank-you page; dataLayer event `employer_inquiry_submitted`

---

## 3. Live LP URLs (Stage 1)

**Host:** `https://vision-three-alpha.vercel.app`  
**Casting:** commit `8705ff05a92ffd89225294c02eb514f5ec1b445c` on production.

### Generics (exist; Brand ads deferred so not used as Final URLs in CSV)

| URL | Market | Phone |
|-----|--------|-------|
| https://vision-three-alpha.vercel.app/us | US | `310-426-8776` |
| https://vision-three-alpha.vercel.app/au | AU | **None** — form primary |

### Category routes (9 × 2) — Ads Final URLs

`/us|au/{digital-marketing|social-media|accounting|bookkeeping|administrative-support|customer-service|hr|recruitment|sales}`

Core → `administrative-support`. Roles AGs → matching category slug.

### A/B QA

`?variant=a|b` · cookie `vc_ab_variant` · 90 days.

### Casting map

George approved: **“all hot / beer-with dude / variety good.”**  
Must **not** be `marketing.webp`, `hire-talent.webp`, `ea.jpg`, `va-team.webp`.  
Must be from: `va-au.jpg | talent-john.jpeg | va-ph.jpg | va-face-1|2|3.jpg | support.jpg | va-us.jpg`.

---

## 4. Form / gate / tracking / lead delivery

| Event | Ads primary? |
|-------|--------------|
| `employer_inquiry_submitted` | **Candidate** (not job order) |
| `phone_cta_clicked` | Secondary; `is_qualified_call: false` |
| `job_seeker_diverted` | **Never** |

**Current prod:** `ALLOW_LOG_ONLY_LEADS=true` (**TEMPORARY QA**) · careers `/ph` · Ads conversions **false** · no AU phone · **no** real inbox for paid.

**Do not claim leads land in a human inbox today.**

---

## 5. Historical ST evidence summary

| Account | Cost | Clicks | Conversions | All conv | ST raw → deduped |
|---------|-----:|-------:|------------:|---------:|-----------------:|
| USA `496-715-1855` | $723,838.59 | 87,060 | 2,597.32 | 4,629.39 | 66,869 → 66,465 |
| AU `573-539-1940` | $457,489.46 | 49,457 | 1,412.66 | 3,505.46 | 26,211 → 26,132 |

**All conv ≫ Conversions** — neither is job orders.

Keep / kill clusters and limitations: see DEBRIEF §3 and `03-search-term-category-findings.md`.

---

## 6. Ads package inventory (all Paused) — v6

| Entity | Count | Status |
|--------|------:|--------|
| Campaigns | **4** | Paused |
| Ad groups | **40** | Paused |
| Positive keywords | **1,568** (Exact 1,182 · Phrase 386) | Paused |
| RSAs | **116** (3/main AG · city 1) | Paused |
| Campaign negative rows | **764** (191 unique × 4) | Broad |
| Callouts / sitelinks / snippets | 24 / 16 / 4 | |
| **CSV rows** | **2,498** | |

### Budgets / CPC

| Market | Core | Roles | Max CPC | ~Monthly at placeholders |
|--------|-----:|------:|--------:|-------------------------:|
| US | $75 | $50 | $8 | ≈ $3.8k (inside $10–20k/account story) |
| AU | A$75 | A$50 | A$6 | ≈ A$3.8k |

Tracking: template `{lpurl}` only · Final URL suffix UTMs + `lp_version=stage1-v6` (**once**).

**Still live outside this CSV (Aug 5 Ads UI read):** legacy `PM_US_RSA_Brand` / `PM_AU_RSA_Brand` — recommend pause.

---

## 7. Decisions locked

| Decision | Locked value |
|----------|--------------|
| Architecture | 2/account; Brand deferred |
| AU phone | Form-primary |
| US phone | `310-426-8776` |
| Careers URL | `/ph` |
| Lead delivery (QA) | Log-only TEMPORARY |
| Ads conversions | Observe-only (`false`) |
| US budgets | Core $75 · Roles $50 |
| AU budgets | Core A$75 · Roles A$50 |
| Max CPC | US $8 · AU A$6 |
| Google Ads enable | **Not approved** |

---

## 8. Known fuck-ups we fixed (v1→v6)

| Fuck-up | Fix |
|---------|-----|
| Double UTM | Template `{lpurl}` only; suffix once |
| Inert `?role=` Final URLs | Category routes + middleware 308 |
| Template / boilerplate RSAs | Unique RSAs; QA rejects spam + blanks |
| Fake AU phone | Form primary |
| Consult / SaaS language | Employer staffing CTAs |
| Plastic / white-HR heroes | Recast (`8705ff0`) |
| Silent log-only default | 503 unless channel or explicit flag |
| Dishonest event names | Inquiry / phone_cta / divert |
| v5: 22-campaign sprawl | **v6: 2 campaigns/account**; Brand deferred; Core owns VA cluster |

---

## 9. What ChatGPT should challenge

1. Log-only for paid? (**No.**)  
2. Core → administrative-support Final URL for hire-VA?  
3. Max CPC + $75/$50 vs historical CPC / $10–20k story?  
4. Controlled HR/recruitment thin ST — strip or delay?  
5. RSA invent savings/credentials?  
6. Legacy PM_* Brand still Enabled?  
7. Conversion mapping poison risk?  
8. Custom domain missing?  
9. Careers `/ph` divert quality?  
10. Is Brand deferral correct for Stage 1?

### Do **not** invent as “missing”

Live Zoho · CallRail qualified calls · WP redesign · Broad/PMax volume · Fake AU phone · Brand in this CSV

---

## 10. Spot-check

```bash
python3 ads-launch/build_stage1_editor_package.py
# Expect: 4 campaigns, ~2536 rows, 116 RSAs, QA OK, lp_version stage1-v6

curl -sI 'https://vision-three-alpha.vercel.app/us/hr?variant=a' | grep -i link
# Expect va-face-1.jpg — not hire-talent.webp
```

Editor after import: **4** campaigns, all Paused · no consult · Final URLs category paths · `{lpurl}` only · bare `hire` / `hiring` / `how to hire a virtual assistant` not blanket-killed.

---

## 11. Operator next

1. Paste **CHATGPT-DEBRIEF.md** (then this MEGA if needed).  
2. Real lead delivery before enable.  
3. Import **Paused**.  
4. Pause legacy PM_* Brand.  
5. Enable per `07` after **explicit** George approval.

**Ads remain Off.**

---

*End of mega audit (v6). Primary paste: `CHATGPT-DEBRIEF.md`. Index: `FULL-BUILD-REPORT.md`.*
