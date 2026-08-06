# Zoho CRM schema inventory (sanitized)

Generated: placeholder — run `npm run zoho:inventory` after `npm run zoho:bootstrap`.

API: Zoho CRM **v8**

> Raw JSON lives only under `.local/zoho/` (gitignored). No PII / tokens in this file.

## Bootstrap scopes used (READ-only)

```
ZohoCRM.org.READ,ZohoCRM.users.READ,ZohoCRM.settings.modules.READ,ZohoCRM.settings.fields.READ,ZohoCRM.modules.READ,ZohoCRM.bulk.READ,ZohoCRM.coql.READ
```

## Status

**Credentials / inventory not run yet in this environment.** Adapter code and mocked tests are ready; live metadata pending George bootstrap.

**Request for Zoho admin (copy/paste):** George needs CRM API read access for Virtual Coworker lead inventory — not full Zoho One admin for every app. Please confirm: (1) **Zoho One seat** is assigned (login exists); (2) the **CRM application** is enabled on that seat; (3) the CRM **profile/role** allows Modules + Fields metadata API (Settings → Modules/Fields read) — a One seat alone does not grant CRM Admin; (4) a **Self Client** in the API Console for the correct data-center may be created by a developer with CRM access (Client ID/secret + grant code with READ-only scopes listed above) — Self Client ≠ CRM Admin; (5) separately, only a **CRM Admin** (or equivalent) can authorize the **native Zoho ↔ Google Ads** connector and change auto-tagging — do not treat Self Client OAuth as Ads connector approval.

## Modules

_Run inventory to populate._

## Related docs

- `GEORGE-5-MINUTE-SETUP.md`
- `ZOHO-FIELD-MAPPING-WORKSHEET.md`
- `NATIVE-GOOGLE-ADS-AUDIT.md`
- `PRODUCTION-LEAST-PRIVILEGE.md`
