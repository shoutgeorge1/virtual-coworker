# Launch sheet — Stage 1 v7 (Paused package)

**Status:** Local package ready for review · **Not** launch-ready  
**Preferred CSVs:** `google-ads-editor-import-us.csv` · `google-ads-editor-import-au.csv`  
**LP:** vision microsite category routes · `lp_version=stage1-v7`  
**Architecture:** **2 campaigns × 2 markets** (Brand deferred)

---

## Next Editor step (after Get recent changes)

**Sitelinks — US + AU (2026-08-10): DONE via API** (6 calls). Do not re-import the sitelink CSVs.

Walkthrough / record: `ads-launch/SITELINK-ADD-2026-08-10.md`

**USA — semantic Exact ad groups (2026-08-09):**

Full walkthrough: `ads-launch/SEMANTIC-ADGROUPS-2026-08-09.md`

1. Import `google-ads-editor-semantic-adgroups-add-us.csv` (4 new Paused AGs + Exact + RSAs)
2. Import `google-ads-editor-semantic-adgroups-pause-dupes-us.csv` (pause overlapping Exact in old AGs)
3. Review locally → Post (still Paused) → Enable one AG at a time (`Staffing_Agency_PH` first)

Campaign Status blank on purpose (live-US-safe). Exact only. No wipe of existing inventory.

**Quiz LP Search (2026-08-09, Paused — review before Import):**

Sheet: `ads-launch/QUIZ-ADS-PACKAGE-2026-08-09.md`  
CSVs: `google-ads-editor-quiz-import-us.csv` / `-au.csv` + quiz campaign-negatives MMC.  
Campaigns: `VC_US_S_QUIZ` / `VC_AU_S_QUIZ` → Final URL `/us/quiz` `/au/quiz`. Enable only when George says.

**Prior add (still valid if not posted):** agency-intent Exact keywords → `google-ads-editor-agency-intent-keywords-add.csv` (many of those terms are now concentrated into the new semantic AGs — prefer the semantic package).

---

## Quick facts

| Item | Value |
|------|-------|
| Campaigns | **4** (Paused) — `VC_{US\|AU}_S_CORE` + `VC_{US\|AU}_S_ROLES` |
| Ad groups | 40 |
| Keywords (positive) | 1628 Exact+Phrase (incl. 60 agency-intent Exact adds US+AU) |
| RSAs | 116 (full 15/4 — no blanks) |
| Unique negatives | 183 curated Broad (+ US-only `VC_Neg_JobSeekers_Live` Phrase) |
| Final URLs | `www.virtualcoworker.app/us\|au` + `/us\|au/{category}` (no WP) |
| US phone (site + Call asset ops) | **888-964-8644** primary (George 2026-08-10 restore — see `DECISIONS.md`) |
| AU phone | **None** — form primary (locked; no Call asset in AU CSV) |
| Careers URL | `/ph` via `NEXT_PUBLIC_CAREERS_URL` (locked for Stage 1) |
| Lead QA | `ALLOW_LOG_ONLY_LEADS=true` — TEMPORARY logs only; Zoho access ≠ integration |
| Editor Account col | USA `496-715-1855` · AU `573-539-1940` stamped on every CSV row |
| Budgets / CPC | US Core **$75** / Roles **$50** · Max CPC **$12** / **$10** · AU Core **A$75** / Roles **A$50** · Max CPC **A$6** / **A$6** |
| Monthly pace | ≈ $3.8k US + A$3.8k AU at these dailies — inside $10–20k/account story |

---

## Before any enable

- [ ] Lead delivery configured (**not** log-only)  
- [x] Careers URL decided (`/ph` — Stage 1 default)  
- [x] AU phone decision (form-primary)  
- [x] Budgets + Max CPC filled (2-campaign defaults; George can change)  
- [x] Architecture locked (2/account; Brand deferred)  
- [ ] GTM maps `employer_inquiry_submitted` carefully  
- [ ] Human review matrix (`09`) signed off  
- [ ] Explicit George approval to enable  

---

## Enable order (after gates green)

**Source of truth:** [`PHASED-ACTIVATION.md`](./PHASED-ACTIVATION.md)

1. US — **PH / Filipino / offshore long-tail** Exact (+ tight Phrase) in Core **and** Roles (incl. bookkeeping/accounting when PH-shaped)  
2. US — broader category Exact/Phrase without PH geo  
3. US — generic Core head terms later (tighter CPC once CTR known)  
4. AU — same pattern after US looks sane (form-primary)  

Never: Broad, PMax, DSA, WP spray, fake Zoho success, Brand until explicitly added. Do **not** hold PH books just because “Controlled.”

---

## Role portraits (site live — Ads later)

AI role/trust PNGs are live on vision LPs + `/services` (`role_imagery` A/B).

**Ads stance (Stage 1 Search):** do **not** upload these via API. Search RSAs don’t need portraits yet.

When ready for Display / PMax / image extensions later:
1. Use files in `ads-launch/assets/role-portraits/` (same set as `~/Downloads/vc-role-*.png`)
2. Attach in **Google Ads Editor** or Ads UI asset library — manual only
3. Never mutate image assets via Google Ads API

Brand deferred. API = read-only / cheap probes only.
