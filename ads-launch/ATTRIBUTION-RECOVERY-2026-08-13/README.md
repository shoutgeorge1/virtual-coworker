# Attribution recovery audit — 13 August 2026

Read-only forensic pass. **Nothing was written in Zoho. Nothing was sent. Google Ads was not mutated. No Editor import/post. CRM writes stayed off.**

**Decision gate:** `NOT READY FOR CRM WRITES OR OFFLINE IMPORT`

## Files

| # | File | What it is |
|---|------|------------|
| 1 | [EXECUTIVE-TRUTH.md](EXECUTIVE-TRUTH.md) | What works, what’s broken, what’s unknown |
| 2 | [ATTRIBUTION-MAP.md](ATTRIBUTION-MAP.md) | Current routes vs a later proposed flow (proposed is **not live**) |
| 3 | [CONVERSION-ACTIONS.md](CONVERSION-ACTIONS.md) | Google Ads conversion reconciliation |
| 4 | [ZOHO-DICTIONARY.md](ZOHO-DICTIONARY.md) | Modules, fields, statuses, relationships |
| 5 | [RECOVERABLE-CANDIDATES.md](RECOVERABLE-CANDIDATES.md) | Three buckets. No uploads. Not “great leads.” |
| 6 | [PHONE-ATTRIBUTION.md](PHONE-ATTRIBUTION.md) | Call paths and later options. Do not buy CallRail from this memo. |
| 7 | [CHECKLIST.md](CHECKLIST.md) | Now / Next / Later |
| 8 | [HUMAN-QUESTIONS.md](HUMAN-QUESTIONS.md) | Caitlin, Cheyenne, Holly, Raffie, Amanda |
| 9 | [TEAM-UPDATE-SOURCE-NOTES.md](TEAM-UPDATE-SOURCE-NOTES.md) | Facts for a later email. **Not a draft to send.** |
| 10 | [CHATGPT-AUDIO-DEBRIEF.md](CHATGPT-AUDIO-DEBRIEF.md) | Paste-ready spoken brief |
| 11 | [FINAL-EVIDENCE-ADDENDUM-2026-08-13.md](FINAL-EVIDENCE-ADDENDUM-2026-08-13.md) | Final evidence pass — corrections + goals/join |
| 12 | [ATTRIBUTION-NUMBERS-2026-08-13.csv](ATTRIBUTION-NUMBERS-2026-08-13.csv) | Non-PII counts only |
| 13 | [CHECKLIST-PATCH-2026-08-13.md](CHECKLIST-PATCH-2026-08-13.md) | Local checklist diff (not deployed) |
| 14 | [TEAM-UPDATE-DRAFT-2026-08-13.md](TEAM-UPDATE-DRAFT-2026-08-13.md) | Draft email. **Not sent.** |
| 15 | [API-CALL-LOG-2026-08-13.md](API-CALL-LOG-2026-08-13.md) | Ads 12 / Zoho 12 |

Record-level IDs (no emails/phones) live only under `.local/zoho/probe-attribution-recovery-2026-08-13.json` (gitignored).

## What this pass did

- Read on-disk Ads snapshots (`xray/data/*`, recovery audit of 13 Aug).
- Independently verified Zoho census facts, then **11 cheap CRM reads** for click-ID recency, Lois metadata, and a small candidate set.
- Read `virtualcoworker.app` form, tracking, Zoho mapping, and Calendly code.
- **Did not** call Google Ads API this pass (conversion inventory already on disk from 13 Aug).
- **Did not** enable `ZOHO_CRM_ENABLED`, touch Zapier, publish GTM, or send email.

## Live acquisition (do not “fix” from this folder)

US: `VC_US_S_CORE` / `VC_US_S_ROLES` · Exact + Phrase · Maximize Clicks · `https://www.virtualcoworker.app/us`  
AU: `VC_AU_S_CORE` / `VC_AU_S_ROLES` · same · `/au`  
Brand deferred. Quiz / PH still gated. Form thank-you, Calendly booked, and 60-second phone are the intended pipe checks ($1 placeholders; Primary OK for now). **E (form $ matrix) is not next.**
