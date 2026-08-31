# Zoho schema inventory (sanitized) — **DEFERRED**

Generated: placeholder — **do not run** inventory until platform discovery completes (`DEFERRED-PLATFORM-DISCOVERY.md`).

## Platform unknown (locked observation)

| UI observation (George) | Do not assume |
|-------------------------|---------------|
| No visible **Leads** module | Standard CRM lead module / hardcode `Leads` |
| Visible: Accounts, Contacts, Job Orders, Placements, Campaigns, Calls, Meetings, Notes, Competitors | Classic CRM-only funnel |
| Module exports available; full Data Backup not | Org-wide backup required for audit |
| May be Zoho Recruit **or** heavily customized CRM | Zoho CRM API **V8** as the only path |

API target: **TBD** — Recruit API V2 **or** CRM API V8 (confirm via read-only metadata).

> Raw JSON (when eventually collected) lives only under `.local/zoho/` (gitignored). No PII / tokens in this file.

## Bootstrap scopes

**Deferred.** Do not paste CRM V8 Leads scopes as production truth. After product ID, document READ-only scopes in `PRODUCTION-LEAST-PRIVILEGE.md`.

Historical CRM V8 READ bundle (may be wrong for this org — reference only):

```
ZohoCRM.org.READ,ZohoCRM.users.READ,ZohoCRM.settings.modules.READ,ZohoCRM.settings.fields.READ,ZohoCRM.modules.READ,ZohoCRM.bulk.READ,ZohoCRM.coql.READ
```

## Status

**Live inventory + API implementation = deferred.** Adapter/CLI stubs exist for CRM V8; they are not proof of the live product. No credentials requested from this placeholder.

**When discovery starts:** identify product/org → choose API → minimal exports (Accounts, Contacts, Job Orders, Placements only) → then metadata inventory. Exclude Candidates, Notes, Calls, Meetings, emails, attachments unless later necessary.

**Admin ask (later, after product known):** seat + app access for the **actual** Zoho product; profile that allows modules/fields metadata READ; Self Client for that data center — Self Client ≠ CRM/Recruit Admin ≠ native Google Ads connector approval.

## Modules

_Populate after deferred discovery + inventory. Expected employer spine to inspect: Account → Contact → Job Order → Placement._

## Related docs

- `DEFERRED-PLATFORM-DISCOVERY.md` — **start here for the later phase**
- `GEORGE-5-MINUTE-SETUP.md`
- `ZOHO-FIELD-MAPPING-WORKSHEET.md`
- `NATIVE-GOOGLE-ADS-AUDIT.md`
- `PRODUCTION-LEAST-PRIVILEGE.md`
