# Stage 1 Google Ads Editor package — FULL BUILD REPORT

**For:** ChatGPT audit + George operator handoff  
**Generated:** 2026-08-05  
**Package:** `ads-launch/google-ads-editor-import.csv`  
**Builder:** `ads-launch/build_stage1_editor_package.py` (re-runnable)  
**Accounts:** USA `496-715-1855` · Australia `573-539-1940`  
**Status of all entities in CSV:** **Paused**  
**Live Ads mutations:** none (no API, no enable)

---

## 1. Executive verdict

Stage 1 is rebuilt as **role-first Search** for Philippine remote staffing employers in **nine service lines only**. **Brand is deferred** (not in this import). Every ad group has keywords + **fully filled RSAs** (15 headlines / 4 descriptions). Exact + Phrase only. Maximize Clicks. Final URLs → vision microsite `/us` and `/au` (not WordPress). Budgets and Max CPC remain George placeholders.

---

## 2. Historical data — available vs missing

### Available (mined)

| Source | Path | Used for |
|--------|------|----------|
| Editor USA export | `audit-data/editor-exports/virtual-coworker-usa.csv` | Keyword archaeology, RSA angle mining, negative frequency, URL spray patterns, campaign museum map |
| Editor AU export | `audit-data/editor-exports/virtual-coworker-australia.csv` | Same, AU mirror |
| Editor structure audit | `audit-data/editor-account-audit.md` | Enabled remnant = brand Max Conv → WP |
| ChatGPT editor handoff | `audit-data/chatgpt-handoff-editor-audit.md` | Counts / wreck signals |
| Keyword scratch | `docs/rebuild/_scratch_keywords.json` | Structure-frequency positives by theme |
| Negative scratch | `docs/rebuild/_scratch_negatives.json` | Job-seeker / info list candidates |
| Prior blueprint / KW docs | `docs/rebuild/02-*.md`, `03-*.md`, `01-*.md` | Naming, Exact-first policy, honesty rules |
| Prior Stage 1 CSV | replaced `ads-launch/google-ads-editor-import.csv` | Format reference (Row Type schema) |
| Pilot status | `xray/data/pilot-status.js` | Confirmed 9 prioritize roles + excludes |

### Missing (explicit — do not invent)

| Missing | Implication |
|---------|-------------|
| Campaign / keyword / search-term **performance** CSVs (clicks, cost, CTR, conv) | **No CTR/CPC/conv ranking used.** Editor exports have Quality Score / Expected CTR columns as structure fields, not delivery metrics. |
| Ads API pulls | Intentionally not used (quota). |
| Search terms report | Negatives curated from Editor lists + strategy, not from live ST reports. |

**Honesty rule:** Any “strong-looking” keyword below means **appeared often as an Exact/Phrase entity in old Editor structure**, not “converted” or “high CTR.”

---

## 3. What was kept vs killed from the old account

### Kept (adapted)

| Kept | Why |
|------|-----|
| Employer PH / Filipino / hire / outsource / offshore language on role themes | Matches Stage 1 intent |
| Role themes with historical AG presence: digital marketing, social media, accounting, bookkeeping, customer service, recruitment, lead-gen/sales, VA/admin | Aligns with George’s 9 lines |
| Job-seeker + info negative concepts from `PM_Job Seekers` / curated lists | Protects Max Clicks from applicant bleed |
| Staffing-partner RSA angle (recruit / vet / manage / interview shortlist / not marketplace) | Supportable positioning without fake pricing |
| Microsite Final URL direction (`try.*` / vision) vs WP homepage spray | Old enabled brand pointed at WP — that pattern is rejected for v1 |

### Killed / rejected

| Rejected | Why |
|----------|-----|
| **Brand campaigns in Stage 1 import** (`VC_*_S_BRAND`, live `PM_*_RSA_Brand`) | George: brand deferred / do not prioritize |
| Empty `ROLE_held_for_evidence` shells | George hates blank ROLE shells |
| Generic CORE-only package without role depth | Replaced by 9 filled role campaigns; general VA hire lives under **Administration** |
| Medical / nursing / healthcare staffing KWs | Explicit exclude |
| Tech staffing: web/dev, programmer, coding, IT/tech staffing | Explicit exclude |
| Spanish / bilingual Spanish claims | Explicit exclude |
| Job-seeker positives (`…jobs`, salary, careers, home-based job variants) | Wrong intent |
| Broad / modified broad (`+hire +accountant`) | Stage 1 Exact + Phrase only |
| PMax / DSA / Demand Gen / Display expansion / Search partners | Out of Stage 1 |
| RSA claims: “Top 1%”, “Save 80%”, “$7/$8/$10 per hour”, fake guarantees | Unsupported / banned |
| WP sitelinks (`/services/*`, blog, pricing-savings-guide on WP) | Contaminated destination sprawl |
| Wholesale import of `PM_Generic Non-Qualified` mega negatives | Opaque; may choke good queries |
| Competitor conquest farms | Deferred |

---

## 4. Final account architecture

```
USA (496-715-1855)                          AU (573-539-1940)
├─ VC_US_S_ROLE_digital_marketing           ├─ VC_AU_S_ROLE_digital_marketing
├─ VC_US_S_ROLE_social_media                ├─ VC_AU_S_ROLE_social_media
├─ VC_US_S_ROLE_accounting                  ├─ VC_AU_S_ROLE_accounting
├─ VC_US_S_ROLE_bookkeeping                 ├─ VC_AU_S_ROLE_bookkeeping
├─ VC_US_S_ROLE_administration              ├─ VC_AU_S_ROLE_administration
│   ├─ Administration_PH                    │   ├─ Administration_PH
│   └─ Admin_City_Test (light)              │   └─ Admin_City_Test (light)
├─ VC_US_S_ROLE_customer_service            ├─ VC_AU_S_ROLE_customer_service
├─ VC_US_S_ROLE_hr                          ├─ VC_AU_S_ROLE_hr
├─ VC_US_S_ROLE_recruitment                 ├─ VC_AU_S_ROLE_recruitment
└─ VC_US_S_ROLE_sales                       └─ VC_AU_S_ROLE_sales

BRAND: deferred — not in CSV
```

### Per role campaign (identical shape)

| Layer | Spec |
|-------|------|
| Type | Search |
| Status | Paused |
| Networks | Google Search only (confirm Search partners **OFF**, Display expansion **OFF** in Editor/UI) |
| Geo | US or AU · Presence (people in or regularly in) |
| Language | English |
| Bid | Maximize Clicks · Max CPC = `[APPROVAL_MAX_CPC]` |
| Budget | `[APPROVAL_DAILY_BUDGET_USD]` or `[APPROVAL_DAILY_BUDGET_AUD]` |
| Ad group | `{Role}_PH` — Exact + Phrase keywords · **2 RSAs** (angles A/B) |
| Extra AG | Administration only: `Admin_City_Test` |
| Assets | 6 callouts · 1 structured snippet (Types) · 4 microsite sitelinks |
| Negatives | Full curated campaign-level Broad set (same list on every role campaign) |

### Ad group themes

| Campaign suffix | Ad group | Theme |
|-----------------|----------|-------|
| digital_marketing | Digital_Marketing_PH | Hire/outsource Filipino digital marketing / marketing VA |
| social_media | Social_Media_PH | Social media VA / SMM Philippines |
| accounting | Accounting_PH | Accountant / accounting outsourcing PH |
| bookkeeping | Bookkeeping_PH | Virtual bookkeeper / books outsourcing PH |
| administration | Administration_PH | General VA hire + admin/EA (absorbs old CORE) |
| administration | Admin_City_Test | Light city Phrase + location-insertion RSA |
| customer_service | Customer_Service_PH | CS / support outsourcing PH |
| hr | Human_Resources_PH | Virtual HR assistant / HR support PH |
| recruitment | Recruitment_PH | Recruitment assistant / TA support PH |
| sales | Sales_PH | Lead gen / appointment setter / sales assistant PH |

---

## 5. Keyword counts by match type

| Match | Count (package total) | Notes |
|-------|----------------------:|-------|
| Exact | 392 | 196 per market (20 Exact × 9 roles × 2? — Administration has 36 Exact; others 20) |
| Phrase | 104 | Role Phrase subsets + 5 city Phrase × 2 markets on Admin_City_Test |
| Broad (positives) | **0** | Forbidden in Stage 1 |
| Campaign negatives (Broad) | 1512 | 84 negatives × 18 campaigns |

**Per market positive keywords:** 248 (Exact+Phrase including city test).  
**Builder QA** refuses positive Broad and empty campaign shells.

### Administration note

General “hire Filipino VA / VA Philippines / offshore VA” Exact set lives under **Administration** (not a separate CORE campaign), because brand/CORE-first is deferred and George asked for the **nine roles only**.

---

## 6. Negative strategy

### Applied to every role campaign (Broad negatives)

Buckets:

1. **Job seeker** — job(s), salary, career(s), resume/cv, apply/application, indeed/glassdoor/jobstreet, onlinejobs, “virtual assistant jobs/salary”, WFH/online/part-time **job** variants  
2. **Info / DIY** — what is, how to become, tutorial, course(s), training, certification, template, diy  
3. **Junk** — free, cheap(est), torrent, reddit, youtube, pdf  
4. **Platforms** — upwork, fiverr, freelancer.com (protect intent; not conquest)  
5. **Excluded verticals / language** — medical/nurse/doctor/healthcare staffing; software/web developer/programmer/coding/IT|tech staffing; spanish/español/bilingual spanish  

### Intentionally NOT negatived

- `hire` / `hiring` alone — would choke employer demand  
- Bare `work from home` — used `work from home job` instead  
- Bare `pay` — used `pay rate` instead  

### Not imported wholesale

- `PM_Generic Non-Qualified` and other opaque mega-lists  

---

## 7. RSA strategy + angles per ad group

### Fill rule

Every RSA: **15 unique headlines ≤30 chars** + **4 unique descriptions ≤90 chars**. Builder fails if any blank slot.

### Banned claims (stripped from historical copy)

- Top 1% · Save 80% · $/hr rates · guaranteed / cheapest · fake social proof counts

### Angles (2 RSAs on each primary AG)

| Angle | ID | Job |
|-------|----|-----|
| Staffing partner | `A_staffing` | Recruit/vet/manage · interview shortlist · not marketplace · employer consult |
| Role specialist | `B_role` | Role-specific benefit language · outsource/hire framing · dedicated capacity |

### DKI / city tests (light — documented)

| Where | What | Why limited |
|-------|------|-------------|
| Administration · RSA `B_role` | One DKI headline `{KeyWord:Hire Filipino VA}` | Learn query mirroring on highest-volume admin/VA theme only |
| Administration · `Admin_City_Test` | Phrase city KWs (US: NY/LA/Chicago/Texas/Florida · AU: Sydney/Melbourne/Brisbane/Australia/Perth) + RSA with `{LOCATION(City):Hire Filipino VA}` | Light geo creative test; same LP |

No city farms on other roles.

---

## 8. Final URLs

| Market | Primary Final URL pattern |
|--------|---------------------------|
| USA | `https://vision-three-alpha.vercel.app/us?role={role}` |
| AU | `https://vision-three-alpha.vercel.app/au?role={role}` |

- Sitelinks: same host only (`#gate`, base `/us`|/au`, role query). **No WordPress.**  
- Final URL suffix / tracking template: UTMs + `lp_version=stage1-v2`  
- Domain TBD: replace host when George buys/attaches custom paid domain on Vercel  

---

## 9. Placeholders George must still approve

| Placeholder | Where | Notes |
|-------------|-------|-------|
| `[APPROVAL_DAILY_BUDGET_USD]` | Each US campaign Budget | Not invented |
| `[APPROVAL_DAILY_BUDGET_AUD]` | Each AU campaign Budget | Not invented |
| `[APPROVAL_MAX_CPC]` | Campaign + AG Max CPC | Max Clicks ceiling |
| Final URL host | All ads/sitelinks | vision-three-alpha until custom domain |
| Enable order | Launch Control | Suggest US roles after gates green; AU throttle |
| Old live brand | Ads UI | `PM_US_RSA_Brand` / `PM_AU_RSA_Brand` still may spend — pause is a George click |

---

## 10. Package inventory (machine counts)

| Entity | Count |
|--------|------:|
| Campaigns | 18 |
| Ad groups | 20 |
| Positive keywords | 496 |
| RSAs | 38 |
| Campaign negative keyword rows | 1512 |
| Callouts | 108 |
| Structured snippets | 18 |
| Sitelinks | 72 |
| **Total CSV rows** | **2282** |

---

## 11. How ChatGPT should spot-check (no blanks)

1. **Open CSV** → filter `Row Type = Ad` → every row must have Headline 1–15 and Description 1–4 non-empty.  
2. Confirm **no** `VC_*_S_BRAND` and **no** `ROLE_held_for_evidence`.  
3. Confirm campaigns are exactly the 18 `VC_{US|AU}_S_ROLE_*` names for the nine roles.  
4. Filter positive keywords → Criterion Type only Exact or Phrase.  
5. Grep creatives for `Top 1%`, `$/hr`, `80%`, `guaranteed` — expect zero.  
6. Grep Final URL for `virtualcoworker.com` WP paths — expect zero (vision host only).  
7. Confirm negatives include medical/tech/spanish buckets and do **not** include bare `hire`/`hiring`.  
8. Administration must contain general hire-VA Exact set + city test AG.  
9. Budgets/Max CPC should still show `[APPROVAL_*]` placeholders — that is correct.  
10. All Campaign Status / Ad Group Status / Keyword Status / Ad Status = Paused.

---

## 12. Operator enable guidance (after approvals)

1. Import CSV in Editor (split US vs AU rows or import then delete other market).  
2. Replace budget + Max CPC placeholders.  
3. Confirm networks/geo/presence.  
4. Confirm Final URL host.  
5. Post **Paused** → UI spot-check.  
6. Enable only after Launch Control gates green — **roles**, not brand.  
7. First 14 days: search-term mining → add negatives / promote Exact variants. Never Broad to “fix” volume.

---

## 13. Files touched this rebuild

| File | Action |
|------|--------|
| `ads-launch/google-ads-editor-import.csv` | Replaced |
| `ads-launch/build_stage1_editor_package.py` | Added (source of truth generator) |
| `ads-launch/LAUNCH-SHEET.md` | Updated (role-first, brand deferred) |
| `ads-launch/FULL-BUILD-REPORT.md` | This file |
| `ads-launch/IMPLEMENTATION-REPORT.md` | Updated pointer |
| `xray/docs/ads-launch/*` | Mirrored |
| `xray/launch-control.html` | Step 6 / enable / glance copy |
| `xray/data/pilot-status.js` | Keyword cluster labels |

---

*End of report — structure archaeology only; no invented performance metrics.*
