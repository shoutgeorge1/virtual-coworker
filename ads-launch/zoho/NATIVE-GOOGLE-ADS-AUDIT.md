# Native Zoho ↔ Google Ads audit (verification checklist only)

**MCC:** `119-318-9031` (Shout George)  
**Children:** USA `496-715-1855` · AU `573-539-1940`

This file is a **verification checklist**. Do **not** authorize the Zoho Google Ads connector from this workstream. Do **not** change auto-tagging. Do **not** run a custom offline conversion uploader while the native path / token decision is pending.

## Conversion honesty lock (Stage 1)

| Rule | Status |
|------|--------|
| **One inquiry ≠ two Primary conversions** | LOCKED |
| GTM `employer_inquiry_submitted` stays **Stage 1 Primary** once verified | LOCKED |
| Zoho lead-created / CRM milestones = **Secondary / downstream only** | LOCKED |
| No custom offline uploader while token / Data Manager path pending | LOCKED |
| Native Zoho export + custom upload for the **same** milestone = forbidden until dedupe proven | LOCKED |

## Account wiring checklist

| Check | US 496-715-1855 | AU 573-539-1940 | Notes |
|-------|-----------------|-----------------|-------|
| Zoho CRM Google Ads integration visible | ☐ | ☐ | CRM Admin only |
| Connected Google Ads customer IDs match children above | ☐ | ☐ | Via MCC 119-318-9031 |
| Google Ads tab present on Leads/Contacts/Deals | ☐ | ☐ | |
| Auto-tagging / GCLID capture status (observe only) | ☐ | ☐ | **Do not change** |
| Google Ads Information section on records | ☐ | ☐ | |
| `Google Ads Conversion Export` view exists | ☐ | ☐ | |
| Conversion import failures reviewed | ☐ | ☐ | |
| CRM milestones currently exported to Ads listed | ☐ | ☐ | None should be Primary for Stage 1 inquiry |
| Ownership / permissions documented | ☐ | ☐ | One seat ≠ CRM Admin ≠ Ads connector admin |
| Compatible with Next.js server-side form path? | ☐ | ☐ | Direct CRM adapter is separate from native click capture |
| Compatible with Google 2026 Data Manager migration? | ☐ | ☐ | Document; do not build legacy upload |

## Who can do what (do not conflate)

| Role | Can |
|------|-----|
| Zoho One seat | Log in to assigned apps |
| CRM app on seat | Use CRM UI if profile allows |
| CRM profile/role | API modules/fields per permission |
| Self Client (API Console) | OAuth for server adapter (READ bootstrap / later write scopes) |
| CRM Admin (native Ads) | Authorize Google Ads connector / auto-tagging settings |

Self Client OAuth **≠** approving the native Ads connector.

## References

- https://help.zoho.com/portal/en/kb/crm/integrations/google/google-ads/articles/google-ads-crm-integration
- https://help.zoho.com/portal/en/kb/crm/integrations/google/google-ads/articles/track-google-ads-data

## Outcome for Stage 1 paid search

**Sequencing lock:** native Zoho↔Ads connector, offline uploads, and Ads API are **OPTIMIZATION READY / CRM READY** work — **not** prerequisites for initial Maximize Clicks **TRAFFIC READY** Enable.

When optimization is wired: Primary conversion remains the **online** durable `employer_inquiry_submitted` path (GTM). Zoho record creation is not a second Primary. Offline qualified / job-order / placement stay blocked until milestones + IDs are approved.
