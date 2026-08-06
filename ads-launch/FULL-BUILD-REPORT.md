# Stage 1 Google Ads Editor package — FULL BUILD REPORT

**For:** ChatGPT audit + George operator handoff  
**Generated:** 2026-08-05  
**Remediated:** 2026-08-05 (v3)  
**Package:** `ads-launch/google-ads-editor-import.csv`  
**Builder:** `ads-launch/build_stage1_editor_package.py` (re-runnable)  
**Accounts:** USA `496-715-1855` · Australia `573-539-1940`  
**Status of all entities in CSV:** **Paused**  
**Live Ads mutations:** none (no API, no enable)

> **ChatGPT critique note:** George’s exact ChatGPT critique text was **not in the repo**. This remediation audited against the failure modes George listed (template RSAs, thin keywords, fat AGs, AU clone, empty assets, fake history, fake DKI) and fixed what was actually weak.

---

## 0. Remediation — what was wrong (v2) and what changed (v3)

### Honest verdict on what we shipped before (v2)

ChatGPT’s instinct was fair. The v2 package was structurally complete but creatively lazy:

- **Template RSAs** — “Recruit Vet & Manage”, “Employers Hiring Only”, “Request a Hiring Consult”, “Clear Hiring Path”, “Not a Gig Marketplace” repeated across nearly every role. Descriptions were the same paragraph with the role noun swapped.
- **One fat ad group per role** — `{Role}_PH` mixed hire + outsource + VA language; poor query→creative relevance.
- **Thin keywords** — ~20 Exact + 5 Phrase per role (except admin). Lots of near-duplicate rearrangements; digital marketing missing offshore; Phrase sets were mostly Exact clones.
- **AU ≈ US** — only `US`→`AU` / `US business`→`Australian business`. No AU spelling (`organisation`, `specialise`, `categorisation`) and no SME framing.
- **DKI underdone** — claimed “light DKI” but only Administration had `{KeyWord:…}`; other roles had zero query mirroring.
- **Negatives adequate-but-lazy** — job-seeker/info/medical/tech/spanish covered; missing platform bleed (Wishup/Athena/etc.), `how to`, `meaning`, `vacancies`, `va jobs`, etc.
- **Assets were fine** — callouts / sitelinks / snippets were filled (not empty). Not a real gap.
- **Historical mining was partially honest** — keywords were archaeology-influenced, but the report over-sold uniqueness. No fake CTR/conv claims (that part was clean).
- **Brand deferred + CORE absorbed into Administration** — intentional and kept; admin Hire AG now carries the full hire-VA depth again.

### What v3 fixed

| Gap | Fix |
|-----|-----|
| Template RSAs | Rewrote creatives per role × theme × angle. Shared CTAs capped; builder QA fails if a non-DKI headline appears in >12 US primary RSAs. |
| Fat AGs | Split every role into **Hire_PH** + **Outsource_PH** (Admin: **Hire_PH** + **EA_PH** + city test). |
| Thin KWs | ~48–62 Exact + ~15–25 Phrase per role (US); long-tail hire/outsource/Filipino/offshore/VA variants from Editor archaeology + curation. |
| AU clone | Market-aware copy: Australian / SMEs / organisation / specialise / categorisation where natural. |
| DKI | `{KeyWord:…}` on every Hire/EA **B_role** RSA (20 ads) + city `{LOCATION(City):…}` test. |
| Negatives | Expanded to **113** unique curated Broad negatives (platforms, vacancies, how-to, VA job salary, graphic/web design bleed). |
| LP version | `lp_version=stage1-v3` |

### What we did **not** invent

- No CTR / CPC / conversion rankings (still no performance CSVs).
- No pricing, Top 1%, Save 80%, $/hr.
- No WordPress sitelinks.
- Budgets / Max CPC still `[APPROVAL_*]` only.

---

## 1. Executive verdict (v3)

Stage 1 is **role-first Search** for Philippine remote staffing employers across **nine service lines**. Brand deferred. Every primary theme has keywords + **fully filled unique RSAs** (15H / 4D). Exact + Phrase only. Maximize Clicks. Final URLs → vision microsite `/us` and `/au`. Budgets and Max CPC remain George placeholders.

---

## 2. Historical data — available vs missing

### Available (mined)

| Source | Path | Used for |
|--------|------|----------|
| Editor USA export | `audit-data/editor-exports/virtual-coworker-usa.csv` | Keyword archaeology via `docs/rebuild/_scratch_keywords.json` |
| Editor AU export | `audit-data/editor-exports/virtual-coworker-australia.csv` | Same, AU mirror |
| Editor structure audit | `audit-data/editor-account-audit.md` | Enabled remnant = brand Max Conv → WP |
| Keyword scratch | `docs/rebuild/_scratch_keywords.json` | hire_va_ph / role_specific / bookkeeping employer terms |
| Negative scratch + `03-*.md` | curated job-seeker / info / platform lists | |
| Prior blueprint | `docs/rebuild/02-*.md`, `03-*.md` | Naming, Exact-first, honesty rules |
| Pilot status | `xray/data/pilot-status.js` | Confirmed 9 prioritize roles + excludes |

### Missing (explicit — do not invent)

| Missing | Implication |
|---------|-------------|
| Campaign / keyword / search-term **performance** CSVs | **No CTR/CPC/conv ranking used.** |
| Ads API pulls | Intentionally not used. |
| Live search terms report | Negatives curated from Editor lists + strategy, not live ST. |

**Honesty rule:** Frequency in old Editor structure ≠ “converted” or “high CTR.”

---

## 3. What was kept vs killed from the old account

### Kept (adapted)

| Kept | Why |
|------|-----|
| Employer PH / Filipino / hire / outsource / offshore language | Stage 1 intent |
| Role themes with historical AG presence | Aligns with 9 lines |
| Job-seeker + info + platform negatives | Protects Max Clicks |
| Staffing-partner positioning (no fake pricing) | Supportable |
| Microsite Final URLs vs WP | Rejects contaminated brand→WP pattern |
| Admin absorbs general hire-VA (old CORE depth) | Brand deferred; roles-first |

### Killed / rejected

| Rejected | Why |
|----------|-----|
| Brand campaigns in Stage 1 | Deferred |
| Empty ROLE shells | George hates blanks |
| Medical / tech / Spanish | Explicit exclude |
| Job-seeker positives | Wrong intent |
| Broad positives | Forbidden |
| PMax / DSA / Demand Gen / Display expansion | Out of Stage 1 |
| “Top 1%”, “Save 80%”, $/hr, fake guarantees | Banned |
| WP sitelinks | Contaminated sprawl |
| Wholesale `PM_Generic Non-Qualified` | Opaque choke risk |
| Competitor conquest farms | Deferred |

---

## 4. Final account architecture (v3)

```
USA (496-715-1855)                          AU (573-539-1940)
├─ VC_US_S_ROLE_digital_marketing           ├─ VC_AU_S_ROLE_digital_marketing
│   ├─ Digital_Marketing_Hire_PH            │   ├─ Digital_Marketing_Hire_PH
│   └─ Digital_Marketing_Outsource_PH       │   └─ Digital_Marketing_Outsource_PH
├─ VC_US_S_ROLE_social_media                ├─ … (same shape)
├─ VC_US_S_ROLE_accounting
├─ VC_US_S_ROLE_bookkeeping
├─ VC_US_S_ROLE_administration
│   ├─ Administration_Hire_PH   ← general VA / CORE depth
│   ├─ Administration_EA_PH     ← EA / admin assistant
│   └─ Admin_City_Test          ← light geo Phrase + location RSA
├─ VC_US_S_ROLE_customer_service
├─ VC_US_S_ROLE_hr
├─ VC_US_S_ROLE_recruitment
└─ VC_US_S_ROLE_sales

BRAND: deferred — not in CSV
```

### Per role campaign

| Layer | Spec |
|-------|------|
| Type | Search · **Paused** |
| Networks | Google Search only (confirm partners/Display **OFF**) |
| Geo | US or AU · Presence |
| Language | English |
| Bid | Maximize Clicks · Max CPC = `[APPROVAL_MAX_CPC]` |
| Budget | `[APPROVAL_DAILY_BUDGET_USD]` / `[APPROVAL_DAILY_BUDGET_AUD]` |
| Ad groups | Hire_PH + Outsource_PH (Admin: Hire + EA + City) |
| RSAs | 2 angles per theme AG (A staffing/partner · B role/capacity with DKI on Hire/EA) |
| Assets | 6 callouts · 1 structured snippet · 4 microsite sitelinks |
| Negatives | 113 curated Broad per campaign |

---

## 5. Keyword counts by match type (v3)

| Match | Count (package total) | Notes |
|-------|----------------------:|-------|
| Exact | 896 | ~48–62 per role per market; admin densest |
| Phrase | 290 | Discovery seeds — not Exact clones only |
| Broad (positives) | **0** | Forbidden |
| Campaign negatives (Broad) | 2034 | 113 × 18 campaigns |

**Per market positive keywords:** 593.  
**Builder QA** refuses positive Broad, empty shells, single-AG campaigns, RSA blanks, boilerplate spam, medical/tech/spanish leaks, and bare `hire`/`hiring` negatives.

### Administration note

General “hire Filipino VA / VA Philippines / offshore VA” Exact set lives under **Administration_Hire_PH** (not a separate CORE campaign). EA/admin assistant intent lives under **Administration_EA_PH**.

---

## 6. Negative strategy

### Applied to every role campaign (Broad)

1. **Job seeker** — job(s), salary, career(s), resume/cv, apply, vacancies, indeed/glassdoor/jobstreet, onlinejobs, VA jobs/salary, WFH/online/part-time **job** variants  
2. **Info / DIY** — what is, how to / how to become, tutorial, course(s), training, certification, template, meaning, diy, for beginners  
3. **Junk** — free, cheap(est), torrent, reddit, youtube, pdf, near me  
4. **Platforms** — upwork, fiverr, freelancer, wishup, athena, boldly, myoutdesk, zirtual, bruntwork, onlinejobs ph  
5. **Excluded verticals** — medical/nurse/doctor/healthcare staffing; software/web developer/programmer/coding/IT|tech staffing; graphic designer/web design; spanish/español/bilingual spanish  

### Intentionally NOT negatived

- `hire` / `hiring` alone  
- Bare `work from home` (used `work from home job` instead)  
- Bare `pay` (used `pay rate` / `hourly rate`)

---

## 7. RSA strategy (v3)

### Fill rule

Every RSA: **15 unique headlines ≤30 chars** + **4 unique descriptions ≤90 chars**. Builder fails on blanks or duplicates.

### Angles

| Theme AG | Angles |
|----------|--------|
| `*_Hire_PH` / `Administration_EA_PH` | `A_staffing` + `B_role` (includes `{KeyWord:…}` DKI) |
| `*_Outsource_PH` | `A_partner` + `B_capacity` |
| `Admin_City_Test` | Location-insertion RSA |

### AU vs US

Not a country-token swap. AU uses Australian / SMEs / organisation / specialise / categorisation where natural. US keeps organization / specialize / SMBs.

### Banned claims

Top 1% · Save 80% · $/hr rates · guaranteed / cheapest · fake social proof

---

## 8. Final URLs

| Market | Primary Final URL pattern |
|--------|---------------------------|
| USA | `https://vision-three-alpha.vercel.app/us?role={role}` |
| AU | `https://vision-three-alpha.vercel.app/au?role={role}` |

- Sitelinks: same host only. **No WordPress.**  
- Tracking: UTMs + `lp_version=stage1-v3`  
- Domain TBD when George attaches custom paid domain

---

## 9. Placeholders George must still approve

| Placeholder | Where |
|-------------|-------|
| `[APPROVAL_DAILY_BUDGET_USD]` | Each US campaign Budget |
| `[APPROVAL_DAILY_BUDGET_AUD]` | Each AU campaign Budget |
| `[APPROVAL_MAX_CPC]` | Campaign + AG Max CPC |
| Final URL host | vision-three-alpha until custom domain |
| Enable order | Launch Control — roles after gates green |
| Old live brand | Pause `PM_*_RSA_Brand` is a George click |

---

## 10. Package inventory (v3 machine counts)

| Entity | Count |
|--------|------:|
| Campaigns | 18 |
| Ad groups | 38 |
| Positive keywords | 1186 |
| RSAs | 74 |
| Campaign negative keyword rows | 2034 |
| Callouts | 108 |
| Structured snippets | 18 |
| Sitelinks | 72 |
| **Total CSV rows** | **3548** |

---

## 11. How ChatGPT should spot-check (re-audit)

1. **Open CSV** → `Row Type = Ad` → every row Headline 1–15 + Description 1–4 non-empty.  
2. Confirm **no** `VC_*_S_BRAND` and **no** `ROLE_held_for_evidence`.  
3. Confirm 18 `VC_{US|AU}_S_ROLE_*` campaigns for the nine roles.  
4. Confirm **≥2 ad groups per campaign** (Hire + Outsource; Admin has 3).  
5. Filter positives → Criterion Type only Exact or Phrase.  
6. Grep creatives for `Top 1%`, `$/hr`, `80%`, `guaranteed` — expect zero.  
7. Grep Final URL for `virtualcoworker.com` WP paths — expect zero.  
8. Confirm DKI: many ads contain `{KeyWord:` (not just Administration).  
9. Confirm AU copy uses `Australian` / `specialise` / `organisation` (not US-only swap).  
10. Confirm shared boilerplate is limited — “Recruit Vet & Manage” should **not** appear on nearly every RSA anymore.  
11. Budgets/Max CPC still `[APPROVAL_*]` — correct.  
12. All statuses = Paused.

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

## 13. Files touched this rebuild / remediation

| File | Action |
|------|--------|
| `ads-launch/google-ads-editor-import.csv` | Regenerated (v3) |
| `ads-launch/build_stage1_editor_package.py` | Rewritten (theme split, unique RSAs, denser KWs) |
| `ads-launch/LAUNCH-SHEET.md` | Updated |
| `ads-launch/FULL-BUILD-REPORT.md` | This file (+ Remediation §0) |
| `ads-launch/IMPLEMENTATION-REPORT.md` | Pointer |
| `xray/docs/ads-launch/*` | Mirrored |

---

*End of report — structure archaeology + remediation; no invented performance metrics.*
