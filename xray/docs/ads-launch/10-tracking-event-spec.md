# 10 — Tracking / event spec (v7)

**LP version:** `stage1-v7`  
**Containers:** `NEXT_PUBLIC_GTM_US` / `_AU` / `_PH` (+ GA4 twins); legacy `NEXT_PUBLIC_GTM_ID` = US fallback  
**No hard-coded Google Ads `send_to` in app code** — map in GTM when ready  
**Ads conversion firing:** `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false` until tested  
**CallRail:** later-ready (phone click ≠ qualified call)

---

## Attribution fields (session + submit)

| Field | Source |
|-------|--------|
| utm_source / medium / campaign / term / content | query → session |
| gclid / gbraid / wbraid | query → session |
| landing_page_url | location |
| referrer | document.referrer |
| market / site_surface | route (`us` \| `au` \| `ph`) |
| category | route slug (empty on generic Core) |
| variant | a\|b cookie / QA override |
| lp_version | `stage1-v7` |
| captured_at / submitted_at | timestamps |

---

## Events

| Event | When | Primary for Ads? | Notes |
|-------|------|------------------|-------|
| `employer_gate_selected` | User chooses employer | No | Gate pass |
| `employer_form_started` | First form interaction after employer | No | Funnel |
| `employer_form_validation_error` | Client validation fail | No | Field names only |
| `employer_inquiry_submitted` | Server accept **+ durable delivery** (`submission_id`) | **Candidate** | **Not** job order / placement; **not** log-only |
| `employer_inquiry_submitted_deduped` | Repeat fire blocked | No | Refresh-safe |
| `employer_inquiry_delivery_failed` | 502/503 / network | No | Fail honestly |
| `employer_inquiry_log_only` | Log-only blocked mode accept | **Never** | QA diagnostic |
| `phone_cta_clicked` | tel: click | Secondary only | **`is_qualified_call: false`** |
| `calendly_cta_clicked` | thank-you book CTA | Secondary / later candidate | Hiring conversation booking — **never** replace primary `employer_inquiry_submitted`. Booked-call event = OPTIMIZATION READY / later when GTM fires. Not TRAFFIC READY. |
| `conversion_assist_opened` | Exit-intent / timed assist shown | No | Flag-gated |
| `conversion_assist_cta_clicked` | Assist CTA → `#gate` | No | |
| `job_seeker_redirected` | Job seeker clicks through to `/ph` | **Never** | Interaction only |
| `spam_or_applicant_rejected` | Validation reject | No | |

Legacy: `job_seeker_diverted` retired → `job_seeker_redirected`.  
Legacy assist aliases `exit_intent_shown` / `exit_intent_accepted` still fire alongside conversion_assist_*.

---

## Lead delivery honesty

| Condition | API result |
|-----------|------------|
| No channel + no log-only flag | **503** `delivery_not_configured`, `conversion_eligible: false` |
| No channel + `ALLOW_LOG_ONLY_LEADS=true` | **200** log-only blocked mode — `conversion_eligible: false`, `paid_ready: false` |
| Zoho URL missing | Not an error by itself; `zoho_synced: false` |
| Zoho URL set and POST ok | `zoho_synced: true` |
| All configured channels fail | **502** `delivery_failed`, `conversion_eligible: false` |
| ≥1 channel ok | **200** `delivery: durable`, `conversion_eligible: true` |

Never return fake Zoho success. Log-only ≠ paid conversion.

---

## Conversion definitions (business) — Aug 6 lock

```
Ad click
  → phone call 60–90s     (VC_US_Phone_Call_From_Ads / _From_Website)
                          first meaningful Primary AFTER routing works
  → form submit           (VC_US_Employer_Form_Submit) Secondary / observation
                          dataLayer: employer_inquiry_submitted + form_submit_success
  → Zoho Qualified        offline quality signal (later; needs GCLID)
  → job order / placement (CRM — not wired)

phone_cta_clicked / phone_click ≠ qualified call (Secondary micro only)
form submit ≠ bidding Primary ≠ job order ≠ placement
log_only accept ≠ employer_inquiry_submitted
Stay Maximize Clicks — no Max Conv yet
```

Aliases for GTM maps: `form_submit_success`, `phone_click`, `calendly_click`.  
See `CONVERSION-PLAN.md`.
