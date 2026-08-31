# Aug 18 change log — 20 Aug 2026

Derived from Zoho people, not Ads conversion counts.

## Before state (saved)

- Ads live pull: blocked (`invalid_grant`). Snapshot used: `xray/data/executive-snapshot.json` 19 Aug 19:27 UTC.
- Conversion actions: `.local/ads/conv-actions-2026-08-19.json`
- RSA/ST: `ads-launch/_rsa_challenger_review.json`
- LP: `/us` and `/au/*` on `baseline_v1_2026_08` commit `e03d1dd` (18 Aug 04:22 PT). Aug 18 US paid forms hit `stage1-v8` before that ship.
- Registry: `ads-launch/aug18-winners/winning-path-registry.json`

## Implemented (reversible, not posted)

| Date | Change | Why | Derived from | Revert |
|---|---|---|---|---|
| 2026-08-20 | Registry freeze of US agency + AU SMM paths | Human CRM probable employers | Zoho 6724032000029876002, 6724032000029986002 | Delete registry / ignore |
| 2026-08-20 | Editor CSV pause `australia virtual assistant` Exact in `Recruitment_Hire_PH` | Two Junk Leads, no employer | AU-A17-01 / AU-A17-02 | Set keyword Enabled |
| 2026-08-20 | Editor CSV Exact negative `virtual assistant hiring in australia` on that ad group | Demonstrated junk search term | Same | Remove negative |
| 2026-08-20 | Editor CSV Exact `hire a social media manager` Enabled in `Social_Media_Hire_PH` | Controlled Exact of converting Phrase | AU-A19-01 | Pause the Exact; leave Phrase |
| 2026-08-20 | X-ray page `aug18-conversions.html` | George looks at vc-xray | — | Unpublish page |
| 2026-08-20 | Confirmed US agency keyword still Enabled (18 Aug inspect). Did not restore. | Disk inspect JSON | — | Leave Enabled |
| 2026-08-20 | RSA IDs: `820314203419` is wrong US group; `820329868205` eligible/unconfirmed on AU SMM | RSA review + post JSON. Ads live blocked | — | Do not declare winners |
| 2026-08-20 | Paused challenger CSVs `04-spend-only-challengers-*.csv` | Spend-only groups, zero good Zoho | After file 02 | Pause/remove those Ad rows |
| 2026-08-20 | X-ray `aug18-next.html` SERP mocks | Show before import | — | Unpublish page |
| 2026-08-20 | Checklist “After Aug 18 — next” | George asked for tasks from learnings | — | Remove section |

No Ads API mutate. No LP code edit. No bid/budget/RSA/URL change on protected paths.

## Not implemented (needs approval)

- `PROTECT_CONFIRMED_WINNER_AUG18` label (Ads reauth)
- Pause Broad `virtual assistant for real estate investors`
- Budget move AU CORE → AU social / US agency
- Maximize Conversions (neither market ready — see `ZOHO-QUALITY-GATE-PROPOSAL.md`)
- Conversion-action Primary cleanup (page_view is firing as US GA4 conversions)
- Company-name required on forms (Cheyenne already asked; do not rebuild `/us` in this pass)
- Offline uploads (proposal only; gate stays OFF)

## Quality gate (report only, 20 Aug)

- `ZOHO-QUALITY-GATE-PROPOSAL.md` + `.json` — classification + future upload rules. No Zoho writes. No uploads.
- Extra COQL: 5 paid people, `Discovery_Call_Date` empty, `Qualification_Status` empty.
- Ads OAuth still `invalid_grant`. Protect label not applied.
