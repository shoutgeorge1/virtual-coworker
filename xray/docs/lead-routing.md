# Lead routing — Stage 1

Distinguish **confirmed** · **recommendation** · **unresolved**.

## Conversion strategy (confirmed)

- **Stage 1 primary:** employer form submissions (server-accepted) + qualified phone calls
- **Do not initially optimize Ads** around job orders / placements — need clean lead data first
- **Future offline ranges (estimates only — not approved for Ads import):**
  - Job order: ~$200–$400
  - Job placement: ~$500–$800
- **Later:** Zoho → Google Ads offline conversions so campaigns learn which leads produce business

## Previous lead-quality problems (confirmed context)

Prior agency traffic produced poor leads (percentages may overlap — not mutually exclusive):

- Unsuitable / new businesses with no relevant staffing need
- ~20% job seekers (including PH applicants)
- ~10–15% spam

**Diagnosis:** optimizing easy form submits vs downstream outcomes.

**Stage 1 needs:** employer-only messaging · strong job-seeker exclusions · spam protection · business qualification fields (recommended — stakeholder approval) · search-term monitoring · sales lead-quality feedback · capture GCLID / GBRAID / WBRAID / UTMs / LP / timestamp.

## Phone routing

| Market | Status | Detail |
|--------|--------|--------|
| NA | **Confirmed** | Destination `310-426-8776` — Raffie/Raffy (PH) manages/answers. Do not replace or port. |
| AU | **Unresolved** | No new paid-media number confirmed. Use only the official approved number already on the AU website. |
| CallRail | **Later** | Tracking numbers forward to existing destinations; AU local tracking eventually. Not fake-operational. Approval/ownership open. |

## Form and CRM routing

- **WordPress + Gravity Forms** = existing site process only. Paid microsite pages must **not** depend on WP/GF.
- **Preferred (when Zoho access confirmed):** new LP form → secure server-side → direct Zoho CRM + success/fail + backup notify/webhook if Zoho down. No browser credentials.
- **Do not build final Zoho** until access, modules, fields, mappings, ownership, and API are confirmed.
- **Stage 1 launch fallback:** email and/or webhook is acceptable.

## Default Stage 1 path

1. Form submission is stored safely (server route)
2. Lead is emailed / webhooked immediately to the designated recipient
3. Attribution fields are included (UTMs, GCLID/GBRAID/WBRAID, market, URL, timestamp)
4. Optional backup copy to a spreadsheet or database
5. User sees a confirmed thank-you state
6. Failed delivery is logged (no silent drops)
7. Zoho integration added later without rebuilding the form

## Recommended qualification fields (needs VC approval)

Not required until stakeholders approve:

- Company name · work email · phone · company size · role/service needed · hiring timeline · country/market · short need message
- Always capture (tech): GCLID / GBRAID / WBRAID · UTMs · LP URL · timestamp

## Target services (confirmed)

**Prioritize PH remote staffing:** Digital marketing · Social media · Accounting · Bookkeeping · Administration · Customer service · HR · Recruitment · Sales

**Exclude:** Medical staffing · Technology staffing · Spanish-language campaigns/claims

## People (confirmed roles — no guessed surnames/emails)

| Person | Role |
|--------|------|
| Caitlin | Ops contact + lead-quality stakeholder; may start maternity leave anytime |
| Braden | Expected takeover while Caitlin is out |
| Raffie/Raffy | PH contact — Zoho + NA phone |
| Cheyenne | Lead-quality (Los Angeles) |
| Pauly | Lead-quality |
| Essa | AI and internship initiatives |
| Dev team | Separate — contact + hours still needed |

## Communication reality

Overseas team · email delayed by TZ · prefers chat · George on personal email · check chat invites/approvals regularly.

**Checklist:** identify official chat platform · invite George · confirm notification settings.

## Weekly quality loop

- VC defines “qualified” / job order / placement (exact defs still open)
- Named responders own first response (owner + SLA still open)
- Caitlin / Cheyenne / Pauly return good / bad / why (path still open)
- George uses that to cut waste keywords and refine ads

## Configuration

Set values via environment variables (see `.env.example`). Never commit secrets.

| Variable | Purpose |
|----------|---------|
| `LEAD_EMAIL_US` | Destination for US leads |
| `LEAD_EMAIL_AU` | Destination for AU leads |
| `LEAD_FROM_EMAIL` | From address for notifications |
| `LEAD_WEBHOOK_URL` | Optional webhook |
| `ZOHO_WEBHOOK_URL` | Optional later Zoho endpoint — only after access confirmed |
| `LEAD_SHEET_WEBHOOK_URL` | Optional spreadsheet / Zapier / Make |
| `NEXT_PUBLIC_US_PHONE` | NA dest confirmed: `310-426-8776` |
| `NEXT_PUBLIC_AU_PHONE` | Official AU-site number — unresolved |

If delivery is not configured, the API returns a clear error and the UI shows a graceful failure — it does not pretend the lead was sent.

## Unresolved (VC confirmation required)

- Zoho access · modules / field mappings · who owns/routes employer leads · response-time expectations
- AU phone · dev team email/phone/chat/hours · approved qualification form fields
- Exact defs of qualified lead / job order / placement
- How Caitlin / Cheyenne / Pauly return lead-quality feedback
- CallRail approval/ownership · final offline conversion values before Ads import
- Official chat platform + George invite
