# Zoho field mapping worksheet (stub)

Fill **only after** `npm run zoho:inventory` with verified API names from CRM metadata. Do not invent API names from UI labels.

Target module (verify): `_______________` (likely `Leads`)

| Display label | API name (verified) | Module | Type | Required / unique / external | Current usage | Proposed VC mapping | Verified? |
|---------------|---------------------|--------|------|------------------------------|---------------|---------------------|-----------|
| First Name | `First_Name` | Leads | text | | | lead.firstName | ☐ assumed standard / ☐ verified |
| Last Name | `Last_Name` | Leads | text | | | lead.lastName | ☐ |
| Email | `Email` | Leads | email | | | lead.email | ☐ |
| Phone | `Phone` | Leads | phone | | | lead.phone | ☐ |
| Company | `Company` | Leads | text | | | lead.company | ☐ |
| Description / notes | | | | | | lead.message + role/timeline | ☐ |
| VC Submission ID | `VC_Submission_ID` | | text | prefer unique/external | | lead.submission_id (idempotency) | ☐ missing → propose |
| GCLID | `$gclid` or custom | | | | | lead.gclid | ☐ |
| GBRAID | | | | | | lead.gbraid | ☐ |
| WBRAID | | | | | | lead.wbraid | ☐ |
| UTM Source | | | | | | lead.utm_source | ☐ |
| UTM Medium | | | | | | lead.utm_medium | ☐ |
| UTM Campaign | | | | | | lead.utm_campaign | ☐ |
| UTM Term | | | | | | lead.utm_term | ☐ |
| UTM Content | | | | | | lead.utm_content | ☐ |
| Market | | | | | | lead.market | ☐ |
| Category | | | | | | lead.category | ☐ |
| Variant | | | | | | lead.variant | ☐ |
| LP version | | | | | | lead.lp_version | ☐ |
| Landing page URL | | | | | | lead.landing_page_url | ☐ |
| Referrer | | | | | | lead.referrer | ☐ |

## Rules

- Map only when the field **exists** in inventory (or is a Zoho system key like `$gclid`).
- Missing fields → list in “field-creation proposal”; **`--apply-schema` requires George approval** (no auto-create).
- `is_job_order` / `is_placement` stay false on initial create; do not invent CRM stages.
- Adapter reads verified names via `ZOHO_CRM_FIELD_*` env overrides or baked config after verification.
