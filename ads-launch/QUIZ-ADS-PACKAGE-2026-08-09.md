# Quiz Ads package — 2026-08-09 (Paused)

Exploratory funnel: **Take the employer hiring quiz / Find the right VA for your business.**  
Homepage variation LPs only. **Not live. Not a statistically controlled A/B test.**  
Import → review → Post (still Paused) → **Enable only when George says.**

Do **not** change live CORE/ROLES (budgets, bids, keywords, negatives, bidding). Brand deferred.

## Final URLs (duplicate these into ads)

- https://www.virtualcoworker.app/us/quiz
- https://www.virtualcoworker.app/au/quiz

No fake role-quiz URLs. Path 1/2 display only (`quiz/what-va`, `quiz/hire`, …).  
Calendly is **optional post-thank-you only** (US Cheyenne / AU APAC) — never Final URL / never primary CTA.

## Files

| File | Use |
|------|-----|
| `google-ads-editor-quiz-import-us.csv` | **Account Import** → USA `496-715-1855` |
| `google-ads-editor-quiz-import-au.csv` | **Account Import** → AU `573-539-1940` |
| `google-ads-editor-quiz-campaign-negatives-us.csv` | **Keywords, Negative → Make multiple changes** (USA) — do **not** Account Import |
| `google-ads-editor-quiz-campaign-negatives-au.csv` | **Keywords, Negative → Make multiple changes** (AU) — do **not** Account Import |
| `QUIZ-KEYWORD-OVERLAP-2026-08-09.md` | Overlap audit vs CORE/ROLES Exact (repo CSVs, not live API dump) |

Builder + validation (fails if anything is not Paused):  
`python3 ads-launch/build_quiz_editor_package.py`

## Campaigns (new, clearly separate)

| Campaign | Budget / day | Max CPC | Status |
|----------|--------------|---------|--------|
| `VC_US_S_QUIZ` | $40 | $10 | **Paused** |
| `VC_AU_S_QUIZ` | A$40 | $6 | **Paused** |

Modest test vs CORE $75 / ROLES $50. **George must approve budgets/CPC before Enable** — do not silently change. Search only. Maximize Clicks. No Broad / PMax / Demand Gen / DSA / Maximize Conversions.

UTM suffix: existing ValueTrack + `lp_version=stage1-v8` (matches site stamp; mega prompt said v7) + **`lp_variant=quiz`**. Preserves gclid/wbraid/gbraid/UTMs/market/lp.

## Ad groups (Exact)

Same names US + AU. **Not** a full CORE/ROLES clone — overlap audit dropped Exact money-term duplicates.

1. `What_Kind_Of_VA` — unique quiz / what-kind / types (all unique vs CORE/ROLES Exact)
2. `Hire_VA_Explore` — unique how-to / should-I-hire (CORE Exact hire terms **dropped**)
3. `VA_Small_Business` — SMB/startup Exact unique vs ROLES
4. `Admin_VA_Quiz` — admin exploratory unique vs ROLES EA Exact
5. `Bookkeeping_VA_Quiz` — books exploratory unique vs ROLES bookkeeping Exact

See overlap report for dropped clones + optional holdout (`how to hire a virtual assistant`).

## Sitelinks (campaign-level, 4)

Paused with the quiz campaign. Microsite only — no WordPress, no Calendly, no quiz self-link.

| Link text | Dest |
|-----------|------|
| Tell Us Who You Need | `/{us\|au}#gate` |
| How Hiring Works | `/how-it-works?market=` |
| Hire by Role | `/services?market=` |
| Admin Support Hire | `/{us\|au}/administrative-support` |

## RSAs

Exploratory / self-help, not CORE hard-sell clones. Employer-positive primary:

- Find the right VA / Take the employer quiz
- A few taps. Clear answer.
- Quiz: admin, sales, books
- For US businesses / For Australian businesses

“Not a job board” lives in descriptions only — **not** the hero headline.

US punchy · AU understated B2B. Employer-only. No job-seeker bait.

## Negatives

Stage 1 CORE employer/job-seeker protections cloned onto `VC_*_S_QUIZ` (**MMC CSV only** — never in Account Import).  
Not historical mega-lists. After Post, George attaches shared lists: Sniper / Competitors / Job seekers.

## Tracking (same GTM as homepage)

| Kind | Event | Ads bidding? |
|------|--------|----------------|
| **Quiz funnel north star** | `employer_inquiry_submitted` (durable delivery) | Observation only — **not** bidding Primary |
| Secondary | `quiz_started` / `quiz_step` / `quiz_completed` / `lead_magnet_completed` | Never |
| Secondary | `phone_cta_clicked` / thank-you view / `calendly_cta_clicked` | Never |
| Site-wide Ads Primary (unchanged) | 60s+ website calls · Zoho Qualified offline | Yes (existing) |

Modeled $ is analytics only — **not** Ads conversion value. `lp_variant=quiz` on quiz LP events.

## Editor (no invented click path)

1. Account Import the US/AU **import** CSVs (not the negatives CSVs).
2. Review locally. Everything should be **Paused**. Validation script already failed the build if not.
3. Post → still Paused.
4. Keywords, Negative → Make multiple changes → paste/import the **negatives** CSVs.
5. Attach shared lists (Sniper / Competitors / Job seekers) if George wants them on quiz too.
6. **Do not Enable** until George says. Enable is George-only.

No Ads API mutate. No Brand. Tiny test when (if) enabled.
