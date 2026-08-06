# Zoho — production least-privilege runbook (**deferred scopes**)

**Do not issue production tokens until** `DEFERRED-PLATFORM-DISCOVERY.md` identifies CRM vs Recruit (or customized CRM) and the entry module for employer inquiries.

## Bootstrap / inventory (after platform ID)

Document the READ-only scope string for the **chosen** API here. Current `npm run zoho:*` helpers assume CRM V8-style scopes — treat as **stubs** until discovery.

Historical CRM V8 READ bundle (may be wrong for this org):

```
ZohoCRM.org.READ,ZohoCRM.users.READ,ZohoCRM.settings.modules.READ,ZohoCRM.settings.fields.READ,ZohoCRM.modules.READ,ZohoCRM.bulk.READ,ZohoCRM.coql.READ
```

No `ALL`, `CREATE`, `UPDATE`, or `DELETE` on bootstrap tokens.

If Recruit API V2 is the product: replace the above with Recruit READ-only scopes from Zoho docs after confirmation — do not invent.

## Production upsert (later — George approval)

After entry module + field API names are verified:

1. Issue a **separate** refresh token with the narrowest write scopes for the **chosen module only** (do **not** default to `ZohoCRM.modules.leads.*` — Leads may not exist).
2. Store secrets server-only (names may change with product): client id/secret, refresh token, accounts URL, API domain.
3. Gate with explicit enable flag only when ready (`ZOHO_CRM_ENABLED` or successor).
4. Prefer an external id (e.g. `VC_Submission_ID`) for upsert idempotency on the chosen module.
5. **Do not** auto-create fields. Schema apply requires explicit George approval.

## Honesty

| Signal | Means |
|--------|--------|
| `ZOHO_WEBHOOK_URL` 200 | Generic webhook delivered (`webhook_zoho`) |
| Direct API upsert returns record id | `zoho_synced: true` (when wired) |
| Email / sheet / webhook ok | Durable lead possible; not Zoho sync |
| Launch Control TRAFFIC READY | Paid readiness — not the Zoho API response |

## Outbox blocker

Vercel process memory is not a durable Zoho retry outbox. If API upsert fails after email/webhook succeeded, `zoho_synced` stays false; a durable outbox/retry store is still required before claiming guaranteed sync.
