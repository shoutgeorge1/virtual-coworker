# Change manifest

| Asset | Kind | Notes |
| --- | --- | --- |
| `vision/config/trust-first.ts` | MODIFIED | Two new page keys + Social media support form option |
| `vision/lib/trust-first.test.ts` | MODIFIED | Count 12; H1 / URL lock |
| `vision/scripts/capture-trust-first-preview.mjs` | MODIFIED | New slugs in screenshot list |
| `ads-launch/research/trust-first-us-2026-08-18/architecture.md` | MODIFIED | Twelve page configs |
| Preview social-media-virtual-assistant | NEW | Isolated namespace |
| Preview digital-marketing-virtual-assistant | NEW | Isolated namespace |
| `ads-launch/build_social_marketing_va_editor.py` | NEW | Builder, no Ads API |
| `ads-launch/google-ads-editor-social-marketing-va-us.csv` | NEW | Paused AGs + keywords + 1 RSA each |
| `ads-launch/google-ads-editor-social-marketing-va-negatives-us.csv` | NEW | Optional Phrase extras |
| This research folder | NEW | Report |
| Live `/us/*` pages | UNCHANGED | |
| `Social_Media_Hire_PH` / `Digital_Marketing_Hire_PH` | UNCHANGED | |
| `google-ads-editor-import-us.csv` | UNCHANGED | Not regenerated |
| AU campaigns | UNCHANGED | |
| Brand | UNCHANGED | |
| GTM / GA4 / Ads conversion labels | UNCHANGED | |

## Google Ads (after George Imports)

NEW only, all Paused:

- Ad group `Social_Media_VA_PH`
- Ad group `Digital_Marketing_VA_PH`
- Exact + Phrase keywords listed in the CSV
- One RSA per group
- Optional campaign Phrase negatives

No campaign create. No enable. No Final URL change on existing ads. Campaign Status is blank so Import cannot pause live `VC_US_S_ROLES`.
