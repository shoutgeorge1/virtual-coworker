# Quiz keyword overlap vs CORE/ROLES — 2026-08-09

Source inventories (repo Editor CSVs — **not** a live Ads API dump):
- `ads-launch/google-ads-editor-import-us.csv` · `VC_US_S_CORE` / `VC_US_S_ROLES`
- `ads-launch/google-ads-editor-import-au.csv` · `VC_AU_S_CORE` / `VC_AU_S_ROLES`

Match compared: **Exact** positives only. Live campaigns were **not** changed.

Classes:
- **unique_quiz** — not Exact in CORE/ROLES → in quiz import
- **unnecessary_duplicate** — Exact already in CORE/ROLES money groups → **dropped** from quiz import
- **optional_holdout** — quiz-shaped but Exact in CORE → **held out** until George approves
- **intentional_limited_overlap** — none kept in this pass (Exact auction split not worth it)

This is an **exploratory funnel**, not a statistically controlled A/B test.

## Included in quiz import (unique_quiz)

| Ad group | Keyword | Class |
|----------|---------|-------|
| `What_Kind_Of_VA` | `what kind of virtual assistant do i need` | unique_quiz |
| `What_Kind_Of_VA` | `what type of virtual assistant do i need` | unique_quiz |
| `What_Kind_Of_VA` | `what virtual assistant do i need` | unique_quiz |
| `What_Kind_Of_VA` | `what va do i need` | unique_quiz |
| `What_Kind_Of_VA` | `which virtual assistant do i need` | unique_quiz |
| `What_Kind_Of_VA` | `types of virtual assistants` | unique_quiz |
| `What_Kind_Of_VA` | `kinds of virtual assistants` | unique_quiz |
| `What_Kind_Of_VA` | `virtual assistant quiz` | unique_quiz |
| `What_Kind_Of_VA` | `hiring quiz virtual assistant` | unique_quiz |
| `What_Kind_Of_VA` | `what kind of va should i hire` | unique_quiz |
| `Hire_VA_Explore` | `hiring a virtual assistant` | unique_quiz |
| `Hire_VA_Explore` | `where to hire a virtual assistant` | unique_quiz |
| `Hire_VA_Explore` | `how to hire filipino va` | unique_quiz |
| `Hire_VA_Explore` | `should i hire a virtual assistant` | unique_quiz |
| `Hire_VA_Explore` | `do i need a virtual assistant` | unique_quiz |
| `Hire_VA_Explore` | `how to choose a virtual assistant` | unique_quiz |
| `Hire_VA_Explore` | `help me hire a virtual assistant` | unique_quiz |
| `VA_Small_Business` | `virtual assistant for small business` | unique_quiz |
| `VA_Small_Business` | `virtual assistant small business` | unique_quiz |
| `VA_Small_Business` | `hire virtual assistant small business` | unique_quiz |
| `VA_Small_Business` | `virtual assistant for small businesses` | unique_quiz |
| `VA_Small_Business` | `va for small business` | unique_quiz |
| `VA_Small_Business` | `virtual assistant for startup` | unique_quiz |
| `VA_Small_Business` | `virtual assistant for startups` | unique_quiz |
| `VA_Small_Business` | `small business virtual assistant` | unique_quiz |
| `Admin_VA_Quiz` | `hire administrative assistant` | unique_quiz |
| `Admin_VA_Quiz` | `hire admin assistant` | unique_quiz |
| `Admin_VA_Quiz` | `virtual assistant for admin` | unique_quiz |
| `Admin_VA_Quiz` | `administrative virtual assistant` | unique_quiz |
| `Admin_VA_Quiz` | `virtual executive assistant` | unique_quiz |
| `Admin_VA_Quiz` | `admin virtual assistant` | unique_quiz |
| `Bookkeeping_VA_Quiz` | `hire virtual bookkeeper` | unique_quiz |
| `Bookkeeping_VA_Quiz` | `virtual bookkeeper` | unique_quiz |
| `Bookkeeping_VA_Quiz` | `hire bookkeeper` | unique_quiz |
| `Bookkeeping_VA_Quiz` | `outsource bookkeeping` | unique_quiz |

## Dropped — unnecessary Exact duplicates

| Would-be AG | Keyword | Already Exact in |
|-------------|---------|------------------|
| `Hire_VA_Explore` | `hire virtual assistant` | Exact in CORE Hire_VA_PH |
| `Hire_VA_Explore` | `hire a virtual assistant` | Exact in CORE Hire_VA_PH |
| `Hire_VA_Explore` | `hire virtual assistant philippines` | Exact in CORE Hire_VA_PH |
| `Hire_VA_Explore` | `hire filipino virtual assistant` | Exact in CORE Hire_VA_PH |
| `Hire_VA_Explore` | `hire a filipino virtual assistant` | Exact in CORE Hire_VA_PH |
| `Admin_VA_Quiz` | `hire virtual administrative assistant` | Exact in ROLES Administration_EA_PH |
| `Bookkeeping_VA_Quiz` | `virtual assistant bookkeeping` | Exact in ROLES Bookkeeping_Hire_PH |
| `Bookkeeping_VA_Quiz` | `hire virtual bookkeeping assistant` | Exact in ROLES Bookkeeping_Hire_PH |

## Optional holdout (George can add later)

| Would-be AG | Keyword | Why hold |
|-------------|---------|----------|
| `Hire_VA_Explore` | `how to hire a virtual assistant` | Exploratory/how-to, but Exact in CORE Hire_VA_PH — auction split risk |

## What this does not do

- Does not pause, add, or rewrite live CORE/ROLES keywords
- Does not invent a Google Ads Experiment
- Does not clone historical mega negative lists into quiz MMC
  (quiz MMC = Stage 1 CORE employer/job-seeker protections only;
  attach Sniper / Competitors / Job seekers shared lists in Editor — George)
