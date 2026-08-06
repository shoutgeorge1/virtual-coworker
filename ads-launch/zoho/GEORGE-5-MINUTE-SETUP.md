# Zoho CRM — George 5-minute setup

**Goal:** refresh token on disk + schema inventory → **CRM READY** path.  
**Not a TRAFFIC READY gate** — Max Clicks Enable does not wait on Zoho.  
No Ads enable. No live lead writes from these steps.

1. **API Console → Self Client** for the correct data center (US/AU/EU Accounts URL).
2. **Grant code** with READ-only scopes (copy from `bootstrap.py` / inventory output). No ALL/CREATE/UPDATE/DELETE.
3. From repo root: `npm run zoho:bootstrap` → paste Client ID, secret, grant code.
4. Confirm `.local/zoho/credentials.json` exists (mode 600). Secrets stay local — never commit, never `NEXT_PUBLIC_*`.
5. `npm run zoho:inventory` → read `CRM-SCHEMA-INVENTORY.md`. If blocked, send the admin paragraph in that file.
6. Fill `ZOHO-FIELD-MAPPING-WORKSHEET.md` with **verified API names** only.
7. For app runtime later: copy `ZOHO_CRM_*` from `.env.example` into `vision/.env.local` (server-only). Leave `ZOHO_CRM_ENABLED=false` until mapping verified.

**Locks:** webhook ≠ CRM sync · native Ads connector = separate admin checklist · `--apply-schema` needs your approval · no live CRM writes from bootstrap/inventory.
