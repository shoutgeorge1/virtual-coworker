# Quiz Ads package — 2026-08-09 (Paused)

Exploratory funnel: **Take the quiz / What kind of VA do you need?**  
Homepage variation LPs only. **Not live.** Import → review → Post (still Paused) → **Enable only when George says.**

## Final URLs (duplicate these into ads)

- https://www.virtualcoworker.app/us/quiz
- https://www.virtualcoworker.app/au/quiz

No fake role-quiz URLs. Path 1/2 display only (`quiz/what-va`, `quiz/hire`, …).

## Files

| File | Use |
|------|-----|
| `google-ads-editor-quiz-import-us.csv` | Account Import → USA `496-715-1855` |
| `google-ads-editor-quiz-import-au.csv` | Account Import → AU `573-539-1940` |
| `google-ads-editor-quiz-campaign-negatives-us.csv` | **Keywords, Negative → Make multiple changes** (USA) — do **not** Account Import |
| `google-ads-editor-quiz-campaign-negatives-au.csv` | **Keywords, Negative → Make multiple changes** (AU) — do **not** Account Import |

Builder: `python3 ads-launch/build_quiz_editor_package.py`

## Campaigns (new, clearly separate)

| Campaign | Budget / day | Max CPC | Status |
|----------|--------------|---------|--------|
| `VC_US_S_QUIZ` | $40 | $10 | **Paused** |
| `VC_AU_S_QUIZ` | A$40 | A$6 | **Paused** |

Modest test vs CORE $75 / ROLES $50. Brand deferred. Search only. Maximize Clicks.

## Ad groups (Exact)

Same names US + AU. Keywords cloned from **more relevant** CORE/ROLES employer themes — not junk, not job-seeker.

1. `What_Kind_Of_VA` — what kind/type of VA do I need · virtual assistant quiz
2. `Hire_VA_Explore` — hire virtual assistant / how to hire (from `Hire_VA_PH`)
3. `VA_Small_Business` — VA for small business / startup
4. `Admin_VA_Quiz` — admin / executive assistant (from ROLES Admin)
5. `Bookkeeping_VA_Quiz` — virtual bookkeeper (from ROLES books)

## RSAs

Totally different angle from hire-a-specialist hard sell:

- What kind of VA do you need?
- Take the hiring quiz
- A few taps. Clear answer.
- Quiz: admin, sales, books
- Not a job board / Employer quiz

US punchy · AU understated B2B. Employer-only. No job-seeker bait.

## Negatives

Cloned Stage 1 CORE job-seeker Broad list onto `VC_*_S_QUIZ` (MMC CSV only — same rule as main package: never put campaign negatives in Account Import).

## Editor (no invented click path)

1. Import the US/AU **import** CSV in Google Ads Editor.
2. Review locally. Everything should be **Paused**.
3. Post → still Paused.
4. Import the **negatives** CSV via Keywords, Negative → Make multiple changes.
5. **Do not Enable** until George says.

No Ads API mutate. No Brand. Tiny test when (if) enabled.
