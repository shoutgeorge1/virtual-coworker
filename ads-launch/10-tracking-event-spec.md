# 10 — Tracking / event spec

**LP version:** `stage1-v5`  
**Container:** `NEXT_PUBLIC_GTM_ID` optional — events still push to `dataLayer`  
**No hard-coded Google Ads `send_to` in app code** — map in GTM when ready  
**CallRail:** later-ready (phone click ≠ qualified call)

---

## Attribution fields (session + submit)

| Field | Source |
|-------|--------|
| utm_source / medium / campaign / term / content | query → session |
| gclid / gbraid / wbraid | query → session |
| landing_page_url | location |
| referrer | document.referrer |
| market | route |
| category | route slug (empty on generic) |
| variant | a\|b cookie / QA override |
| lp_version | `stage1-v5` |
| captured_at / submitted_at | timestamps |

---

## Events

| Event | When | Primary for Ads? | Notes |
|-------|------|------------------|-------|
| `employer_gate_selected` | User chooses employer | No | Gate pass |
| `employer_form_started` | First form interaction after employer | No | Funnel |
| `employer_inquiry_submitted` | Server accepted employer lead (`submission_id`) | **Candidate** | **Not** job order / placement |
| `employer_inquiry_submitted_deduped` | Repeat fire blocked | No | Refresh-safe |
| `phone_cta_clicked` | tel: click | Secondary only | **`is_qualified_call: false`** |
| `job_seeker_diverted` | Job seeker gate | **Never** primary | No Zoho sales lead |
| `spam_or_applicant_rejected` | Validation reject | No | |

Legacy names (`employer_form_valid_submit`, `phone_click`, `employer_gate_pass`) **retired**.

---

## Lead delivery honesty

| Condition | API result |
|-----------|------------|
| No email/webhook/sheet/zoho configured | **503** `delivery_not_configured` (unless `ALLOW_LOG_ONLY_LEADS=true`) |
| Zoho URL missing | Not an error by itself; `zoho_synced: false` |
| Zoho URL set and POST ok | `zoho_synced: true` |
| All configured channels fail | **502** |

Never return fake Zoho success.

---

## Conversion definitions (business)

```
Ad click
  → employer_inquiry_submitted   (qualified inquiry attempt)
  → human follow-up
  → job order                    (CRM — not wired)
  → placement                    (ops — not wired)

phone_cta_clicked ≠ qualified call
form submit ≠ job order ≠ placement
```
