# US baseline & measurement repair — implementation report

**Date:** 18 August 2026  
**Market:** US only. AU campaigns, budgets, RSAs, and AU phone rules were not changed. Shared event helpers and `StaffingBaselineLanding` now use canonical event names on `/au` as well (safe: names only; AU validation unchanged).

**Clean measurement start (after vision production deploy):** `2026-08-18`

---

## Implemented and deployed

| Item | Where |
| --- | --- |
| Vision production | `dpl_34uzqp6wzc4hkYDXRFkZ3U71TcG6` — 18 Aug 2026 09:36:20 PDT — https://www.virtualcoworker.app |
| Freeze `US_BASELINE_2026-08-18` | Live `/us` has `data-lp-version="baseline_v1_2026_08"` and `data-baseline-label="US_BASELINE_2026-08-18"` |
| Authoritative LP version | `vision/config/lp-version.ts` |
| Canonical events (code on live host) | dataLayer path. GTM/GA4 forwarding not confirmed. |
| US phone validation | Live `/api/lead` + client. Interactive prod check still George. |
| `/us/staffing` candidate | Live, `noindex`, lp_version `staffing_agency_candidate_2026_08_18`. Not an Ads Final URL. |
| Launch Control section `US Baseline & Measurement Repair` | https://vc-xray.vercel.app/launch-control.html#us-baseline-measurement |
| Baseline registry JSON | https://vc-xray.vercel.app/data/us-baseline-2026-08-18.json |
| Suffix dry-run, destination map, Zoho GCLID handoff | https://vc-xray.vercel.app/docs/ads-launch/ |

X-ray: **https://vc-xray.vercel.app** (`dpl_2DvkTBJ24eFs1EChcfwqTGHJTQ5C`).

---

## Implemented, awaiting live verification (GA4 / Ads / Zoho)

| Item | Status |
| --- | --- |
| `lp_view` / `form_start` / step / submit / phone / seeker / validation events in DebugView | Code live. GTM must map. Not confirmed in GA4. |
| No duplicate GA4/GTM firing | Code has one dataLayer name. GTM tags not audited live. |
| GCLID/UTMs on a real Zoho record | Payload code live. Zoho field join unconfirmed. |
| One Ads conversion reconstruction | Unresolved. See table below. |

---

## Completed through GA4 / GTM / Ads / Zoho APIs

**None.** No GA4 Admin API, no GTM publish, no Ads mutate, no Zoho write. Ads API remains read-only / 1–2 cheap probes (none added in this pass).

---

## Blocked — George’s checklist (exact)

Live: https://vc-xray.vercel.app/launch-control.html#us-baseline-measurement

1. **Import US suffix CSV in Google Ads Editor** (account `496-715-1855`). File: `ads-launch/google-ads-editor-us-suffix-drop-lp-version.csv`. Campaigns stay **Enabled**. AU suffix unchanged. Recipe: `ads-launch/US-ADS-SUFFIX-DRY-RUN-2026-08-18.md`. Do not import the full paused Stage 1 package.
2. **GTM-M92DX9BJ** (US) → GA4 `G-2V3V0BS6JW` (property `549075481`): one Custom Event trigger per canonical name; drop tags for `phone_click`, `form_submit`, `form_submit_success`, `employer_form_started`. Do not publish unrelated workspace changes.
3. **GA4 event-scoped custom dimensions** (Admin → Custom definitions): `lp_version`, `baseline_label`, `landing_page_type`, `cta_location`, `role_selected`, `step_name`, `error_category`, `lead_reference`, `redirect_reason`. Parameter name = dimension name.
4. Mark `employer_inquiry_submitted` as a GA4 key event **if intended**. Do not mark `form_start` or `phone_cta_clicked` as Ads primary.
5. **Ads** `496-715-1855`: confirm `VC_US_Thank_You` imports `employer_inquiry_submitted` and is the form action. 60s website calls stay the call-quality signal.
6. **DebugView / Realtime** on `/us`: confirm each event once, no duplicates, no PII.
7. **Zoho admin:** field `utm_gclid` (not `$gclid`). Procedure: `ads-launch/zoho/US-GCLID-HANDOFF-2026-08-18.md`. Missing GCLID ≠ organic.
8. Approve ad-group → Final URL map **before** any live reroute (`ads-launch/US-LP-DESTINATION-MAP-2026-08-18.md`).

---

## Intentionally not changed

- Live `/us` visual design, H1, guided-match flow, trust proof, phone visibility
- Budgets, bids, bidding strategies, keywords, match types, negatives, RSAs, campaign status
- No new experiment
- AU campaigns, AU Ads suffix, AU phone validation
- Brand campaigns
- Full Editor Stage 1 CSV regenerate / import
- Unrelated dirty working-tree files (`.local/`, other xray/ads-launch edits)

---

## One reported conversion

| Field | Verified |
| --- | --- |
| Campaign | `VC_US_S_CORE` (1.0 conversions / 2.0 all_conversions, 10–16 Aug) |
| Timestamp | Likely 14 Aug; exact hour unverified |
| Action, AG, keyword, GCLID, device, SHA | Unverified |
| Classification | **Unresolved** — do not roll `/us` back |

Full table: `reports/us-employer-conversion-reconstruction-2026-08-18.md`

---

## Exact files changed (this assignment)

**Vision:** `config/lp-version.ts`, `config/lp-baseline.ts`, `config/lp-staffing-agency.ts`, `config/lp-real-estate.ts`, `lib/tracking.ts`, `lib/lp-events.ts`, `lib/phone-format.ts`, `lib/lead-validation.ts`, `lib/job-seeker-exit.ts`, `lib/zoho/payload.ts`, `app/api/lead/route.ts`, `app/components/StaffingBaselineLanding.tsx`, `app/components/GuidedMatchGate.tsx`, `app/components/LeadGate.tsx`, `app/components/DataTrackClicks.tsx`, `app/us/staffing/page.tsx`, `docs/US-BASELINE-2026-08-18.md`, plus tests (`lp-events.test.ts`, `phone-format.test.ts`, `lead-validation.test.ts`, `lp-staffing-agency.test.ts`, and related tracking tests).

**Ads / ops:** `ads-launch/build_stage1_editor_package.py`, `ads-launch/google-ads-editor-us-suffix-drop-lp-version.csv`, `ads-launch/US-ADS-SUFFIX-DRY-RUN-2026-08-18.md`, `ads-launch/US-LP-DESTINATION-MAP-2026-08-18.md`, `ads-launch/zoho/US-GCLID-HANDOFF-2026-08-18.md`.

**X-ray:** `launch-control.html`, `data/us-baseline-2026-08-18.json`, `smoke-live.mjs`, copied docs under `xray/docs/ads-launch/`.

**Reports:** `reports/us-employer-conversion-reconstruction-2026-08-18.md`, `reports/us-baseline-measurement-repair-2026-08-18.md`.

---

## Tests / build

`vision/`: `npm test` **199 passed** (33 files). `npm run typecheck` pass. `npm run validate:routes` pass (`/us/staffing` listed). `npm run build` pass; `/us/staffing` static.

---

## Live URLs to inspect

- https://www.virtualcoworker.app/us
- https://www.virtualcoworker.app/us/staffing (candidate; noindex)
- https://vc-xray.vercel.app/launch-control.html#us-baseline-measurement

---

## Attribution gaps still open

- Site captures GCLID/UTMs; Zoho `utm_gclid` join is **unconfirmed**.
- Absence of GCLID in Zoho does **not** prove organic.
- Events in code ≠ events in GA4 until GTM forwards them and DebugView shows them.
- Ads suffix `lp_version=stage1-v7` remains on live campaigns until George Posts the Editor import.
