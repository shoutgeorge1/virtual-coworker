# Zoho CRM — production least-privilege runbook

## Bootstrap / inventory (current)

Scopes (READ only — verified V8 style):

```
ZohoCRM.org.READ,ZohoCRM.users.READ,ZohoCRM.settings.modules.READ,ZohoCRM.settings.fields.READ,ZohoCRM.modules.READ,ZohoCRM.bulk.READ,ZohoCRM.coql.READ
```

No `ALL`, `CREATE`, `UPDATE`, or `DELETE` on bootstrap tokens.

## Production lead upsert (later — George approval)

After module + field API names are verified:

1. Issue a **separate** refresh token (or Self Client grant) with the narrowest write scopes for the chosen module only, e.g.:
   - `ZohoCRM.modules.leads.CREATE`
   - `ZohoCRM.modules.leads.UPDATE`
   - Keep `ZohoCRM.settings.fields.READ` only if runtime must re-check schema (prefer bake verified names into config).
2. Store secrets server-only: `ZOHO_CRM_CLIENT_ID`, `ZOHO_CRM_CLIENT_SECRET`, `ZOHO_CRM_REFRESH_TOKEN`, `ZOHO_CRM_ACCOUNTS_URL`, `ZOHO_CRM_API_DOMAIN`.
3. Gate with `ZOHO_CRM_ENABLED=true` only when ready.
4. Prefer external id field `VC_Submission_ID` for upsert idempotency.
5. **Do not** auto-create fields. Documented `--apply-schema` would require explicit George approval (not implemented as a silent default).

## Honesty

| Signal | Means |
|--------|--------|
| `ZOHO_WEBHOOK_URL` 200 | Generic webhook delivered (`webhook_zoho`) |
| CRM upsert returns record id | `zoho_synced: true` |
| Email / sheet / webhook ok | Durable lead possible; not CRM sync |
| Launch Control gates green | Paid readiness — not the lead API response |

## Outbox blocker

Vercel process memory is not a durable Zoho retry outbox. If CRM upsert fails after email/webhook succeeded, `zoho_synced` stays false; a durable outbox/retry store is still required before claiming guaranteed CRM sync.
