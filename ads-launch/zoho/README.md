# Zoho tooling (Virtual Coworker) — inventory/API **deferred**

Helpers and docs for OAuth bootstrap, schema inventory, and CRM READY mapping. Direct adapter stubs live in `vision/lib/zoho/` (feature-gated, mocked tests).

**Important:** George’s UI shows **no Leads** and an employer spine (Accounts → Contacts → Job Orders → Placements). Product may be **Zoho Recruit** or customized CRM. Do **not** assume CRM API V8 or hardcode Leads. See **`DEFERRED-PLATFORM-DISCOVERY.md`**.

## Commands (repo root) — deferred until platform ID

```bash
npm run zoho:bootstrap   # Self Client → refresh token → .local/zoho/credentials.json
npm run zoho:inventory   # Modules + fields → CRM-SCHEMA-INVENTORY.md
```

Current scripts are **CRM V8–oriented**. Treat live bootstrap/inventory/API implementation as **deferred** until discovery picks Recruit API V2 vs CRM API V8 (or confirms customized CRM).

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

This folder is the **CRM READY** parallel track. It is **not** a **TRAFFIC READY** gate for initial Maximize Clicks Enable. See `ads-launch/DECISIONS.md`.

Ads verdicts stay:

```
SAFE TO IMPORT INTO EDITOR FOR REVIEW
SAFE TO POST WHILE PAUSED
NOT SAFE FOR PAID TRAFFIC until minimum traffic gates pass
```

## Hard rules

- No live CRM/Recruit record writes from these CLIs.
- No Google Ads Post/enable from this folder.
- No secrets in Git / `NEXT_PUBLIC_*`.
- Webhook env `ZOHO_WEBHOOK_URL` ≠ direct Zoho sync.
- Native Google Ads audit ≠ George’s pending Ads developer token.
