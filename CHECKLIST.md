# External Funnel Audit — factual checklist

Mark each item **Found / Absent / N/A** with a public evidence pointer (`raw/…` path or URL). No guessing behind login.

## Hard rules

- Public page-load + public JS only  
- **Never** submit forms · **Never** log in · **Never** mutate ads/CRM/email  

## Checklist

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1 | Primary domain homepage captured | | |
| 2 | robots.txt / sitemap noted | | |
| 3 | About / team / ownership pages | | |
| 4 | Contact / consult / demo CTAs mapped | | |
| 5 | Pricing / offer pages (if public) | | |
| 6 | Blog / resources paths | | |
| 7 | Regional / alternate TLDs linked from nav/footer | | |
| 8 | Careers / talent / jobs paths or sister domains | | |
| 9 | Admin / app / staging hosts probed | | |
| 10 | CMS / theme / host clues | | |
| 11 | Form vendor IDs (GF, HubSpot, etc.) — **not submitted** | | |
| 12 | Chat / support widget vendor | | |
| 13 | GTM container ID(s) | | |
| 14 | Public GTM.js pulled (if ID found) | | |
| 15 | GA4 measurement ID(s) | | |
| 16 | Google Ads conversion ID(s) | | |
| 17 | Meta pixel ID(s) | | |
| 18 | LinkedIn / other pixels | | |
| 19 | Call tracking vendor | | |
| 20 | ATS / CRM public hosts (Zoho, Greenhouse, etc.) | | |
| 21 | Buyer vs candidate (or other) funnel bleed | | |
| 22 | Dual/competing conversion doors | | |
| 23 | Pixel ownership chaos (theme-hardcoded vs GTM) | | |
| 24 | Regional tracking posture differences | | |
| 25 | Discovery questions drafted for paid follow-up | | |

## Pass criteria for a sellable deliverable

- [ ] `report.html` (or Markdown twin) covers sections 1–10 from `TEMPLATE.md`  
- [ ] Hard rules printed in header/footer  
- [ ] Every “High/Critical” finding cites public evidence in `PROOF.md`  
- [ ] Offer one-pager (`OFFER.md`) matches scope in `SCOPE.md`  
- [ ] Zero form submits / logins in the work log  
