# Pilot scope — $3,000 Google Search proof of concept

## Objective

Answer one question: **Can Google Search generate qualified US and Australian employer leads at an acceptable cost?**

## In scope (Phase 1)

- Google Search Ads for US and Australia employers
- Independently hosted Next.js microsite (Vercel)
- US and AU landing pages, form, thank-you, privacy
- UTM + GCLID capture
- Temporary GTM + GA4 (George-controlled)
- Email-first lead delivery with optional spreadsheet backup
- Weekly lead-quality feedback loop
- Basic Search optimization after launch

## Out of scope (Phase 1)

- Repairing or rebuilding Virtual Coworker WordPress sites
- Existing GTM / GA4 / Search Console as launch dependencies
- Full Zoho / CRM rebuild
- SEO expansion, blog, industry page farms
- Remarketing, Customer Match, offline conversions (unless Phase 2)
- Custom client dashboards before traffic launches
- PH recruiting campaigns unless they are part of paid Search

## Commercial boundary

- Fee: **$3,000** pilot
- Preliminary concepts already exist
- Additional implementation begins after payment
- Expanded work requires a separate scope and approval

## Architecture

```
Google Search Ads
  → Next.js microsite (temp domain / Vercel)
  → form or tracked phone
  → email (+ optional backup store)
  → VC qualifies manually / in CRM
  → weekly quality feedback
  → offline conversions later if justified
```

WordPress is not on the critical path.
