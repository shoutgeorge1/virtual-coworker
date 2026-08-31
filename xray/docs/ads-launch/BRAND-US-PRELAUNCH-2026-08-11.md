# PRE-LAUNCH PLAN — `VC_US_S_BRAND`

**Date:** 2026-08-11  
**Superseded for settings:** 2026-08-13 audit — `BRAND-US-DEFENSE-AUDIT-2026-08-13.md` (TIS 85% · Max CPC $12 · $15/day placeholder · `/contact-us/` sitelink · tighter keywords).  
**Status:** Plan + Editor CSVs only. **Paused.** Do not Enable. No Ads API mutate.  
**AU:** Do not create `VC_AU_S_BRAND` in this pass.

This is a controlled brand-defense layer. It is not a vanity campaign and it is not mixed into CORE/ROLES.

---

## What already exists (do not distort CORE to please one search)

| Item | Finding |
|------|---------|
| Live US brand targeting | `Brand_VC` **Enabled** inside `VC_US_S_CORE` (AG id `205906384984`). 36 Exact+Phrase. 3 RSAs to `https://www.virtualcoworker.app/us`. |
| Isolated US brand campaign | **None.** Coverage today pollutes CORE Maximize Clicks metrics. Cannot run Target Impression Share on one ad group inside CORE. |
| Isolated US brand CPC / IS | **Not in repo.** No Ads API dump this pass. |
| US CORE last-7 (campaign, mixed) | ~$592 spend · avg CPC ~$2.74 · Max CPC cap $12 · Maximize Clicks. Brand queries are mixed in — do not treat this as brand CPC. |
| AU legacy `PM_AU_RSA_Brand` | Paused remnant. Last-7 avg CPC **$14.75** — **not** a US cap. Different market. |
| Shared PM_* negative mega-lists | Do **not** attach. Conflict risk on branded nav (staffing / contact / reviews / pricing / services). |
| US call asset | `(888) 964-8644` live on CORE/ROLES. Attach the **same** number to `VC_US_S_BRAND` in Editor after import. Do not invent a new number. |
| Conversion actions | US employer form + website-call 60s + ad-call 60s exist for **microsite**. `.com` Ads/GA4/call tags are **not verified** in this pass. |

**Conflict to resolve before Enable:** pause `Brand_VC` in CORE so two brand systems do not bid against each other.

---

## Architecture

| Field | Launch value |
|-------|----------------|
| Campaign | `VC_US_S_BRAND` |
| Ad group | `BRAND_CORE` (one AG — do not fragment) |
| Network | Google Search only. **No Search Partners.** |
| Geo | United States · **Presence** (people in or regularly in the US). Not “interested in.” |
| Languages | en |
| Status | **Paused** until George Enables |
| Budget | **$25/day dedicated** (hypothesis). Separate from CORE $75 + ROLES $50. |
| Bidding | **Target Impression Share** · **Top of page** · **90%** · Max CPC **$8** |
| Match | Exact + one Phrase `"virtual coworker"`. **No Broad.** |
| Final URL | `https://www.virtualcoworker.com/` (corporate homepage) |
| RSA pinning | **None** |
| AU | Not this package |

### Why $8 Max CPC (sparse — review days 2–3)

- No isolated US brand CPC, top-of-page CPC, or impression-share history in the repo.
- US CORE mixed avg CPC ~$2.74; CORE campaign cap is $12.
- Brand should usually be cheaper than nonbrand. $8 is a **guardrail** so TIS can reach top-of-page without Absolute Top vanity, and without using AU legacy $14.75.
- If Search Lost IS (Rank) stays high after 2–3 days, raise the cap. If Lost IS (Budget) is the constraint, raise daily budget only if the extra coverage is worth it.
- Do **not** start at 100% Absolute Top.

### Why $25/day

Enough that a thin branded query set should not be budget-starved. Watch Search Lost IS (Budget). Do not raise just to hit 100%.

---

## Keywords (tight)

**Exact**

- `[virtual coworker]`
- `[virtualcoworker]`
- `[virtual coworker staffing]`
- `[virtual coworker philippines]`
- `[virtual coworker reviews]`
- `[virtual coworker virtual assistant]`
- `[virtual coworker virtual assistants]`
- `[virtual coworker usa]`
- `[virtual coworker us]`
- `[virtual coworker contact]`
- `[virtual coworker pricing]`
- `[virtual coworker services]`

**Phrase**

- `"virtual coworker"`

**Not in launch**

- Broad match
- Misspelling farms (Exact close variants cover those)
- `[virtual coworker careers]` — job-seeker path; negative instead
- VA abbreviation as a keyword

---

## Negatives (brand-specific list)

Ship in `google-ads-editor-brand-negatives-us.csv` → Editor **Keywords, Negative → Make multiple changes**. Do **not** Account-import those rows (AU lesson: dual-write as positive Broad).

Included: job / jobs / careers / career / salary / salaries / apply / application / resume / cv / vacancy / vacancies / work from home / virtual assistant jobs / philippines jobs / remote jobs / employee login / applicant login / BPO / call center variants / va jobs / job opening(s).

**Deliberately omitted**

| Term | Why |
|------|-----|
| `hiring` (bare) | Can block employer “virtual coworker hiring.” Add only if search terms prove job-seeker junk. |
| `philippines` | Conflicts with `[virtual coworker philippines]`. |
| `recruitment` | Employer nav. |
| Entire PM_* mega list | Over-block risk. |

Review search terms **daily** in week 1.

---

## RSA (unpinned)

15 headlines / 4 descriptions. Claims checked against live VC copy: since 2011, dedicated Filipino staff, FT/PT, client time zone, not a freelancer marketplace, recruit + support. **No** pricing, guarantees, review counts, or staffing counts.

Landing path: homepage. Contact is a **sitelink**, not a second RSA yet (keeps impression-share reporting on one campaign).

**Later LP test (same campaign, not a second campaign):** A homepage vs B `/contact/`. C `virtualcoworker.app` only if the microsite clearly beats `.com`. Do not assume C wins.

---

## Sitelinks (`.com` only)

| Link | URL |
|------|-----|
| Book Consultation | `/contact/` |
| How It Works | `/how-it-works/` |
| Services | `/services/` |
| About Us | `/about/` |

No quiz. No `.app` sitelinks on this campaign. Role pages skipped until a specific branded query cluster justifies them.

**Call asset:** attach existing US `888-964-8644` in Editor after import (no Call row in this CSV schema).

---

## Tracking — blocker before Enable

Branded clicks go to **WordPress `.com`**, not the microsite.

Before Enable, George (or a tagged walkthrough) must confirm on `.com`:

- [ ] Google Ads conversion tag / gtag present
- [ ] GA4 firing
- [ ] Phone tracking / forwarding if used
- [ ] Form submit measured
- [ ] gclid / UTM survive the Gravity Form
- [ ] Cross-domain not wiping source

Until that is true, **leave Paused.** Enabling brand into an unmeasured `.com` is spend without a consultation signal.

Do not attach legacy Zoho/Zapier conversion actions. Primary wins remain: employer form, qualified phone (60s), booked consultation when available. No micro-conversion inflation.

---

## Editor files (this package)

| File | Action |
|------|--------|
| `google-ads-editor-brand-us.csv` | Account Import — new **Paused** campaign + AG + keywords + RSA + sitelinks |
| `google-ads-editor-brand-negatives-us.csv` | **Keywords, Negative → Make multiple changes** only |
| `google-ads-editor-brand-pause-core-ag-us.csv` | Account Import — pause `Brand_VC` in CORE. Campaign Status **blank** (does not pause CORE) |

Rebuild: `python3 ads-launch/build_us_brand_campaign.py`

### TIS in Editor after import

CSV sets Bid Strategy Type = `Target impression share` and Maximum CPC bid limit = `8`. Editor may not apply **location / 90%** from this template.

After import, on the campaign: Bid strategy → Target impression share → **Top of page** → **90%** → Max CPC **$8**.

---

## Launch checklist (Enable only after all true)

- [ ] Campaign is US only, Search only, Presence geo
- [ ] Brand-only keywords, no Broad
- [ ] Job-seeker negatives posted (Keywords, Negative MMC)
- [ ] TIS = Top of page 90% + $8 cap
- [ ] RSA unpinned; URLs load; contact form works
- [ ] Call asset 888-964-8644 attached; call conversions still the 60s actions
- [ ] `.com` Ads/GA4/form/gclid verified
- [ ] Own $25/day budget
- [ ] `Brand_VC` in CORE is **Paused**
- [ ] CORE/ROLES Maximize Clicks unchanged

---

## First-week protocol

Daily: search terms, spend, CPC, IS / top IS / abs top IS, Lost IS rank, Lost IS budget, CTR, LP behavior, calls/forms, job-seeker junk.

Do **not** change bids because Braden searched once. Coverage = Search Impression Share, not one SERP.

Raise Max CPC only if Lost IS (Rank) is the constraint and economics justify it. Add negatives from real terms.

---

## Reporting

Dashboard KPI: **Brand search coverage** = Search Impression Share.

Always split **BRAND · NONBRAND · TOTAL**. Brand CTR/CPC/CVR will look better. That is not CORE improving.

AU brand later: `VC_AU_S_BRAND` only after US is operating correctly.
