# Sitelink add — US + AU · 2026-08-10

**Status (2026-08-12):** US sitelinks were verified on disk after the Aug 10 push. **AU is missing in Editor after Get recent changes — treat as not live.** Re-import AU via Editor CSV (no Ads API mutate). `#gate` removed from Final URLs (Ads rejects fragments).

**Accounts:** USA `496-715-1855` · AU `573-539-1940`  
**Campaigns:** `VC_*_S_CORE` + `VC_*_S_ROLES` only. **Not** account-level. **Not** Brand. **Not** PM_*.

API used hub URLs (no `#gate` — Ads Final URLs reject fragments). Form still sits on `/us` and `/au`.

Add-only Editor CSVs remain as a backup. Campaign Status / Budget blank so live campaigns stay as they are.

| File | Import into |
|------|-------------|
| `google-ads-editor-sitelink-add-us.csv` | USA |
| `google-ads-editor-sitelink-add-au.csv` | AU |
| Regenerator | `python3 ads-launch/build_sitelink_add.py` |

**12 sitelinks per account** (6 CORE + 6 ROLES). All `www.virtualcoworker.app` — no WordPress.

## What they point at

### CORE (`VC_*_S_CORE`)

| Link text | Dest |
|-----------|------|
| Tell Us Who You Need | `/{us\|au}#gate` |
| How Hiring Works | `/how-it-works?market=` (real process page — not homepage) |
| Take the VA Quiz | `/{us\|au}/quiz` |
| Hire by Role | `/services?market=` |
| Admin Support Hire | `/{us\|au}/administrative-support` |
| Bookkeeping Hire | `/{us\|au}/bookkeeping` |

### ROLES (`VC_*_S_ROLES`)

| Link text | Dest |
|-----------|------|
| Tell Us Who You Need | `/{us\|au}#gate` |
| How Hiring Works | `/how-it-works?market=` |
| Take the VA Quiz | `/{us\|au}/quiz` |
| Digital Marketing Hire | `/{us\|au}/digital-marketing` |
| Social Media Hire | `/{us\|au}/social-media` |
| Bookkeeping Hire | `/{us\|au}/bookkeeping` |

If Stage 1 sitelinks were already posted, preview may show some as **updates** (same link text, new URL) plus new ones (Quiz / Hire by Role / How Hiring Works on the real page). Uncheck any row you don’t want.

Quiz campaigns (`VC_*_S_QUIZ`) are **not** in these files. Quiz sitelinks live in the quiz import CSVs if/when you import quiz.

## Editor — USA first

1. Open Google Ads Editor → **USA** account.
2. **Get recent changes.** Wait until it finishes.
3. **Account → Import → From file…** → `google-ads-editor-sitelink-add-us.csv`
4. Preview should be **Sitelink adds/updates only**. No campaign pause. No new keywords.
5. Check a couple of Final URLs (`/how-it-works`, `/us/quiz`, `#gate`).
6. **Post.** These can show on live Enabled `VC_US_*` ads right after Post.

Then AU: same steps with `google-ads-editor-sitelink-add-au.csv` in the **AU** account.

Do **not** Account Import the main Stage 1 package to get sitelinks — that file still has Campaign Status = Paused and would rewrite live campaigns.

No Ads API. Brand deferred.
