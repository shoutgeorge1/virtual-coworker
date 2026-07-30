# External Funnel Audit — repeatable template

Copy this workflow for any public domain. Sample proof: Virtual Coworker in this repo (`report.html` + `raw/`).

## Hard rules (loud)

| NEVER | NEVER | NEVER |
|-------|-------|-------|
| Submit forms | Log into client systems | Mutate ads / CRM / email |
| Click “Buy” / checkout | Fill contact fields “just to see” | Touch Google Ads / Meta admin |

**Allowed:** `curl` / browser view-source / public JS / public GTM containers / robots + sitemaps / obvious linked subdomains.

---

## Copy-and-run (one domain)

```bash
DOMAIN=example.com
SLUG=${DOMAIN//./-}
DIR=~/Developer/experiments/${SLUG}-audit
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

mkdir -p "$DIR/raw" && cd "$DIR"
# optional: git init && git checkout -b agent/external-funnel-audit

# 1) Homepage + headers
curl -sL -A "$UA" -D raw/headers.txt -o raw/home.html "https://$DOMAIN/"

# 2) Key paths (adjust after reading nav / footer)
for path in about contact pricing careers blog faq how-it-works; do
  curl -sL -A "$UA" -o "raw/${path}.html" --max-time 15 "https://$DOMAIN/${path}/" || true
done

# 3) Subdomain probe (many 000 — fine)
for h in www admin app go lp careers blog staging shop; do
  curl -sL -A "$UA" -o /dev/null -w "$h %{http_code} %{url_effective}\n" --max-time 8 "https://$h.$DOMAIN/" || true
done | tee raw/subdomain-probe.txt

# 4) If GTM-XXXX found in HTML:
# curl -sL -A "$UA" -o raw/gtm.js "https://www.googletagmanager.com/gtm.js?id=GTM-XXXX"

# 5) Grep clues → fill CHECKLIST.md → write report.html from this TEMPLATE → map PROOF.md
# 6) open -a "Google Chrome" report.html
```

---

## Report skeleton (fill per domain)

Use as Markdown draft or mirror sections into `report.html`.

1. **Public properties found** — table: URL · role · notes  
2. **Tech stack clues** — CMS, forms, chat, host, bots  
3. **Tracking & ads** — GTM / GA4 / Ads / Meta / LinkedIn / call tracking IDs  
4. **CRM / lead routing clues** — forms destination *unknown without submit*; admin / ATS hosts  
5. **Funnel contamination** — buyer vs talent / support bleed  
6. **CTAs & conversion paths** — primary + secondary doors  
7. **Org / ownership clues** — About / careers / press only  
8. **Chaos / weak-tracking signs** — split stacks, hardcoded pixels, dual forms  
9. **Client discovery questions** — paid kickoff only (see `DISCOVERY.md`)  
10. **Top findings (executive)** — ≤5 bullets  

Footer every deliverable: *Public crawl only · No form submits · No login · No ads mutations.*

---

## Grep cheat sheet

| Clue | Patterns |
|------|----------|
| GTM | `GTM-` |
| GA4 / Ads | `G-`, `AW-`, `gtag(` |
| Meta | `fbq(`, `fbevents.js` |
| LinkedIn | `_linkedin_partner_id`, `snap.licdn.com` |
| Call tracking | `callrail`, `swap.js` |
| CRM / forms | `hubspot`, `gform_`, `wpforms`, `pardot`, `zoho` |
| Chat | `zdassets`, `intercom`, `drift` |
| WP | `wp-content`, `yoast` |
