# Zoho tooling (Virtual Coworker) — **DEFERRED DURING COLD START** (2026-08-14)

Zoho is **not cancelled**. It is **not** an active Google Ads optimization project right now.

Helpers and docs for OAuth bootstrap, schema inventory, and CRM READY mapping. Direct adapter stubs live in `vision/lib/zoho/` (feature-gated, mocked tests).

**Cold-start lock:** `ads-launch/ZOHO-COLD-START-DEFERRED-2026-08-14.md`

- Keep API access **read-only**. Keep `.app` → Zoho production writes **OFF**.
- Do **not** build a new Zoho-to-Google Ads offline conversion integration.
- Do **not** add Zapier. Do **not** change existing Zoho records, workflows, fields, users, or permissions.
- Do **not** make existing Zoho-related Google Ads conversions Primary.
- Do **not** alter bidding through the API. Continue Maximize Clicks.

**Important:** George’s UI shows **no Leads** and an employer spine (Accounts → Contacts → Job Orders → Placements). Product may be **Zoho Recruit** or customized CRM. Do **not** assume CRM API V8 or hardcode Leads. See **`DEFERRED-PLATFORM-DISCOVERY.md`**.

Missing `VC_*` / `.app` stamps on current Zoho rows is **expected** (new forms are not connected). That is not a Zoho failure.

## Commands (repo root) — parked until the revisit gate

```bash
npm run zoho:bootstrap   # Self Client → refresh token → .local/zoho/credentials.json
npm run zoho:inventory   # Modules + fields → CRM-SCHEMA-INVENTORY.md
```

Current scripts are **CRM V8–oriented**. Treat live bootstrap/inventory/API implementation as **deferred** until discovery picks Recruit API V2 vs CRM API V8 (or confirms customized CRM). Do not run these as Ads optimization work during cold start.

## Layout

| Path | Purpose |
|------|---------|
| `DEFERRED-PLATFORM-DISCOVERY.md` | **Later-phase** product/API discovery + audit checklist |
| `.local/zoho/` | Raw responses + credentials (gitignored) |
| `CRM-SCHEMA-INVENTORY.md` | Sanitized inventory placeholder (not CRM-V8-assumed) |
| `GEORGE-5-MINUTE-SETUP.md` | Short operator path (after discovery) |
| `ZOHO-FIELD-MAPPING-WORKSHEET.md` | Verified API name worksheet |
| `NATIVE-GOOGLE-ADS-AUDIT.md` | Native Ads connector checklist (separate; observe only) |
| `PRODUCTION-LEAST-PRIVILEGE.md` | Scope runbook (rewrite after platform ID) |

## Sequencing

This folder is the **CRM READY** parallel track. It is **not** a **TRAFFIC READY** gate and **not** this week’s Google Ads optimization work. See `ads-launch/DECISIONS.md` and `ZOHO-COLD-START-DEFERRED-2026-08-14.md`.

**Revisit only after:** enough qualified employer enquiries · VC names the Zoho owner · existing Zoho/Zapier/Ads uploads documented and reconciled · one `.app` Sales Enquiry tested safely end to end · CRM outcome definitions/values consistent enough to validate.

Ads verdicts stay:

```
SAFE TO IMPORT INTO EDITOR FOR REVIEW
SAFE TO POST WHILE PAUSED
NOT SAFE FOR PAID TRAFFIC until minimum traffic gates pass
```

## Hard rules

- No live CRM/Recruit record writes from these CLIs.
- No Google Ads Post/enable from this folder.
- No new offline-conversion integration or Zapier.
- No secrets in Git / `NEXT_PUBLIC_*`.
- Webhook env `ZOHO_WEBHOOK_URL` ≠ direct Zoho sync.
- Native Google Ads audit ≠ George’s pending Ads developer token.
