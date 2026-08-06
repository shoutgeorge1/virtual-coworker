# Cursor mega prompt — repair Google Ads Editor package + promote Zoho CRM into Phase 0

Paste everything below into Cursor Agent while the Virtual Coworker repository is open.

---

You are working in George’s existing repository:

- Local repo: `/Users/george/Developer/virtual-coworker`
- Target branch: `vision-demo`
- Google Ads accounts:
  - US: `496-715-1855`
  - AU: `573-539-1940`
- Current paid microsite preview: `https://vision-three-alpha.vercel.app`
- Launch Control: `https://vc-xray.vercel.app/launch-control`

## Mission

Repair the Google Ads Editor package before George imports it, make the import impossible to confuse between US and AU, produce a plain-English preflight inventory, and move Zoho CRM inventory/direct lead delivery/offline conversion planning into the real Phase 0 launch path.

Do not upload, import, Post, enable, deploy, purchase, authorize OAuth, or change anything in Google Ads or Zoho. This is local repo work only. All campaigns, ad groups, keywords, ads, and assets must remain Paused. George will handle the Google Ads Editor review and any external authorization separately.

Do not ask broad planning questions. Inspect the actual repo, implement the safe parts, document genuine blockers, and stop only where credentials, live Zoho schema, Google conversion-action IDs, or an external authorization are actually required.

## Before editing

1. Read any `AGENTS.md` files that apply.
2. Run `git status --short --branch` and preserve all unrelated or existing worktree changes.
3. Confirm the active branch. Do not reset, clean, stash, discard, or overwrite user work.
4. Read these files completely before changing anything:
   - `ads-launch/build_stage1_editor_package.py`
   - `ads-launch/google-ads-editor-import.csv`
   - `ads-launch/FULL-BUILD-REPORT.md`
   - `ads-launch/CHATGPT-DEBRIEF.md`
   - `ads-launch/DECISIONS.md`
   - `ads-launch/LAUNCH-SHEET.md`
   - `ads-launch/PHASED-ACTIVATION.md`
   - `ads-launch/07-phased-activation-recommendation.md`
   - `ads-launch/12-blocker-decision-list.md`
   - `xray/launch-control.html`
   - `xray/lead-routing.html`
   - `vision/app/api/lead/route.ts`
   - `vision/lib/lead-delivery.ts`
   - `vision/lib/tracking.ts`
   - the employer form component that calls `/api/lead`
   - `.env.example`, `vision/package.json`, and relevant tests
5. Run the existing builder and tests once to capture the current baseline. Do not “fix” unrelated failures.

## Confirmed current-state facts

Treat these as an audit starting point, then verify them in the code:

- Current combined CSV contains 4 campaigns, 40 ad groups, 1,568 positive keywords, 116 RSAs, and 764 campaign-negative rows (191 unique negatives repeated across 4 campaigns).
- Positive keywords are 1,182 Exact and 386 Phrase. No Broad positive keywords.
- Current package has 2 campaigns per market: `VC_{US|AU}_S_CORE` and `VC_{US|AU}_S_ROLES`.
- Everything is Paused.
- Current builder uses `{_campaign}` and `{_adgroup}` in the Final URL suffix without defining those custom parameters.
- Current builder uses a `Max CPC` column and fills it on campaign/ad-group/keyword/ad rows even though Maximize Clicks needs a campaign-level `Maximum CPC bid limit`.
- The combined CSV does not safely map every row to a Google Ads customer ID.
- Current launch-control step 6 still tells George to import one combined file, and Zoho is still described as “later.”
- `/api/lead` already captures `gclid`, `gbraid`, `wbraid`, UTMs, landing page, market, category, variant, and `submission_id`.
- Current “Zoho” delivery is only a generic `ZOHO_WEBHOOK_URL` POST. It is not a verified direct Zoho CRM integration.

## Workstream A — repair the Google Ads Editor builder

### A1. Make account routing explicit and safe

Add a single source of truth such as:

```python
ACCOUNT_IDS = {
    "US": "496-715-1855",
    "AU": "573-539-1940",
}
```

Every generated row must be deterministically associated with exactly one market/account.

Generate all of these outputs:

1. `ads-launch/google-ads-editor-import-us.csv`
   - US rows only
   - Account/customer ID `496-715-1855`
2. `ads-launch/google-ads-editor-import-au.csv`
   - AU rows only
   - Account/customer ID `573-539-1940`
3. `ads-launch/google-ads-editor-import-multi-account.csv`
   - both markets
   - an `Account` column on every row containing the correct customer ID
   - clearly documented as manager-level multi-account import only
4. Preserve `ads-launch/google-ads-editor-import.csv` only if compatibility requires it. If preserved, make it an exact copy of the safe multi-account file and document that fact. Never leave an ambiguous combined file behind.

The split US/AU files are the recommended operator path. Update all docs and Launch Control to point George to the two split files, one account at a time.

### A2. Fix Maximize Clicks bid caps

Use Google Ads Editor’s campaign-level header exactly:

`Maximum CPC bid limit`

Requirements:

- US campaign rows: `8`
- AU campaign rows: `6`
- Only campaign rows may contain `Maximum CPC bid limit`.
- Ad group, keyword, ad, negative, and asset rows must leave it blank.
- Remove the automated-bidding misuse of `Max CPC` from non-campaign rows.
- Preserve `Bid Strategy Type = Maximize Clicks` on the campaign rows.
- Add QA assertions that reject a cap on a non-campaign row and reject a missing/wrong cap on a campaign row.

Reference: `https://support.google.com/google-ads/editor/answer/94241?hl=en`

### A3. Fix URL tracking parameters

Do not use undefined `{_campaign}` or `{_adgroup}` custom parameters.

Use supported ValueTrack IDs. Safe default:

```text
utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}&utm_device={device}&lp_version=stage1-v7
```

Keep `Tracking template = {lpurl}` if a tracking template is emitted. Do not double-append UTMs.

Apply the tracking template and Final URL suffix at campaign level only unless the repo contains a documented reason for a lower-level override. Child rows must not redundantly create identical URL-option overrides.

Do not bump the landing-page version merely because the Editor package changed. If useful, introduce a separate package version such as `stage1-editor-v8` while preserving `lp_version=stage1-v7` until the LP code itself changes.

Add QA assertions that fail on:

- `{_campaign}` or `{_adgroup}` anywhere in generated files
- more than one UTM layer
- a tracking template without `{lpurl}`
- a child-level URL-option override without an explicit allowlist

Reference: `https://support.google.com/google-ads/answer/6305348?hl=en`

### A4. Put risky commercial negatives on hold

The current list uses campaign-level Broad negatives. Do not ship generic negatives that can suppress bottom-funnel employer research.

Remove these from active generated negatives and place them in a documented `NEGATIVE_REVIEW_HOLDOUT` (or equivalent) that is reported but not imported:

- `review`
- `reviews`
- `pricing`
- `virtual assistant cost`
- `virtual assistant philippines cost`
- `cost of a virtual assistant`
- `cost of virtual assistant philippines`
- `how much does a virtual assistant cost`
- `how much is a virtual assistant`
- `how much does a va cost`
- `how much do virtual assistants cost`
- `top 10 virtual assistant companies`
- `top 10`
- `cheap`
- `cheapest`
- `filipina va`

Reason: cost, pricing, reviews, comparisons, and `filipina va` can be commercial employer intent. George’s locked strategy is PH/Filipino/offshore high-intent first, with enough volume to learn. These should be judged from real search terms and lead quality, not blocked pre-launch.

Keep the obvious job-seeker, training, Spanish/LATAM, excluded-vertical, marketplace, and known competitor exclusions unless QA reveals a positive collision or the evidence docs say otherwise. Do not casually broaden the negative list.

Generate a negative audit report containing:

- active negative count per campaign
- held-out commercial terms and reason
- exact positive/negative collisions
- substring/theme risks
- duplicate negatives
- negatives that could block Phase 1 PH-shaped intent

### A5. Produce review manifests, not enable files

Generate plain review CSVs or Markdown tables for:

- full US inventory
- full AU inventory
- Phase 1 US keyword manifest
- Phase 1 AU keyword manifest

Each row should show account, campaign, ad group, keyword, match type, phase, Final URL, and status. These are review artifacts only; do not create an “Enabled” import file.

Phase 1 definition remains locked:

- Philippines / Philippine / Filipino / Filipina / offshore intent
- plus hire, VA, outsource, or role intent
- Exact first plus tight Phrase
- across Core and every relevant Roles category, including bookkeeping/accounting
- generic Core heads later
- US before AU

Compute counts from source; do not hard-code the previously observed ~596 keywords per market.

## Workstream B — strengthen automated preflight QA

Create or extend a deterministic validation command. Prefer the existing Python builder plus standard-library tests unless the repo already has a better pattern.

The validator must fail non-zero on any of the following:

- wrong or missing Account/customer ID
- US entity inside AU file or AU entity inside US file
- any enabled entity
- any Broad positive keyword
- duplicate positive targeting within the same account/campaign
- positive/negative collision
- active risky-negative holdout term
- missing campaign budget
- wrong/missing campaign-level Maximum CPC bid limit
- bid limit on non-campaign row
- undefined custom tracking parameter
- double UTMs
- wrong market Final URL
- WordPress Final URL or asset URL
- Core routed anywhere except market home
- Roles routed anywhere except matching category page
- search/display expansion accidentally enabled
- blank RSA slots
- duplicate RSA assets where uniqueness is required
- character-limit violation
- missing parent campaign/ad group
- malformed CSV shape or mixed row lengths
- approval placeholders or secret-looking values

Write one operator-facing report, for example:

`ads-launch/EDITOR-PREFLIGHT-REPORT.md`

It must contain:

- package version and generated timestamp
- exact output filenames
- account IDs
- per-file and per-campaign counts
- budgets and bid caps
- keyword match-type totals
- Phase 1 totals
- negatives active vs held out
- tracking suffix
- Final URL map
- all checks passed/failed
- explicit text: `SAFE TO IMPORT FOR REVIEW` or `NOT SAFE TO IMPORT`
- explicit text: `IMPORT/POST/ENABLE NOT PERFORMED`

Do not call a package “safe to import” unless every local test passes.

## Workstream C — make the Editor workflow honest in Launch Control

Update `xray/launch-control.html` and all companion docs so the operator sequence is:

1. Download fresh US and AU accounts into Editor.
2. Rebuild and read `EDITOR-PREFLIGHT-REPORT.md`.
3. Import the US split file into the US account.
4. Run Editor `Check changes`; inspect warnings/errors; leave Paused.
5. Import the AU split file into the AU account.
6. Run Editor `Check changes`; inspect warnings/errors; leave Paused.
7. Post only after George has reviewed the proposed changes; if posted, everything remains Paused.
8. Enabling remains a completely separate explicit decision after all launch gates are green.

Do not tell George to import the old ambiguous combined file.

Make the checklist visually obvious about the difference between:

- local CSV validation
- Editor import for review
- Editor Post while Paused
- actual Enable/spend

Preserve the locked Phase 1 activation order in `PHASED-ACTIVATION.md`.

## Workstream D — Zoho CRM export/inventory becomes Phase 0

George now has access to Zoho One. For this project, scope the audit to Zoho CRM and the integrations that affect lead routing/conversion measurement. Do not pretend this means every Zoho One app has been audited.

### D1. Create a safe Zoho export intake path

Add a documented local-only folder such as:

`.local/zoho/`

Add specific `.gitignore` rules so raw Zoho backups, extracted CSVs, attachments, tokens, and generated PII never enter Git.

Create a local inspection command that accepts a Zoho CRM backup ZIP or extracted folder and produces only sanitized metadata. It must never print or commit lead names, emails, phones, addresses, messages, tokens, or attachment contents.

Sanitized output should include:

- file/module names
- record counts
- column/API-field names
- null percentages
- likely IDs and relationship columns
- detected layouts/status/source fields
- presence of GCLID/GBRAID/WBRAID/UTM/submission ID fields
- presence of Leads, Contacts, Accounts, Deals/Potentials, Activities, Campaigns, and custom modules
- workflow/conversion-relevant stage vocabulary if available without exposing PII
- obvious data-quality issues

Write sanitized outputs to something like:

- `ads-launch/zoho/ZOHO-CRM-INVENTORY.md`
- `ads-launch/zoho/zoho-schema-summary.json`
- `ads-launch/zoho/ZOHO-FIELD-MAPPING-WORKSHEET.md`

The worksheet must distinguish:

- display label
- API name
- module
- type
- required/unique/external-ID status
- current usage
- proposed VC field mapping
- verified vs assumed

Do not infer API names from display labels. Zoho direct integration stays blocked until actual API names are verified.

Official CRM backup limitations must be documented: the backup includes module records and attachments, but not IMAP email content, Documents, or integration-derived data. A “CRM backup” is not literally every Zoho One datum.

References:

- `https://help.zoho.com/portal/en/kb/crm/data-administration/data-backup/articles/requesting-data-backup`
- `https://www.zoho.com/crm/developer/docs/api/v8/modules-api.html`
- `https://www.zoho.com/crm/developer/docs/api/v8/field-meta.html`
- `https://www.zoho.com/crm/developer/docs/api/v8/bulk-read/create-job.html`

### D2. Audit native Zoho ↔ Google Ads before custom offline uploads

Add a checklist to determine whether the Zoho CRM account already has the native Google Ads integration configured:

- connected Google Ads customer accounts
- Google Ads tab present
- auto-tagging/GCLID capture status
- Google Ads Information section on Leads/Contacts/Deals
- `Google Ads Conversion Export` view
- conversion import failures
- current CRM milestones exported to Ads
- ownership and permissions
- whether the integration supports this custom Next.js/server-side form path
- whether it is compatible with Google’s current 2026 Data Manager migration

Do not run native integration and a custom upload path for the same milestone until duplicate behavior is proven safe.

References:

- `https://help.zoho.com/portal/en/kb/crm/integrations/google/google-ads/articles/google-ads-crm-integration`
- `https://help.zoho.com/portal/en/kb/crm/integrations/google/google-ads/articles/track-google-ads-data`

### D3. Build the direct Zoho CRM adapter safely, but keep it feature-gated

Replace the fiction that an arbitrary `ZOHO_WEBHOOK_URL` equals direct CRM sync.

Implement a proper server-only Zoho CRM adapter behind an explicit feature flag. Keep the existing webhook as a separate fallback if useful, but name it honestly.

Suggested modules/files, adjusted to repo conventions:

- `vision/lib/zoho/client.ts`
- `vision/lib/zoho/config.ts`
- `vision/lib/zoho/map-lead.ts`
- tests with mocked `fetch`

Requirements:

- OAuth refresh-token flow is server-only.
- No access token, refresh token, client secret, or auth code may reach the browser, logs, generated reports, or Git.
- Respect Zoho data-center domains; do not hard-code `.com` if the live account uses another DC.
- Use Zoho CRM API V8.
- Use verified module and field API names only.
- Use a unique/external submission ID and Upsert where the live schema supports it.
- Map the existing `submission_id`, market, intent, name, email, phone, company, role, category, timeline, message, variant, UTMs, click IDs, landing page, referrer, LP version, and timestamps.
- Preserve `is_job_order=false` and `is_placement=false` on initial lead creation.
- Return the Zoho record ID and an honest delivery result internally.
- Redact PII and tokens from logs.
- Add bounded timeouts and retry only safe/idempotent operations.
- A Zoho failure must not be reported as success.
- If backup email/webhook delivery succeeds but Zoho fails, the online lead may still be durable, but `zoho_synced` must remain false and the retry/outbox path must retain the submission.
- Add an idempotent retry/outbox design; do not rely on Vercel process memory as durable storage.
- If no durable outbox exists in the current stack, document that as a blocker instead of faking one.
- Never accept a job seeker into the employer lead module.

Environment/config placeholders may be added to `.env.example`, but never add real credentials. Include only the minimum scopes required after the live module is known.

References:

- `https://www.zoho.com/crm/developer/docs/api/v8/insert-records.html`
- `https://www.zoho.com/crm/developer/docs/api/v8/upsert-records.html`
- `https://www.zoho.com/crm/developer/docs/api/v8/upsert-records-ext.html`

### D4. Define conversion events without inflating reality

Keep the existing honest online event:

- `employer_inquiry_submitted` = employer form accepted and durably delivered

Define offline CRM milestones separately and do not fire them until the Zoho field/stage mapping is verified:

- `qualified_lead`
- `job_order_created`
- `placement_created`

For each milestone document:

- source Zoho module
- exact verified trigger field and value
- timestamp source
- Google Ads account chosen by market
- conversion action ID/name (blocked until supplied)
- value and currency policy (blocked until approved)
- GCLID/GBRAID/WBRAID/user-provided-data match keys
- dedupe key: `submission_id + milestone`
- retraction/adjustment rule if a CRM stage is reversed
- maximum upload age and retry policy
- PH job-seeker exclusion

Do not equate:

- form submit with qualified lead
- lead with job order
- job order with placement
- phone click with qualified call
- Zoho record creation with revenue

Important 2026 implementation rule: do not build a new offline-conversion uploader against the legacy Google Ads API path. Google states that starting June 15, 2026, offline/enhanced-conversion-for-leads uploads migrate to the Data Manager API and new Google Ads API uploads are blocked except limited legacy allowlisting. Build a provider-neutral conversion outbox/export contract and document the Data Manager/native-Zoho decision. Do not send live conversions.

References:

- `https://support.google.com/google-ads/answer/15713840?hl=en`
- `https://support.google.com/google-ads/answer/2998031?hl=en`
- `https://support.google.com/google-ads/answer/16782203?hl=en`

### D5. Promote Zoho gates in Launch Control

Remove “Zoho access” from the vague Later bucket. Replace it with explicit statuses:

- Zoho login/access confirmed
- CRM backup downloaded
- modules/layouts/fields inventoried
- existing Google Ads integration audited
- lead module and owner confirmed
- field API mapping verified
- direct CRM test lead succeeds
- duplicate/idempotency test succeeds
- failure + backup delivery test succeeds
- qualified/job-order/placement stage mapping approved
- Data Manager/native Zoho offline conversion path selected
- live Google conversion-action IDs still required
- no live offline uploads until explicit approval

Zoho direct lead delivery should be a Phase 0 paid-readiness gate once selected as the durable lead destination. Offline qualified/job-order/placement feedback may remain a post-launch optimization gate if the primary lead is safely delivered and tracked, but the checklist must say that plainly.

## Workstream E — update canonical documentation

Update every stale statement that conflicts with the repaired package or Zoho status, including:

- `FULL-BUILD-REPORT.md`
- `CHATGPT-DEBRIEF.md`
- `DECISIONS.md`
- `LAUNCH-SHEET.md`
- `12-blocker-decision-list.md`
- `07-phased-activation-recommendation.md` only where import mechanics changed
- `xray/launch-control.html`
- `xray/lead-routing.html`
- relevant README/env docs

Preserve the locked activation strategy. Do not rewrite ad copy or keyword architecture “for vibes.”

Clearly separate these statuses everywhere:

- Editor package mechanically valid
- safe to import for review
- safe to Post while Paused
- paid lead delivery ready
- measurement ready
- offline CRM feedback ready
- approved to Enable

Only the first two can become green from this local task.

## Verification commands

Run the repo’s actual commands, adapting only if filenames differ:

```bash
python3 ads-launch/build_stage1_editor_package.py
python3 ads-launch/validate_editor_package.py
cd vision
npm test
npm run typecheck
npm run build
```

Also run the X-ray/static-site checks that exist in the repo. Do not deploy.

Inspect the generated CSVs programmatically and report exact counts. Spot-check at least:

- each campaign row
- one ad group per campaign
- one Exact and one Phrase keyword per campaign
- one RSA per campaign
- one negative per campaign
- one sitelink/callout/snippet per campaign
- Core and Roles Final URLs in both markets
- tracking suffix substitution syntax

## Acceptance criteria

Do not declare completion unless all are true:

- US and AU split import files exist and contain only their own account.
- Safe multi-account file has a correct Account column on every row.
- `Maximum CPC bid limit` is correct and campaign-only.
- Undefined custom tracking parameters are gone.
- Risky commercial negatives are held out, documented, and absent from imports.
- Positive campaign/ad-group/keyword/RSA architecture is unchanged unless a verified defect required a surgical change.
- Every entity remains Paused.
- Preflight validator passes.
- Plain-English inventory and Phase 1 manifests are generated.
- Launch Control points to the split imports and explains Import vs Post vs Enable.
- Zoho raw data/secrets are gitignored.
- Zoho inventory/mapping workflow exists.
- Direct Zoho adapter is honest, server-only, tested, and disabled until real schema/credentials are supplied.
- No live Zoho or Google Ads API call was made.
- No deploy, Post, Enable, OAuth authorization, or external write occurred.

## Final Cursor response format

Return a concise execution report with:

1. Files changed.
2. Exact generated package counts by market.
3. Exact negative terms held out.
4. Preflight/test/build results.
5. What George should import into which Editor account.
6. Explicit reminder: import/review first; Post remains Paused; Enable is separate.
7. Zoho work completed locally.
8. The smallest remaining live Zoho inputs needed:
   - backup/export
   - verified module/field API names
   - existing Google Ads integration status
   - approved OAuth client/scopes
   - lead owner/status mapping
   - Google conversion action IDs/value policy
9. Any blocker stated honestly without fake completion.

Do not commit or push unless George separately asks.

---

End of Cursor prompt.
