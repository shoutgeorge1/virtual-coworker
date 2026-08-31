# Zoho — George setup (deferred until platform known)

**Goal (later):** read-only auth + schema inventory → **CRM READY** path.  
**Not a TRAFFIC READY gate** — Max Clicks Enable does not wait on Zoho.  
No Ads enable. No live lead writes from these steps.

## Stop — discover first

George’s UI observation (2026-08-06): **no visible Leads**; modules look like **Accounts / Contacts / Job Orders / Placements** (+ Campaigns, Calls, Meetings, Notes, Competitors). This may be **Zoho Recruit** or a heavily customized CRM.

**Do not** run bootstrap/inventory assuming CRM API V8 + Leads until `DEFERRED-PLATFORM-DISCOVERY.md` is started and the product/API is identified.

Full deferred checklist: **`DEFERRED-PLATFORM-DISCOVERY.md`**.

## When discovery says “go” (not tonight)

1. Confirm product (CRM vs Recruit) + data center from read-only metadata / admin.
2. **API Console → Self Client** for that product’s correct Accounts URL — scopes from the **post-discovery** least-privilege doc (not assumed CRM-Leads scopes).
3. **Grant code** READ-only only. No ALL/CREATE/UPDATE/DELETE.
4. From repo root: `npm run zoho:bootstrap` / `zoho:inventory` **only after** helpers match the chosen API (current scripts are CRM V8–oriented stubs — treat live use as **deferred**).
5. Confirm credentials stay under `.local/zoho/` (mode 600). Never commit, never `NEXT_PUBLIC_*`.
6. Fill `ZOHO-FIELD-MAPPING-WORKSHEET.md` with **verified API names** for the **chosen entry module** (may not be Leads).
7. Leave runtime `ZOHO_CRM_ENABLED=false` (or equivalent) until mapping verified + George approves writes.

**Locks:** webhook ≠ CRM/Recruit sync · native Ads connector = separate admin checklist · no live writes from bootstrap/inventory · not a Max Clicks blocker.
