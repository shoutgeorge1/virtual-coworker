# Semantic Exact ad groups — 2026-08-09

**Goal:** New Exact-only ad groups from live US search-term clusters, imported via Google Ads Editor without wiping anything live.

**API:** 1 read-only `search_term_view` call · US `496-715-1855` · `LAST_7_DAYS` · saved as `_last7_search_terms.json` (231 rows / 178 unique terms).

**Landing pages:** Reuse existing. No new LP in this pass.

| New ad group | Campaign | Final URL |
|--------------|----------|-----------|
| `Staffing_Agency_PH` | `VC_US_S_CORE` | `/us` |
| `VA_Agency_Firm_PH` | `VC_US_S_CORE` | `/us` |
| `Virtual_Staff_PH` | `VC_US_S_CORE` | `/us` |
| `Appointment_Setter_Hire_PH` | `VC_US_S_ROLES` | `/us/sales` |

---

## A. Why these four (from live terms)

Directional only — conversion volume still too thin for statistical claims.

| Cluster | 7d signal | Why a new AG |
|---------|-----------|--------------|
| Remote / offshore **staffing agency** | `remote staffing agencies` $10 / 4c · `remote staffing agency` $5 / 2c | Cleanest employer/provider intent; was leaking into generic `Hire_VA_PH` RSAs |
| **VA agency / firm / company** | Impressions on `virtual assistant agency` (+usa) | Provider-shopping language; deserves agency RSA hypothesis (agency-intent keywords were dumped into Hire/Offshore) |
| **Virtual staff** | `virtual staff` / `virtualstaff ph` ~$9 / 4c | Distinct shorthand; was landing in Admin/Offshore AGs |
| **Appointment setter** (employer Exact) | Setter cluster ~$19 / 5c but mostly WFH/job junk | Real sales-support demand; isolate employer Exact → `/us/sales`, leave WFH to negatives |

**Not promoted into a new AG**

- `va workers ph` — watch/pause landmine (botty / weird shorthand). Do not build a family around it.
- Pure job-seeker terms (`virtual assistant jobs`, WFH setters) — negatives / George ST work, not positives.
- Admin remote / virtual bookkeeper / CS outsource / DM agency PH — already sitting in the right role AGs.

---

## B. Files (Editor)

| File | What it does |
|------|----------------|
| `google-ads-editor-semantic-adgroups-add-us.csv` | **ADD** 4 Paused AGs + 58 Exact keywords (Paused) + 12 RSAs (Paused) |
| `google-ads-editor-semantic-adgroups-pause-dupes-us.csv` | **Pause** overlapping Exact keywords in `Hire_VA_PH` / `Offshore_VA_PH` / `Sales_*` so the themed AG owns them |
| `build_semantic_adgroups_add.py` | Regenerator |

Safety baked into CSVs:

- Campaign Status / Budget blank → will not pause or rewrite live campaigns
- New AGs + keywords + RSAs all **Paused** until you enable
- Exact only (no Phrase in this package)
- No campaign-negative rows (avoids blank/`Unkown` Broad dual-write)

---

## C. Editor walkthrough (USA only — one careful path)

Do this in Google Ads Editor after your Phrase / search-term work, or before — either order is fine. This import only **adds** Paused inventory.

### Step 1 — Sync

1. Open Google Ads Editor.
2. Select the **USA** account (`496-715-1855` / Virtual Coworker US).
3. **Get recent changes** so Editor matches live.

### Step 2 — Import the new ad groups (ADD file)

1. Still on the USA account.
2. **Account → Import → From file…** (Mac: ⌘I). If grayed out, Keep/Reject pending proposals first.
3. Choose:

`/Users/george/Developer/virtual-coworker/ads-launch/google-ads-editor-semantic-adgroups-add-us.csv`

4. Review the import preview. You should see **only adds**:
   - 4 new ad groups under existing `VC_US_S_CORE` / `VC_US_S_ROLES`
   - Exact keywords under those new AGs
   - 3 RSAs per new AG
5. Confirm nothing is rewriting budgets, old ad groups, or unrelated keywords.
6. Finish the import into the **local** Editor draft (still not live).
7. **Known Editor gotcha (2026-08-09):** if Import stamped Languages=`en` on the new AGs, clear Languages on those AGs (campaign already owns language targeting) before Post.

### Step 3 — Sanity check in Editor (before Post)

In the tree / views, confirm:

- [ ] `Staffing_Agency_PH`, `VA_Agency_Firm_PH`, `Virtual_Staff_PH` under `VC_US_S_CORE`
- [ ] `Appointment_Setter_Hire_PH` under `VC_US_S_ROLES`
- [ ] Each AG status **Paused**
- [ ] Keywords = **Exact** only, status **Paused**
- [ ] Each AG has **3** RSAs, Final URL `/us` or `/us/sales` as in the table above
- [ ] Existing ad groups still present unchanged

### Step 4 — Pause duplicates in old AGs

1. Import the second file the same way:

`/Users/george/Developer/virtual-coworker/ads-launch/google-ads-editor-semantic-adgroups-pause-dupes-us.csv`

2. Preview should show **Keyword Status → Paused** on Exact terms inside `Hire_VA_PH`, `Offshore_VA_PH`, `Sales_Hire_PH`, `Sales_Outsource_PH`.
3. If Editor flags a keyword that isn’t in that old AG (already removed / never posted), skip that row — don’t force-create junk.
4. Goal: those Exact terms live in the **new** themed AG only.

### Step 5 — Post (upload draft → Google, still Paused)

1. **Post** the USA account changes when the local review looks right.
2. Post uploads; statuses stay **Paused** from the CSV.
3. Do **not** Enable yet unless you intentionally want them live.

### Step 6 — Enable (separate decision)

When you’re ready to test:

1. Enable the **ad group** you want first (recommend `Staffing_Agency_PH` — strongest clean buyer signal).
2. Enable its **Exact keywords** + **RSAs**.
3. Leave the other three AGs Paused until that one looks sane in search terms.
4. Suggested enable order:
   1. `Staffing_Agency_PH`
   2. `VA_Agency_Firm_PH`
   3. `Virtual_Staff_PH`
   4. `Appointment_Setter_Hire_PH` (after job-seeker negatives feel solid)

---

## D. Landing-page call

**No new pages for this batch.**

- Agency / virtual-staff Exact → `/us` (hub already employer-gated; RSA path text carries agency language)
- Appointment setter → `/us/sales` (role-specific)

**Later (only if Exact volume stays clean):** a dedicated `/us/offshore-staffing` (or similar) for staffing-agency message match. Not justified as a thin page today.

---

## E. Experiment log (lightweight)

| Date | Surface | Current | Challenger | Hypothesis | Evidence | Result | Decision |
|------|---------|---------|------------|------------|----------|--------|----------|
| 2026-08-09 | CORE ST → AG | Agency terms in `Hire_VA_PH` | `Staffing_Agency_PH` Exact + agency RSAs | Provider-shopping CTR/quality improves with agency message match | remote staffing agency/agencies clicks | — | INSUFFICIENT DATA |
| 2026-08-09 | CORE ST → AG | VA agency terms mixed in Hire/Offshore | `VA_Agency_Firm_PH` Exact + agency/firm RSAs | Agency/firm language deserves its own RSA set | agency impressions + prior agency-intent spine | — | INSUFFICIENT DATA |
| 2026-08-09 | CORE ST → AG | virtual staff in Admin/Offshore | `Virtual_Staff_PH` Exact | Shorthand cluster needs dedicated Exact + copy | virtual staff / virtualstaff ph clicks | — | INSUFFICIENT DATA |
| 2026-08-09 | ROLES ST → AG | Setter terms in `Sales_Hire_PH` w/ WFH junk | `Appointment_Setter_Hire_PH` employer Exact → `/us/sales` | Isolating employer Exact reduces junk share of setter spend | setter cluster cost + WFH terms | — | INSUFFICIENT DATA |

---

## F. What George is handling (out of this package)

- Turning lots of existing keywords into **Phrase** (discovery) — your call
- Search-term hygiene / negatives
- **Do not** add Phrase into these four new AGs yet — Exact seasoning first

---

## G. Rebuild

```bash
python3 ads-launch/build_semantic_adgroups_add.py
```
