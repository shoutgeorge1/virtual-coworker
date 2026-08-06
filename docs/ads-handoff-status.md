# Virtual Coworker × ShoutGeorge Ads — status (2026-08-05)

## Where things live

| What | Path |
|---|---|
| Client pilot / build | `~/Developer/virtual-coworker` (this project) |
| Personal Ads API toolkit | `~/Developer/shoutgeorge-ads` |
| VC account IDs (private) | `~/Developer/shoutgeorge-ads/clients/virtual-coworker.env` |

## Access

- **MCC:** Shout George — George Aguilar — `119-318-9031`
- **VC USA:** `496-715-1855` (Virtual Coworker USA - Braden Yuill)
- **VC AU:** `573-539-1940` (Virtual Coworker AU - Braden Yuill)
- **MCC link:** Accepted by Braden — USA + AU under Shout George
- **Still verify:** Admin permission inside each US + AU account (separate from MCC Accept)
- **Pilot payment:** On its way to George’s bank (in transit — not yet confirmed cleared)

## API — treat tokens as scarce

- OAuth + developer token configured in `shoutgeorge-ads/.env` (gitignored)
- Cloud project: **Shoutgeorge Ads** (separate from YouTube)
- Access level: **Explorer** until Basic approved (test accounts only for live API; tiny daily ops budget)
- Basic Access application: in progress / submit if not yet done
- Form answers + tool doc: `shoutgeorge-ads/docs/basic-access-application.md`

**Hard rule for agents + humans:** do **not** burn Ads API quota for exploration, inventory dumps, or Editor cleanup. Prefer **browser UI + Google Ads Editor**. API only for intentional, minimal reads after Basic lands (or test accounts under Explorer). On `RESOURCE_EXHAUSTED`: stop, do not retry.

## Google Ads Editor (local)

- Path: `~/Library/Application Support/Google/Google-AdWords-Editor/`
- Editor cleaned Aug 4; download USA + AU when ready
- **Zero Ads API calls** for Editor cleanup — it is desktop SQLite only

## Stage 1 machine (built)

**Path:** Google Ads → independent microsite. WordPress stays as-is (not the paid destination).

1. MCC Accept done → verify Admin in-account → USA + AU visible under MCC (browser)
2. Stage 1 LP + server-validated employer form verified (Zoho/CallRail optional — do not block)
3. Download USA + AU into clean Editor (ShoutGeorge login only)
4. Import paused Stage 1 package from `ads-launch/` (nine role campaigns US+AU; brand deferred — see `FULL-BUILD-REPORT.md`)
5. Confirm Final URLs = Stage 1 LPs (not WP) · enable only after launch-control checklist
6. **Editor fact (structure):** Enabled brand RSAs currently point at WordPress, not try.* — try.* ads are paused (AU try.* also disapproved on enabled campaign). Live spend Unknown until Admin UI.

Editor is the bulk tool — agent does the heavy CSV/structure lift; George reviews and posts. Prefer browser + Editor; **no Ads API burns**.

## Next (not blocked on MCC Accept)

1. Confirm USA + AU show under MCC; verify Admin inside each account
2. Approvals: budgets/CPC, phones, lead inbox; payment clearing
3. Open Google Ads Editor → ShoutGeorge → **Download** USA `496-715-1855` + AU `573-539-1940` only
4. Import paused Stage 1 CSV · enable only after Launch Control green
