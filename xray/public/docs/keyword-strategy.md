# Keyword strategy — Phase 1 Google Search pilot

Employer-side Search only. Quality over volume.

**Priority (2026-08-09):** employers looking for an **agency / firm / company** to hire remote staff in the Philippines — not job seekers, and not ambiguous hire/recruit language alone.

## Match types

| Priority | Match | Rule |
|----------|-------|------|
| 1 | **Exact** | Launch / expand with exact first |
| 2 | Phrase | Add only after search-term quality is confirmed |
| 3 | Broad | **Not used** in the initial pilot |

Low volume is acceptable. Job-seeker traffic must be excluded aggressively (see `negative-keywords.md`).

## Primary clusters

### 1 — Philippines VA / staffing **agency** (highest intent)

Intent: businesses shopping for a provider to staff PH remote workers.

Examples: `philippines virtual assistant agency`, `philippines va agency`, `filipino virtual assistant agency`, `virtual staffing agency`, `philippines staffing agency`, `philippines outsourcing agency`, `outsourcing agency philippines`, `staffing firm philippines`, `remote staffing agency`

Editor add-on (Paused Exact): `ads-launch/google-ads-editor-agency-intent-keywords-add.csv`

### 2 — Firm / company / outsourcing provider language

Intent: same buyer, different words (firm, company, outsourcing).

Examples: `virtual assistant firm`, `va firm`, `virtual assistant company`, `philippines va company`, `filipino outsourcing agency`, `offshore staffing agency`

### 3 — Hire VA / Filipino VA (supporting — messier)

Intent: often employer, but “hire/recruit/hiring” can mix with job-seeker noise. Keep as support; don’t lead the package with head terms alone.

Examples: `hire filipino virtual assistant`, `hire VA philippines`, `hire a virtual assistant`

### 4 — Role outsourcing (ROLES campaign)

Intent: outsource a named function (bookkeeping, CSR, marketing, etc.) to PH staff — secondary dial to CORE agency intent.

## Watch / pause

- `va workers ph` and similar odd shorthand — can look buyer-ish but doesn’t always read human; watch spend and pause if it climbs.
- Bare general VA head terms without agency/PH cue — higher competition, more junk.

## Phase 1 destination rule

- **Clusters 1–3** → market hubs `/us` and `/au` (CORE Final URLs).
- **Cluster 4** → category LPs `/us|au/{category}`.

## Do not block globally

Do **not** add account-level negatives for `hire` or `hiring` — those often signal employer intent. Prefer bidding agency language harder and negatives for true job-seeker roots (`job`, `salary`, `resume`, …).
