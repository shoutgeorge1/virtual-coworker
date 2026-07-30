# External Funnel Audit (sample)

Productized **public-only** funnel / tracking snapshot.  
Sample target: [virtualcoworker.com](https://virtualcoworker.com/) (US + linked AU / PH / admin / Zoho).

**Deliverable:** open [`report.html`](./report.html) in a browser.

## Scope (what this product is)

- Public sites, obvious subdomains, linked regional / careers properties
- Tech stack clues from HTML (CMS, forms, chat, host headers)
- Tracking clues from page-load scripts + public GTM containers (GTM / GA4 / Ads / Meta / etc.)
- CTA paths, buyer vs talent funnel bleed, chaos / ownership signals
- Client discovery questions for a **paid** deeper audit

## Hard rules

- **Never** submit forms
- **Never** log into client systems
- **Never** mutate ads / CRM / email
- Page-load + public JS only

## How to rerun for another domain

```bash
# 1. New folder
DOMAIN=example.com
DIR=~/Developer/experiments/${DOMAIN//./-}-audit
mkdir -p "$DIR/raw" && cd "$DIR"
git init && git checkout -b agent/external-funnel-audit

# 2. Fetch homepage + key paths (adjust paths after reading nav)
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
curl -sL -A "$UA" -D raw/headers.txt -o raw/home.html "https://$DOMAIN/"

# 3. Pull GTM container if you find GTM-XXXX in HTML
# curl -sL -A "$UA" -o raw/gtm.js "https://www.googletagmanager.com/gtm.js?id=GTM-XXXX"

# 4. Probe obvious hosts (expect many to fail — that's fine)
for h in www admin app go lp careers blog staging; do
  curl -sL -A "$UA" -o /dev/null -w "$h %{http_code} %{url_effective}\n" --max-time 8 "https://$h.$DOMAIN/"
done

# 5. Copy/adapt report.html — replace findings for the new domain
# 6. Open report
open -a "Google Chrome" report.html
```

### What to grep for

| Clue | Patterns |
|------|----------|
| GTM | `GTM-` |
| GA4 / Ads | `G-`, `AW-`, `gtag(` |
| Meta | `fbq(`, `fbevents.js`, `facebook.com/tr?id=` |
| LinkedIn | `_linkedin_partner_id`, `snap.licdn.com` |
| Call tracking | `callrail`, `swap.js` |
| CRM / forms | `hubspot`, `hs-scripts`, `gform_`, `wpforms`, `pardot` |
| Chat | `zdassets`, `intercom`, `drift` |
| WP | `wp-content`, `yoast`, theme CSS |

### Checklist for the HTML report

1. Public sites / subdomains  
2. Tech stack  
3. Tracking & ads  
4. CRM / lead routing clues  
5. Buyer vs candidate (or other) funnel contamination  
6. CTAs / conversion paths  
7. Org / ownership clues from About / careers / press  
8. Chaos / agency / weak-tracking signs  
9. Client discovery questions for paid follow-up  

## This sample’s artifacts

| Path | Purpose |
|------|---------|
| `report.html` | Client-facing one-pager |
| `raw/` | Cached HTML / GTM (evidence; not required to read the report) |
| `README.md` | How to productize / rerun |

## Method notes (Virtual Coworker sample)

- Audited **2026-07-29**
- US: `GTM-TTKNKT`, GA4 `G-JCQKGCTYCQ`, Ads `AW-962672995`, Meta `233132881256273`
- AU: `GTM-KNDLKVW`, GA4 `G-W57WKPRGV9`, Ads `AW-1010248779`
- PH: Zoho Recruit; no GTM on homepage HTML
- Admin: Rails Devise at `admin.virtualcoworker.com`
