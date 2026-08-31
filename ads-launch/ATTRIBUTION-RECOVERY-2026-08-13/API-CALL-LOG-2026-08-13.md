# API call log — 13 August 2026 final evidence pass

Read-only. No mutations, uploads, or retries after schema/parse failures. Stop rule on Ads `RESOURCE_EXHAUSTED` was not hit.

Ceilings: **≤12 Google Ads queries**, **≤20 Zoho CRM requests**.

Token refresh (Zoho accounts OAuth, Ads client build) is not counted as a CRM/Ads query.

---

## Totals

| System | Used | Ceiling | Hard stop |
|--------|-----:|--------:|-----------|
| Google Ads GAQL | **12** | 12 | None |
| Zoho CRM | **12** | 20 | None (one 401 on settings; not retried) |

Pass 1 spent **9** Ads queries then crashed while parsing `change_event.changed_fields` (FieldMask). Results were **not written**. Those 9 still count. Pass 2 used the remaining **3** and did not replay monthly metrics or conversion-action refresh.

---

## Google Ads (customer US `4967151855`, AU `5735391940`; MCC not queried)

| n | Name | Account | OK | Rows / error | Counted? |
|---|------|---------|----|--------------|----------|
| 1 | `us_goal_config_vc` | US | yes (unwritten) | pass1 crash after later parse | Yes |
| 2 | `us_campaign_conversion_goal_vc` | US | yes (unwritten) | pass1 | Yes |
| 3 | `us_conversion_actions` | US | yes (unwritten) | pass1 | Yes |
| 4 | `us_monthly_conversion_actions` | US | yes (unwritten) | pass1; **not replayed** | Yes |
| 5 | `au_goal_config_vc` | AU | yes (unwritten) | pass1 | Yes |
| 6 | `au_campaign_conversion_goal_vc` | AU | yes (unwritten) | pass1; AU map **UNKNOWN** in files | Yes |
| 7 | `au_conversion_actions` | AU | yes (unwritten) | pass1 | Yes |
| 8 | `au_monthly_conversion_actions` | AU | yes (unwritten) | pass1; **not replayed** | Yes |
| 9 | `us_change_event_14d` | US | yes then parse fail | FieldMask not iterable; **not retried** | Yes |
| 10 | `us_goal_config_vc_pass2` | US | yes | 2 | Yes |
| 11 | `au_goal_config_vc_pass2` | AU | yes | 2 | Yes |
| 12 | `us_campaign_conversion_goal_vc_pass2` | US | yes | 28 | Yes |

Not run (ceiling): AU `campaign_conversion_goal` rewrite, AU `change_event`, `custom_conversion_goal`, conversion-action afternoon refresh, `click_view`, offline-upload summaries.

Morning forensic pull (`xray/data/recovery-ads-raw.json`, 16:03 UTC, 9 calls earlier today) is a **separate** prior pass. This log is the final-evidence ceiling only.

---

## Zoho CRM V8 (COQL + GET)

Join script (8):

| n | Name | HTTP | OK | Notes |
|---|------|-----:|----|-------|
| 1 | `jo_gclid_all` | 200 | yes | Job Orders with `UTM_Gclid` |
| 2 | `leads_for_gclid_jos` | 200 | yes | Linked Sales Enquiries for those 18 |
| 3 | `jo_90d_lookup_gclid` | 200 | yes | Newest 200 of 90d Job Orders |
| 4 | `leads_utm_gclid_chunk_1` | 200 | yes | Enquiry GCLID hashes |
| 5 | `leads_utm_gclid_chunk_2` | 200 | yes | |
| 6 | `leads_utm_gclid_chunk_3` | 200 | yes | |
| 7 | `leads_utm_gclid_chunk_4` | 200 | yes | |
| 8 | `related_lists_job_orders` | 401 | no | Settings API; **not retried** |

Related-name probes after the 401 (4; different endpoints, not a retry of settings):

| n | Name | HTTP | Result |
|---|------|-----:|--------|
| 9 | `Job_Orders/{id}/Deals` | 400 | invalid relation name |
| 10 | `Job_Orders/{id}/Placements` | 400 | invalid relation name |
| 11 | `Job_Orders/{id}/Contacts` | 400 | invalid relation name |
| 12 | `Job_Orders/{id}/Accounts` | 400 | invalid relation name |

No bulk export of 782/3,433. No emails, phones, raw GCLIDs, or full record IDs in shipped markdown/CSV. Hashed summaries: `.local/attribution-final-evidence-2026-08-13.json` (gitignored).

---

## Not called

GA4 historical reconstruction · Zapier · GTM Admin API · Ads mutate · Zoho write · conversion upload.
