# 02 — USA + AU v1 Search campaign blueprint

**Scope:** Clean Search only. No PMax, Demand Gen, DSA, broad match, or large competitor build.  
**Budgets:** Not invented. Set by George after spend owner + payment confirmed. Legacy Editor budget fields (USA 100 / AU 30) are **structure only**, not recommendations.  
**Bidding at launch:** Maximize Clicks (Stage 1) — see `09-bidding-migration-ladder.md`.

---

## Naming convention

```
VC_{MKT}_S_{INTENT}_{theme}
```

| Token | Values |
|-------|--------|
| `MKT` | `US` · `AU` |
| `S` | Search |
| `INTENT` | `BRAND` · `CORE` · `ROLE` |
| `theme` | short snake or Title Case AG name |

Examples: `VC_US_S_BRAND` · `VC_US_S_CORE_hire_va` · `VC_US_S_ROLE_bookkeeping`

Shared negative lists: `VC_SHARED_NEG_jobseeker` · `VC_SHARED_NEG_info` · `VC_SHARED_NEG_platforms`

---

## Architecture per market (identical shape)

| Layer | Campaigns | Purpose | Launch? |
|-------|-----------|---------|---------|
| **Brand** | 1 | Protect brand / navigate known-intent | Yes |
| **High-intent core** | 1 | Hire VA / PH VA / offshore staffing employer queries | Yes |
| **Role intent** | 3–5 max | Role-specific hire intent with dedicated AG + RSA | Yes (start with ≤3) |
| **Deferred** | Document only | Competitors · broad generic · DSA leftovers · Display · PMax · NZ · RLSA sprawl | No |

**Ad group rule:** One strong theme per AG · **one RSA** · Exact at launch · Phrase only after search-term QA · **no broad**.

**Final URL rule:** Every ad + sitelink in a market → **one canonical paid LP** (see `04-paid-lp-requirements.md`). No WP homepage/services spray.

---

## USA — `496-715-1855`

### Account settings (launch)

| Field | Spec |
|-------|------|
| Currency | As account (confirm in UI — Unknown until Admin view) |
| Time zone | As account |
| Auto-apply recommendations | **Off** (esp. broad match, DSA, PMax, budget) |
| Networks | **Google Search only** — Search Partners **Off** · Display **Off** |
| Location | United States · Presence: **People in or regularly in** |
| Language | English |
| IP exclusions | Add known spam ranges later from CallRail/form logs |
| Conversion goals (primary) | **None for bidding** at Stage 1 — observe only; see event map |
| Remarketing lists for search ads | Off at v1 |

### Campaign 1 — `VC_US_S_BRAND`

| Field | Spec |
|-------|------|
| Type | Search |
| Status at build | Paused until checklist green |
| Bid strategy | Maximize Clicks |
| Max CPC bid limit | **TBD** — set only after keyword CPC evidence; else leave blank / soft manual review daily |
| Daily budget | **TBD** (George) |
| Ad schedule | All days; tighten after hour-of-day data |
| Start/end | Start on launch day · no end |
| Final URL suffix | `utm_source=google&utm_medium=cpc&utm_campaign={_campaign}&utm_content={_adgroup}&utm_term={keyword}` (or GTM/Ads value-track equivalent) |
| EU political ads | N/A |

**Ad group:** `Brand`  
**Keywords (Exact):**  
`[virtual coworker]` · `[virtual coworker usa]` · `[virtual coworker staffing]` · `[virtual coworker reviews]` · `[virtual coworker pricing]` · `[virtualcoworker]`  

**RSA:** One RSA — adapt verified enabled-brand copy (structure source: Editor `PM_US_RSA_Brand`):

| Asset | Content |
|-------|---------|
| H | Virtual Coworker Official · Virtual Coworker™ · Virtual Coworker USA · World-Class Filipino VAs · White-Glove VA Service · Hire Offshore Staff · Build A Remote Team · Recruit Vet & Manage · USA-Based Staffing Firm · Scale Without Overhead · No Bulk VA Marketplace · Long-Term Team Members · Operate In Your Timezone · High-Performing VAs · 14 Years Recruitment |
| D | World-class Filipino VAs delivered with white-glove service. · We recruit, vet & manage your team behind the scenes. · Operate in your time zone. Scale without overhead. · Employer hiring only — book a free consultation. |
| Path | `hire` / `usa` |
| Final URL | Canonical US paid LP |

**Sitelinks (LP sections only):** How it works · Pricing · Roles · Book consult — **all same-host paid LP anchors**. No WP, no blog, no `.ph`.  
**Callouts:** Vetted Filipino talent · US-based account team · Recruited & managed · Free consultation  
**Call asset:** US CallRail number only (when live)  
**Structured snippets:** Types: Virtual Assistants, Bookkeepers, Executive Assistants, Social Media Managers, Developers  

### Campaign 2 — `VC_US_S_CORE_hire_va`

| Field | Spec |
|-------|------|
| Type | Search · Search only · US · English |
| Bid | Maximize Clicks · CPC limit TBD |
| Budget | TBD |
| Negatives | Shared jobseeker + info + platforms + campaign-specific |

**Ad groups (launch):**

| AG | Theme | Match |
|----|-------|-------|
| `Hire_VA_PH` | Philippines / Filipino VA hire | Exact |
| `Hire_VA_General` | Employer VA company / hire (no job words) | Exact |

Keywords → see `03-keyword-negative-launch-set.md`.  
**One RSA per AG.** Final URL = canonical US LP. Paths: `philippines` / `va` and `hire` / `va`.

### Campaign 3 — `VC_US_S_ROLE_*` (max 3 at launch)

| Campaign | AG | Launch priority |
|----------|-----|-----------------|
| `VC_US_S_ROLE_bookkeeping` | `Bookkeeping_PH` | 1 — strong commercial fit |
| `VC_US_S_ROLE_ea` | `Executive_Assistant` | 2 |
| `VC_US_S_ROLE_smm` | `Social_Media_VA` | 3 |
| Deferred | Web/dev · CSR · lead gen · content · recruitment assistant | After search-term + lead QA |

Each: Maximize Clicks · Exact · 1 RSA · same US LP (role query param or hash OK: `?role=bookkeeping`).

### USA deferred (do not build v1)

Competitor conquest · OnlineJobs.ph conquest · DSA · PMax · Display/RM · “Generic catch-all” · modified broad · NZ · huge SKAG farms · any Final URL to `virtualcoworker.com` WP.

---

## Australia — `573-539-1940`

Mirror USA with these deltas:

| Field | AU spec |
|-------|---------|
| Location | Australia · Presence: people in or regularly in |
| Language | English |
| Brand KW extras | `[virtual coworker australia]` Exact |
| Brand RSA market lines | Virtual Coworker Australia · Australia-Based Staffing Firm · Operate In Your Timezone |
| Canonical LP | AU paid LP (not US) |
| Call asset | AU CallRail number |
| Currency/budget | TBD in account currency |
| Role set | Same 3: bookkeeping · EA · SMM |

Campaign names: `VC_AU_S_BRAND` · `VC_AU_S_CORE_hire_va` · `VC_AU_S_ROLE_bookkeeping` · `VC_AU_S_ROLE_ea` · `VC_AU_S_ROLE_smm`

---

## Cross-account operating rules

1. **Pause or leave untouched** legacy `PM_*` / museum campaigns until George explicitly chooses pause-all vs coexist. **Recommendation (inference):** pause all non-v1 Search before launch so Max Conv remnants cannot steal budget or poison learning.  
2. **Do not import** old shared sets wholesale — curate into `VC_SHARED_NEG_*` (Editor had useful `PM_Job Seekers` / `Jobseekers` / informational lists — mine, don’t clone).  
3. **US first spend**, AU second — same structure ready; throttle AU budget until US diagnostics look sane.  
4. **No sitelink to WordPress** while paid Search is live.  
5. Job-seeker path on LP must **never** fire employer Ads conversion (see event map + gate plan).

---

## Build sequence (Editor-friendly)

1. Shared negative lists  
2. Brand campaign + AG + KW + RSA + assets  
3. Core campaign + 2 AGs  
4. Role campaigns (≤3)  
5. Conversion actions created but **excluded from bidding** (Stage 1)  
6. Tag Assistant + test clicks (internal)  
7. Enable Brand → Core → Roles over days, not all at once  

**Owner to post:** George (Editor/UI). **Approver:** Braden for claims/budget/phone.
