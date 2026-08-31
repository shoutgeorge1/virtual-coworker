# Prioritized checklist — 13 August 2026

Practical only. Not 100 tiny tasks.

**Decision gate:** `NOT READY FOR CRM WRITES OR OFFLINE IMPORT`

Do not start Next until the Now questions are answered. Do not start Later to look busy.

---

## Now — necessary to trust the pilot

| # | Task | Owner | Dependency | Risk if skipped | Success looks like | Kind | George OK? | Human first? |
|---|------|-------|------------|-----------------|--------------------|------|------------|--------------|
| N1 | Confirm `.app` employer emails actually arrive and are recognizable | Cheyenne (US), Holly (AU) | One real (or clearly labelled test) submit per market | Sales never sees the new funnel | They can point to a message with **Submission ID** and market in the subject `Free Consultation (virtualcoworker.app/…)` | Read-only / ops | No | **Yes — Cheyenne, Holly** |
| N2 | Confirm thank-you fires **once** in GTM Preview (event `employer_inquiry_submitted` only — not the alias, not page view) | Raffie + George | US GTM `GTM-M92DX9BJ`; Ads action `VC_US_Thank_You` already exists | False conversions or a desert | One fire per submit; refresh = deduped; `eligible=0` does not count | GTM / Ads UI check | Yes to publish if a tag is missing | Raffie |
| N3 | Confirm Calendly **booked** (schedule confirmed), not open, is what George thinks is mapped | Raffie | Vision code has **no** booked listener. Published GTM US v6 / AU v6 **do** listen for `calendly.event_scheduled`. Existence ≠ firing | Open counted as booked, or a silent miss | A test booking creates one Ads hit; a mere overlay open does not | GTM / Calendly | Yes | Raffie |
| N4 | Confirm campaign-specific goals on all four `VC_*` campaigns: only new pipe checks; **no** Zoho/Zapier/UA/eBook | Amanda or George in Ads UI | Campaigns already live | Museum junk silently sits on the campaign | Screenshot of campaign goals list | Ads UI | Yes to change goals if wrong | **Amanda** |
| N5 | Ask whether the old Zapier → Ads upload is still on | Caitlin or whoever owns Zapier (likely Raffie / Caitlin) | Zapier login | Any later import double-counts | “On / off / I don’t have it” plus a screenshot of the Zap | External | No | **Caitlin, Raffie** |
| N6 | Get the authoritative CRM definitions | Caitlin, Cheyenne | This dictionary | We import the wrong object | Written answers to the questions in [HUMAN-QUESTIONS.md](HUMAN-QUESTIONS.md) | Conversation | No | **Caitlin, Cheyenne** |
| N7 | Keep Maximize Clicks. Do not change bids, budgets, Brand, Primary/Secondary from this audit | George | — | Fake optimization | No “fix the CPA” work this week | None | — | — |

Out of scope for Now: enabling Zoho writes, offline import, CallRail purchase, E form $, Broad / PMax / Max Conv, WordPress revival, Brand enable.

---

## Next — after definitions are confirmed

| # | Task | Owner | Dependency | Risk | Success | Kind | George OK? | Human first? |
|---|------|-------|------------|------|---------|------|------------|--------------|
| X1 | Design `.app` → Sales Enquiries write (field map only) | Engineering + Caitlin | N6 | Wrong module/source | Written map: `utm_gclid` not `$gclid`; Region USA/AU; source Google Ads when click id present; new `VC_Submission_ID` if they agree to create it | Zoho change **later** | **Yes** before any enable | Caitlin |
| X2 | Persist click ids more durably than `sessionStorage` (consent-aware) | Engineering | X1 | Lost gclid on new tab — already happening | Paid click still present at submit after an internal navigation | Website | Yes | — |
| X3 | Freeze museum Zapier + Standard OCI (leave in account, do not attach to `VC_*`) | Raffie / Amanda | N5 | Double meter | Written “frozen / still reporting only” | Ads UI + Zapier | Yes | Raffie |
| X4 | If — and only if — N5–N6 are clean: **one** Secondary test upload of **one** Bucket A job order Caitlin vouches for | Amanda + George | N5, N6, click still valid | Teach Google junk or double-count | One row, Secondary, new action name, not Zapier twins | Ads UI / CSV later | **Yes** | Caitlin, Amanda |
| X5 | AU 60s website-call + AU 60s ad-call (#16 / #17) | George in Ads UI | AU GTM already live | AU pipe stays blind | Actions exist; a real 60s call appears | Ads UI | Yes | — |
| X6 | Human-review workflow: Cheyenne/Holly tag junk vs useful on `.app` leads for two weeks | Cheyenne, Holly | N1 | We judge the LP with no sales eyes | A short weekly count: useful / junk / job-seeker | Ops | No | Cheyenne, Holly |
| X7 | Call answering tree (who picks up 888 / 1300, missed calls) | Cheyenne, Holly | — | 60s actions fire into voicemail | Named owner | Ops | No | **Cheyenne, Holly** |

Do not enable `ZOHO_CRM_ENABLED` in Next until X1 is on paper and Zapier is frozen.

---

## Later — after enough qualified volume

| # | Task | Why later |
|---|------|-----------|
| L1 | Enhanced conversions for leads | Needs consented PII + working click id. Not the missing piece today. |
| L2 | Monetary values / E form $ | Locked: **not next**. After AU 60s + a named Zoho outcome. |
| L3 | Conversion adjustments / retractions | Only after a real offline action exists. |
| L4 | Revisit Smart Bidding | Only after a trustworthy Primary exists and volume is real. Stay on Max Clicks until then. |
| L5 | Brand defense | Separate project. Deferred. |
| L6 | Competitor / extra role campaigns | Not an attribution problem. |
| L7 | CallRail DNI | Existing 1–2 month lock. After form + CRM definitions. |
| L8 | CRM cleanup and admin hygiene | 17 admins, Peter Mill leftover, Lois identity. **Low priority vs leads.** See below. |
| L9 | Access cleanup | Do not delete anyone until dependencies are known (especially Lois and Web Master). |

### Access hygiene (low priority — do not distract from lead gen)

- Identify Lois before any disable.
- Peter Mill already deleted (twice). Leave unless a live integration still uses that identity (**UNKNOWN**).
- George’s deleted gmail Administrator: leave until confirmed unused.
- Do not drop 17 admins to “a sensible number” in a sweep.

---

## Explicitly not on this list

Broad match · Performance Max · DSA · Maximize Conversions · budget bumps to “stimulate” · WordPress as the paid LP · attaching historical Zoho/Zapier conversions to `VC_*` · enabling Brand · sending the team email from these notes.
