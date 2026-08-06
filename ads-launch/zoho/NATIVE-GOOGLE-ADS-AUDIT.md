# Native Zoho ↔ Google Ads audit (verification checklist only)

**MCC:** `119-318-9031` (Shout George)  
**Children:** USA `496-715-1855` · AU `573-539-1940`

This file is a **verification checklist**. Do **not** authorize the Zoho Google Ads connector from this workstream. Do **not** change auto-tagging. Do **not** run a custom offline conversion uploader while the native path / token decision is pending.

**Separate from** platform discovery (`DEFERRED-PLATFORM-DISCOVERY.md`) and from George’s pending **Google Ads developer token**. Native Zoho↔Ads wiring may exist (or not) independent of Ads API access — audit by observation only; do not assume the developer token is required to complete this checklist.

## Conversion honesty lock (Stage 1)

| Rule | Status |
|------|--------|
| **One inquiry ≠ two Primary conversions** | LOCKED |
| GTM `employer_inquiry_submitted` stays **Stage 1 Primary** once verified | LOCKED |
| Zoho record-created / CRM-or-Recruit milestones = **Secondary / downstream only** | LOCKED |
| No custom offline uploader while token / Data Manager path pending | LOCKED |
| Native Zoho export + custom upload for the **same** milestone = forbidden until dedupe proven | LOCKED |

## Account wiring checklist

| Check | US 496-715-1855 | AU 573-539-1940 | Notes |
|-------|-----------------|-----------------|-------|
| Zoho Google Ads integration visible (CRM and/or Recruit) | ☐ | ☐ | Admin only; product TBD |
| Connected Google Ads customer IDs match children above | ☐ | ☐ | Via MCC 119-318-9031 |
| Google Ads tab present on relevant modules (not assumed Leads) | ☐ | ☐ | Contacts / Job Orders / etc. per org |
| Auto-tagging / GCLID capture status (observe only) | ☐ | ☐ | **Do not change** |
| Google Ads Information section on records | ☐ | ☐ | |
| Conversion export view / failures reviewed | ☐ | ☐ | |
| Milestones currently exported to Ads listed | ☐ | ☐ | None should be Primary for Stage 1 inquiry |
| Ownership / permissions documented | ☐ | ☐ | One seat ≠ app Admin ≠ Ads connector admin |
| Compatible with Next.js server-side form path? | ☐ | ☐ | Direct API adapter is separate from native click capture |
| Compatible with Google 2026 Data Manager migration? | ☐ | ☐ | Document; do not build legacy upload |
| Needs George’s Ads developer token? | ☐ | ☐ | **Do not assume yes** — document actual dependency |

## Who can do what (do not conflate)

| Role | Can |
|------|-----|
| Zoho One seat | Log in to assigned apps |
| CRM / Recruit app on seat | Use UI if profile allows |
| App profile/role | API modules/fields per permission |
| Self Client (API Console) | OAuth for server adapter (after platform ID) |
| App Admin (native Ads) | Authorize Google Ads connector / auto-tagging settings |
| Google Ads developer token | Ads API — **separate** from native Zoho connector |

Self Client OAuth **≠** approving the native Ads connector **≠** Ads developer token.

## References

- https://help.zoho.com/portal/en/kb/crm/integrations/google/google-ads/articles/google-ads-crm-integration
- https://help.zoho.com/portal/en/kb/crm/integrations/google/google-ads/articles/track-google-ads-data
- (Recruit-specific Ads docs — confirm after product ID)

## Outcome for Stage 1 paid search

**Sequencing lock:** native Zoho↔Ads connector, offline uploads, Ads API, and platform discovery are **OPTIMIZATION READY / CRM READY** work — **not** prerequisites for initial Maximize Clicks **TRAFFIC READY** Enable.

When optimization is wired: Primary conversion remains the **online** durable `employer_inquiry_submitted` path (GTM). Zoho record creation is not a second Primary. Offline qualified / job-order / placement stay blocked until milestones + IDs are approved.
