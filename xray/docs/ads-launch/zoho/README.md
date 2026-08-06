# Zoho CRM tooling (Virtual Coworker)

Official **CRM API V8** helpers for OAuth bootstrap, schema inventory, and docs. Direct CRM adapter code lives in `vision/lib/zoho/` (feature-gated, mocked tests).

## Commands (repo root)

```bash
npm run zoho:bootstrap   # Self Client → refresh token → .local/zoho/credentials.json
npm run zoho:inventory   # Modules + fields → CRM-SCHEMA-INVENTORY.md
```

## Layout

| Path | Purpose |
|------|---------|
| `.local/zoho/` | Raw responses + credentials (gitignored) |
| `CRM-SCHEMA-INVENTORY.md` | Sanitized inventory |
| `GEORGE-5-MINUTE-SETUP.md` | Short operator path |
| `ZOHO-FIELD-MAPPING-WORKSHEET.md` | Verified API name worksheet |
| `NATIVE-GOOGLE-ADS-AUDIT.md` | Native Ads connector checklist (no authorize) |
| `PRODUCTION-LEAST-PRIVILEGE.md` | Scope runbook |

## Sequencing

This folder is the **CRM READY** parallel track. It is **not** a **TRAFFIC READY** gate for initial Maximize Clicks Enable. See `ads-launch/DECISIONS.md`.

## Hard rules

- No live CRM record writes from these CLIs.
- No Google Ads Post/enable from this folder.
- No secrets in Git / `NEXT_PUBLIC_*`.
- Webhook env `ZOHO_WEBHOOK_URL` ≠ direct CRM sync.
