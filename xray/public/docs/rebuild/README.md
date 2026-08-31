# Virtual Coworker — Clean Search Rebuild

**Status:** Implementation-ready package · **No live Ads / GTM / Zoho / CallRail mutations**  
**Generated:** 2026-08-05 · Branch `vision-demo`  
**Evidence basis:** Google Ads Editor structure exports + public LP probes. **Not** performance exports.

Dashboard entry: [`xray/clean-rebuild.html`](../../xray/clean-rebuild.html)  
Dashboard mirror of these docs: [`xray/docs/rebuild/`](../../xray/docs/rebuild/) (keep in sync when editing)

## Strategic ladder (locked)

1. Tightly controlled **Search** first  
2. **Maximize Clicks** temporarily (conversion signal untrusted)  
3. Early diagnostics: CTR · search-term relevance · CPC · GA4 engagement · form behavior · manually reviewed lead quality  
4. Clean **employer-only** form + phone conversions  
5. Connect **qualified Zoho** outcomes  
6. **Max Conversions** only after verified signal  
7. Later: qualified-lead / opp / customer **value bidding**

**v1 out of scope:** PMax · Demand Gen · DSA · broad match · large competitor build

## Deliverables

| # | File | Phase |
|---|------|-------|
| 1 | [01-recent-performance-evidence.md](./01-recent-performance-evidence.md) | Evidence + missing-data request |
| 2 | [02-usa-au-v1-campaign-blueprint.md](./02-usa-au-v1-campaign-blueprint.md) | USA + AU Search architecture |
| 3 | [03-keyword-negative-launch-set.md](./03-keyword-negative-launch-set.md) | Keywords + negatives |
| 4 | [04-paid-lp-requirements.md](./04-paid-lp-requirements.md) | Canonical paid LP per market |
| 5 | [05-employer-gate-experiment-plan.md](./05-employer-gate-experiment-plan.md) | Gate baseline + variants |
| 6 | [06-callrail-implementation-map.md](./06-callrail-implementation-map.md) | CallRail event hierarchy |
| 7 | [07-ga4-gtm-ads-event-map.md](./07-ga4-gtm-ads-event-map.md) | GA4 / GTM / Ads map |
| 8 | [08-zoho-field-lifecycle-contract.md](./08-zoho-field-lifecycle-contract.md) | Zoho contract (no writes) |
| 9 | [09-bidding-migration-ladder.md](./09-bidding-migration-ladder.md) | Bidding stages 1–4 |
| 10 | [10-launch-readiness-checklist.md](./10-launch-readiness-checklist.md) | Launch checklist |
| 11 | [11-risks-decisions-owners.md](./11-risks-decisions-owners.md) | Risks · decisions · owners |

## Certainty labels (use everywhere)

| Label | Meaning |
|-------|---------|
| **Verified** | Proven from Editor CSV structure, public HTTP probes, or repo docs |
| **Reasonable inference** | Strong structural pattern; not traffic/ROAS proof |
| **Unknown** | Needs Ads UI / GA4 / CRM / CallRail / VC answer |

**Never confuse Editor row counts / Final URL refs with traffic.**

## Scratch (structure mining only)

- [`_scratch_negatives.json`](./_scratch_negatives.json) — unique negative terms from Editor (structure frequency ≠ importance)  
- [`_scratch_keywords.json`](./_scratch_keywords.json) — positive keyword archaeology + enabled-brand RSA assets  

Do **not** paste scratch buckets into Ads without human curation (esp. `geo_irrelevant` / `other` — mining noise).
