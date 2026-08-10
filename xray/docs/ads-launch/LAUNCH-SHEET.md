# Launch sheet — Stage 1 v7 (Paused package)

**Status:** Local package ready for review · **Not** launch-ready  
**Preferred CSVs:** `google-ads-editor-import-us.csv` · `google-ads-editor-import-au.csv`  
**LP:** vision microsite category routes · `lp_version=stage1-v7`  
**Architecture:** **2 campaigns × 2 markets** (Brand deferred)

---

## Next Editor step (after Get recent changes)

**USA — agency-intent Exact adds (one step):**

In Google Ads Editor, select the **USA** account (`496-715-1855`), then **Import** → choose file:

`/Users/george/Developer/virtual-coworker/ads-launch/google-ads-editor-agency-intent-keywords-add.csv`

Review the new Exact keywords (Comment = agency-intent). **Keyword Status stays Paused.** Campaign/Ad Group Status columns are blank on purpose so live Enabled campaigns are not paused. Do **not** Enable keywords until George says.

(AU rows are in the same file — import AU later the same way if you want parity.)

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
| US phone (site + Call asset ops) | **310-730-9126** primary (George 2026-08-10; 888 paused — see `DECISIONS.md`) |
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
