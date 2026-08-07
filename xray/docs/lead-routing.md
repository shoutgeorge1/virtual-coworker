# Lead routing — Stage 1

Distinguish **confirmed** · **recommendation** · **unresolved**.

Status as of **Aug 7, 2026**: USA Search live; microsite Resend + GitHub delivery active; AU paused on phone; conversion tracking + US phone routing are the hot ops items.

## Conversion strategy (confirmed)

- **Stage 1 primary:** employer form submissions after **durable delivery** (Resend and/or GitHub Issues) — not a bare click
- **Stage 1 secondary:** click-to-call observation; qualified phone (~60s / CallRail) later
- **Calendly (confirmed, secondary only):**
  - US: https://calendly.com/cheyenne-virtualcoworker/30min
  - APAC: https://calendly.com/apac-virtualcoworker/30min
  - Not a second Primary for the same enquiry
- **Do not initially optimize Ads** around job orders / placements — need clean lead data first
- **Do not triple-count** form + Calendly + Zoho offline as Primary for one enquiry
- **Future offline ranges (estimates only — not approved for Ads import):**
  - Job order: ~$200–$400
  - Job placement: ~$500–$800
- **Later:** Zoho → Google Ads offline conversions so campaigns learn which leads produce business
- **Stay Maximize Clicks** until new campaign-specific goals on `VC_US_*` are clean

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
| US | **Hot ops** | Destination `310-730-9126` — rings ~5–6 → Google Voice voicemail. Ash (intern) got a test VM; not durable. **Cheyenne owns US sales.** Raffie = phone systems/IT, **not** US salesperson. Real task: route into Cheyenne/US sales workflow, name missed-call owner, E2E test. |
| AU | **Paused gate** | No confirmed/tested AU phone for paid. Form-first; AU ads paused until phone confirmed/tested. |
| CallRail | **Later** | ~1–2 months. Tracking numbers forward to sales destinations. Not Stage 1 operational. |

## Form and CRM routing

- **WordPress + Gravity Forms** = existing site process only. Still emails `us@` / `apac@`. Paid microsite pages must **not** depend on WP/GF.
- **Microsite (ACTIVE Aug 2026):** form → `/api/lead` → **Resend** → `us@virtualcoworker.com` / `apac@virtualcoworker.com` (+ George CC via `LEAD_EMAIL_CC` only) **and** GitHub Issues (`shoutgeorge1/vc-employer-leads`) as durable backup / interim monitor (not permanent CRM). Verified: Caitlin test Issues #5; probe #6; Resend sent to `us@`. Form can succeed if either durable path works.
- **Do not say Resend is “still next.”** It is live.
- **Sales inboxes mix** paid microsite + WP + organic — Monday report **must** distinguish paid microsite/Ads from total inbound.
- **Attribution captured:** `utm_*`, `gclid`, `gbraid`, `wbraid`, landing URL, referrer, market, category, variant. Verify sales-facing email/CRM exposes enough to ID paid microsite leads.
- **Preferred (when Zoho path locked):** new LP form → secure server-side → direct Zoho + success/fail + backup. No browser credentials.
- **Zoho:** George can sign in. Mapping / admin / direct write / offline / Job Order later. **Not a traffic-readiness blocker.** Don’t rebuild Zoho as the week’s center.

## Sales ownership (confirmed vs open)

**Confirmed**

- Cheyenne Gichana owns US sales
- Holly Wallace owns APAC
- `us@` / `apac@` group inboxes; Caitlin says they distribute to teams
- Monday buckets: enquiries · sales calls booked · junk · work-seekers
- No new tracker this week — Zoho + Monday email enough

**Unresolved (waiting Holly / Cheyenne)**

- Day-to-day counting source
- Whether they monitor microsite messages in the group inboxes
- How they separate paid vs total inbound in practice

## Default Stage 1 path

1. Form submission is stored safely (server route)
2. Lead is emailed via Resend immediately to the market inbox (+ optional George CC)
3. GitHub Issues receives a durable backup copy
4. Attribution fields are included (UTMs, GCLID/GBRAID/WBRAID, market, URL, referrer, timestamp)
5. User sees a confirmed thank-you state
6. Failed delivery is logged (no silent drops) — success if either durable path works
7. Zoho integration added later without rebuilding the form

## Recommended qualification fields (needs VC approval)

Not required until stakeholders approve:

- Company name · work email · phone · company size · role/service needed · hiring timeline · country/market · short need message
- Always capture (tech): GCLID / GBRAID / WBRAID · UTMs · LP URL · referrer · timestamp

## Target services (confirmed)

**Prioritize PH remote staffing:** Digital marketing · Social media · Accounting · Bookkeeping · Administration · Customer service · HR · Recruitment · Sales

**Exclude:** Medical staffing · Technology staffing · Spanish-language campaigns/claims

## People (confirmed roles)

| Person | Role |
|--------|------|
| Caitlin | Ops contact + lead-quality stakeholder; may start maternity leave anytime; LP copy already live |
| Braden | Expected takeover while Caitlin is out |
| Raffie/Raffy | PH — phone systems / IT / Zoho help (**not** US salesperson) |
| Cheyenne Gichana | US sales owner |
| Holly Wallace | APAC sales owner |
| Ash | Intern — test VM only; not permanent call owner |
| Pauly | Lead-quality |
| Essa | AI and internship initiatives |
| Dev team | Separate — contact + hours still needed |

## Communication reality

Overseas team · email delayed by TZ · prefers chat · George on personal email · check chat invites/approvals regularly.

**Checklist:** identify official chat platform · invite George · confirm notification settings.

## Weekly quality loop

- Monday buckets: enquiries · sales calls booked · junk · work-seekers
- Monday **must** separate paid microsite/Ads from total inbound
- Named sales owners: Cheyenne (US) · Holly (APAC)
- Waiting Holly/Chey on counting source + inbox monitoring
- George uses feedback to cut waste keywords and refine ads

## Configuration

Set values via environment variables (see `.env.example`). Never commit secrets.

| Variable | Purpose |
|----------|---------|
| `LEAD_EMAIL_US` | Destination for US leads (Resend — **active**) |
| `LEAD_EMAIL_AU` | Destination for AU leads (Resend — **active**) |
| `LEAD_EMAIL_CC` | Optional CC (George only unless explicitly expanded) |
| `LEAD_FROM_EMAIL` | From address for notifications |
| `LEAD_WEBHOOK_URL` | Durable webhook (pilot: `/api/lead-sink` → GitHub Issues) |
| `LEAD_WEBHOOK_AUTH` | Optional Bearer for webhook POSTs |
| `LEAD_SINK_SECRET` / `GITHUB_LEADS_TOKEN` | Pilot GitHub Issues sink |
| `ZOHO_WEBHOOK_URL` | Optional later Zoho endpoint — only after access confirmed |
| `LEAD_SHEET_WEBHOOK_URL` | Optional spreadsheet / Zapier / Make |
| `NEXT_PUBLIC_US_PHONE` | NA dest: `310-730-9126` (routing still open) |
| `NEXT_PUBLIC_AU_PHONE` | Official AU-site number — unresolved / AU ads paused |

If delivery is not configured, the API returns a clear error and the UI shows a graceful failure — it does not pretend the lead was sent.

## Unresolved (VC confirmation required)

- Holly / Cheyenne: counting source + whether group inboxes are monitored for microsite
- US phone → Cheyenne/US sales workflow + missed-call owner + E2E
- AU phone confirmed/tested (blocks AU Enable)
- Zoho modules / field mappings / ownership (later — not traffic gate)
- Exact defs of qualified lead / job order / placement
- How lead-quality feedback returns (Caitlin / Cheyenne / Pauly)
- CallRail approval/ownership · final offline conversion values before Ads import
- Official chat platform + George invite
