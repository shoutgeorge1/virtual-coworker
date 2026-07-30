# Proof checklist — Virtual Coworker sample

Maps each executive finding → **public** evidence on disk / URL.  
Audit date: **2026-07-29**. Method: page-load + public GTM only.

## Hard rules verified

| Rule | Status |
|------|--------|
| No form submits | Held (forms observed in HTML only) |
| No login | Held (`admin` login page HTML captured, not authenticated) |
| No ads / CRM mutations | Held |

---

## Finding → evidence

| Finding | Severity | Public evidence |
|---------|----------|-----------------|
| US buyer site is WordPress (Kadence + Yoast), Kinsta/CF | Info | `raw/home.html`, `raw/headers.txt` |
| Primary CTAs → `/contact-us/` and `/contact/` | Info | `raw/home.html`, `raw/contact.html` |
| Gravity Forms IDs `gform_9` / `gform_10` | Info | contact page HTML in `raw/` |
| US GTM `GTM-TTKNKT` | Info | `raw/home.html`, `raw/gtm.js` |
| US GA4 `G-JCQKGCTYCQ` + Ads `AW-962672995` | Info | `raw/gtm.js` |
| US Meta pixel `233132881256273` (hardcoded + noscript) | High (ownership blur) | `raw/home.html` |
| AU separate GTM `GTM-KNDLKVW` / GA4 / Ads | High (regional silo) | `raw/au.html`, `raw/gtm-au.js` |
| PH homepage: no GTM in HTML | High | `raw/ph.html` |
| PH talent → Zoho Recruit | Info | `raw/ph.html` / careers links; Zoho URL in report |
| Rails Devise admin at `admin.virtualcoworker.com` | Info | `raw/admin.html` |
| Consult form includes **“I am searching for a job”** | Critical | `raw/contact.html` / contact-us capture |
| US footer pushes PH careers from buyer chrome | High | `raw/home.html` footer copy |
| Dual contact doors + Zendesk chat | High | `raw/home.html`, contact captures |
| No CallRail / obvious call tracking on sampled pages | Info | absence in `raw/home.html` + GTM sample |

---

## Package completeness

| Artifact | Present |
|----------|---------|
| `report.html` sample deliverable | Yes |
| `raw/` evidence cache | Yes |
| `TEMPLATE.md` rerun workflow | Yes |
| `CHECKLIST.md` factual checklist | Yes |
| `DISCOVERY.md` paid questions | Yes |
| `SCOPE.md` public-only boundary | Yes |
| `OFFER.md` one-page proposal | Yes |
| `README.md` product hub | Yes |
| This `PROOF.md` | Yes |

**Sellable package status:** ready for George to show locally. Outreach / send = George’s call (not this Mini cycle).
