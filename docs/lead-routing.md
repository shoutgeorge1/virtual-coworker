# Lead routing — Phase 1

Zoho **API / write access** is on the “what we need” list so George can push paid leads in.
Email delivery still works as a backup. Full CRM admin / rebuild is not required.

## Default pilot path (Aug 2026)

**Live now (microsite):** form → (1) durable webhook → private GitHub Issues  
`shoutgeorge1/vc-employer-leads` **and** (2) Resend email → `us@` / `apac@`  
(+ optional `LEAD_EMAIL_CC`, currently George).

**WordPress still:** Gravity Forms → `us@` / `apac@` (unchanged).

**Later:** Zoho CRM API (sales ops parallel — not required for Monday ads review).

1. Form submission is stored safely (server route)
2. Lead is delivered to a durable channel (GitHub Issues pilot; email when Resend is wired)
3. Attribution fields are included (UTMs, GCLID, market, URL, timestamp)
4. Optional backup copy to a spreadsheet or database
5. User sees a confirmed thank-you state
6. Failed delivery is logged (no silent drops)
7. Zoho integration can be added later without rebuilding the form

## Lead fields

| Group | Fields |
|-------|--------|
| Identity | first name, last name, work email, phone, company |
| Context | country, employees / company size, requested role / service, hiring timeline, message |
| Market | landing-page market, landing-page URL, referrer |
| Attribution | utm_source, utm_medium, utm_campaign, utm_term, utm_content, gclid, submission timestamp |

## Configuration

Set values via environment variables (see `.env.example`). Never commit secrets.

| Variable | Purpose |
|----------|---------|
| `LEAD_EMAIL_US` | Destination for US leads |
| `LEAD_EMAIL_AU` | Destination for AU leads |
| `LEAD_FROM_EMAIL` | From address for notifications (must be on a Resend-verified domain) |
| `LEAD_EMAIL_CC` | Optional CC list (comma/space separated) |
| `RESEND_API_KEY` | Resend API key for lead notification email |
| `LEAD_WEBHOOK_URL` | Durable webhook (pilot: `/api/lead-sink`) |
| `LEAD_WEBHOOK_AUTH` | Optional Bearer for webhook/sheet POSTs |
| `LEAD_SINK_SECRET` / `GITHUB_LEADS_TOKEN` | Pilot GitHub Issues sink |
| `ZOHO_WEBHOOK_URL` | Optional later Zoho endpoint |
| `LEAD_SHEET_WEBHOOK_URL` | Optional spreadsheet / Zapier / Make |

If delivery is not configured, the API returns a clear error and the UI shows a graceful failure — it does not pretend the lead was sent.

## Weekly quality loop

- VC defines “qualified”
- Named responders own first response
- Weekly note: good / bad / why
- George uses that to cut waste keywords and refine ads
