# 08 — Zoho field + lifecycle contract

**No credentials. No API writes in this phase.** This is the data contract for when VC grants access.

---

## Principle

Paid Search may create **employer sales leads** only.  
Job seekers, gate-abandons, and spam go elsewhere (or nowhere) — **never** Zoho Sales Lead with Google Ads conversion credit.

---

## Objects

| Object | When created | Owner system |
|--------|--------------|--------------|
| Lead (Sales) | Employer form success **or** qualified call | Paid LP backend → Zoho (or email interim) |
| Contact / Account | On sales accept | Zoho / VC sales |
| Deal / Opportunity | When job order intent confirmed | Zoho |
| Job seeker record | Optional separate module / sheet | **Not** Sales Lead |
| Spam quarantine | Server flag | Backend logs / sheet |

---

## Field contract — Lead create (employer)

| Field | Required | Example / notes |
|-------|----------|-----------------|
| `First_Name` | Y | |
| `Last_Name` | Y | |
| `Email` | Y | Work email preferred |
| `Phone` | Y | E.164 if possible |
| `Company` | Y | |
| `Lead_Source` | Y | `Google Ads` |
| `Lead_Source_Detail` | Y | `VC_US_S_CORE_hire_va` (campaign) |
| `Market` | Y | `US` / `AU` |
| `Country` | Y | |
| `Role_Requested` | Y | VA / Bookkeeping / EA / SMM / Other |
| `Company_Size` | Y | Band |
| `Hiring_Timeline` | Y | |
| `Description` / message | N | |
| `GCLID` | Y if present | Store raw for offline conv |
| `GBRAID` / `WBRAID` | N | If present |
| `UTM_Source` | Y | google |
| `UTM_Medium` | Y | cpc |
| `UTM_Campaign` | Y | |
| `UTM_Term` | N | |
| `UTM_Content` | N | |
| `Landing_URL` | Y | |
| `Gate_Variant` | Y | inline / quiz / modal |
| `Employer_Confirmed` | Y | true |
| `Form_Vendor` | Y | microsite / formspree / gf — whatever used |
| `Lead_ID_External` | Y | UUID from form backend |
| `Submitted_At` | Y | ISO-8601 UTC |
| `Quality_Status` | Y | `new` default |
| `Spam_Score` | N | |
| `CallRail_Call_ID` | N | If call-originated |

**Custom field names** can match Zoho conventions; map 1:1 in integration sheet before go-live.

---

## Lifecycle statuses (sales lead)

```
new
  → attempting_contact
  → qualified          ← offline conv: zoho_qualified_lead
  → disqualified       ← reason required; NOT a positive Ads conv
  → opportunity        ← offline: zoho_opportunity (+ value)
  → customer / placed  ← offline: zoho_customer / placement (+ value)
  → nurture
  → spam               ← never Ads primary
```

| Status | Ads offline conversion | Value |
|--------|------------------------|-------|
| `qualified` | Yes (Stage 4 prep / Stage 3+ secondary) | Fixed lead value TBD |
| `opportunity` | Yes Stage 4 | Opp $ or proxy |
| `customer` / placement | Yes Stage 4 | Highest |
| `disqualified` / `spam` | Adjustment / exclude | 0 |
| `jobseeker` (if misrouted) | Never create; if exists delete/convert out | 0 |

---

## Ownership

| Step | Owner |
|------|-------|
| Field map approval | Braden + George |
| Zoho API / webhook credentials | VC IT / Braden → George (secure store) |
| First-response SLA | Braden names human |
| Weekly quality CSV/notes | Braden → George |
| Offline conversion upload | George |
| Job-seeker CRM policy | Braden (PH recruiting team?) |

---

## Interim (before Zoho write access)

1. Email to `LEAD_EMAIL_US` / `LEAD_EMAIL_AU` with full field table  
2. Optional sheet backup  
3. Manual `Quality_Status` in sheet  
4. Same lifecycle labels so Zoho cutover is rename-not-rebuild  

---

## Explicit non-goals v1

- Full CRM rebuild  
- Marketing automation journeys  
- Dual-writing to WP Gravity Forms **and** Zoho for the same paid lead  
- Pushing job-seeker path into Sales pipeline “just to have a record”
