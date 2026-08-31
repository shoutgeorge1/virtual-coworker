# Zoho platform discovery and audit — **DEFERRED DURING COLD START**

**Status:** later-phase parallel workstream · **not** a TRAFFIC READY blocker · **not** an active Google Ads optimization project (locked 2026-08-14)

Zoho is **not cancelled**. Do **not** run inventory, OAuth, exports, adapter writes, or a new Zoho→Ads offline-conversion build from this doc until the [revisit gate](../ZOHO-COLD-START-DEFERRED-2026-08-14.md) is met.

Keep API **read-only**. Keep `.app` writes **OFF**. Do not add Zapier. Do not change existing Zoho records, workflows, fields, users, or permissions. Do not make Zoho-related Ads conversions Primary. Do not alter bidding via API. Continue Maximize Clicks.

Missing `VC_*` / `.app` attribution on current Zoho records is **expected** (new forms are not connected). That is not a Zoho failure.

## Observation (George — UI, 2026-08-06)

| Finding | Implication |
|---------|-------------|
| Can start **module exports**; cannot access full **Data Backup** | Prefer minimal module exports over org-wide backup |
| **No visible `Leads` module** | Do **not** hardcode Leads or assume standard CRM lead funnel |
| Visible modules include: **Accounts, Contacts, Job Orders, Placements, Campaigns, Calls, Meetings, Notes, Competitors** | Employer lifecycle may already be Account → Contact → Job Order → Placement |
| Product may be **Zoho Recruit** **or** heavily customized CRM | Do **not** assume Zoho CRM API V8 until org/product is identified |

Existing `npm run zoho:*` helpers and `vision/lib/zoho/*` are **CRM V8–oriented stubs**. Treat live inventory + API implementation as **deferred** until discovery completes. Do not request credentials or authorize APIs for this phase from Launch Control.

## Deferred task checklist (later phase)

1. **Identify exact Zoho product + org** via read-only metadata (CRM vs Recruit vs Zoho One app mix; data center; org id).
2. **Detect/support the correct API:** Zoho Recruit API V2 **or** Zoho CRM API V8 (or confirm customized CRM still on CRM APIs). Do not hardcode one path.
3. **Inventory** module labels, API names, layouts, required fields, ownership, statuses, workflows, assignment rules, and integrations — sanitized notes only; raw under `.local/zoho/` (gitignored).
4. **Inspect employer lifecycle:** Account → Contact → Job Order → Placement (how records relate; what “won” looks like).
5. **Determine where a new employer inquiry should enter** before any mapping or create path is designed.
6. **Manual audit starts with minimal exports only:** Accounts, Contacts, Job Orders, Placements.
7. **Exclude by default:** Candidates, Notes, Calls, Meetings, emails, attachments, and other sensitive data unless later necessary and approved.
8. **Build read-only least-privilege API auth instructions AFTER** the platform is identified (scopes/product-specific). Do not invent CRM-Leads scopes as the production path.
9. **Audit native Google Ads integration separately** (`NATIVE-GOOGLE-ADS-AUDIT.md`). Do **not** assume it needs George’s pending Ads developer token.
10. **Keep Zoho/API parallel to Max Clicks** — **not** a TRAFFIC READY blocker if durable delivery + live test + named responder are verified.

## Sequencing lock (unchanged)

| Status | Zoho relation |
|--------|----------------|
| **TRAFFIC READY** | Zoho record / OAuth / native Ads connector **not** required |
| **CRM READY** | Direct record + verified field map — **after** platform discovery |
| **OPTIMIZATION READY** | Downstream CRM/Ads feedback — later |

## Ads package verdicts (unchanged — do not conflate)

```
SAFE TO IMPORT INTO EDITOR FOR REVIEW
SAFE TO POST WHILE PAUSED
NOT SAFE FOR PAID TRAFFIC until minimum traffic gates pass
```

## Related docs

- `GEORGE-5-MINUTE-SETUP.md` — deferred until product/API known
- `CRM-SCHEMA-INVENTORY.md` — placeholder; title is historical; do not assume CRM V8/Leads
- `ZOHO-FIELD-MAPPING-WORKSHEET.md` — fill only after entry module is chosen
- `NATIVE-GOOGLE-ADS-AUDIT.md` — separate observe-only checklist
- `PRODUCTION-LEAST-PRIVILEGE.md` — rewrite scopes after platform ID
- `ads-launch/DECISIONS.md` · `ads-launch/CHATGPT-DEBRIEF.md` · Launch Control
