# Zoho + offline conversions — DEFERRED DURING COLD START

**Locked 2026-08-14.** Zoho is not cancelled. It is not an active Google Ads optimization project right now.

Campaigns are about one week into cold start. Immediate priority is generating and improving **verified employer conversion signal** through search terms, ads, landing pages, forms, bookings, and calls.

Dashboard: [Checklist · Zoho deferred](../../xray/launch-control.html#zoho-deferred-cold-start) · [Later Phases](../../xray/later.html#zoho-revisit-gate)

## Current Zoho position

- Keep Zoho API access **read-only**.
- Keep `.app` → Zoho production writes **OFF**.
- Do **not** build a new Zoho-to-Google Ads offline conversion integration.
- Do **not** add Zapier.
- Do **not** change existing Zoho records, workflows, fields, users, or permissions.
- Do **not** make any existing Zoho-related Google Ads conversion **Primary**.
- Do **not** alter bidding or campaign settings through the API.
- Continue **Maximize Clicks** during cold start.

## Reason

The API audit found that the previous offline-conversion setup cannot currently be validated cleanly:

- Google click IDs were not consistently preserved through the historical CRM records.
- Most enquiries were grouped under broad sources such as “Website.”
- Legacy “Zoho JO Submitted,” “Standard OCI,” and possible Zapier uploads may overlap or represent incomplete slices of CRM activity.
- Existing Job Order uploads and values do not reconcile cleanly enough with Zoho to use them as bidding signals.

The absence of `VC_*` and `.app` attribution on the new records is **expected** because the new forms have not been connected. Do **not** misrepresent that as a Zoho failure.

## What remains active

- Continue verified front-end Google Ads conversion tracking.
- Preserve GCLID, GBRAID/WBRAID, UTMs, campaign, landing page, and submission ID on `.app` enquiries wherever currently supported.
- Continue email delivery of employer leads.
- Continue dashboard read-only monitoring of Zoho for business context.
- Keep preliminary front-end conversion values **separate** from unverified CRM outcomes.

## Revisit only after

1. The new campaigns have enough qualified employer enquiries.
2. Virtual Coworker identifies the person responsible for Zoho.
3. Existing Zoho, Zapier, and Google Ads uploads are documented and reconciled.
4. One `.app` Sales Enquiry can be tested safely from beginning to end.
5. The CRM outcome definitions and values are consistent enough to validate.

## Communication record

George emailed **Braden** and **Amanda** with the subject **Stage 1 conversion strategy and Zoho next steps**.

The email explains that George supports offline conversions long term, but recommends slowing that work during cold start and validating the previous agency’s implementation before adding another feedback system.

## Related locks

- `ads-launch/DECISIONS.md` — operator defaults
- `ads-launch/zoho/` — CRM tooling stays parked; writes off
- Google Ads API remains read-only / Editor-only (`google-ads-api-editor-only.mdc`)
