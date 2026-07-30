# External Funnel Audit — sellable package

Productized **public-only** funnel / tracking snapshot.  
**Sample target:** [virtualcoworker.com](https://virtualcoworker.com/) (US + linked AU / PH / admin / Zoho).

**Show the sample:** open [`report.html`](./report.html) in a browser.

```bash
open -a "Google Chrome" ~/Developer/experiments/virtual-coworker-audit/report.html
```

---

## Hard rules (loud)

| NEVER | NEVER | NEVER |
|-------|-------|-------|
| **Submit forms** | **Log into client systems** | **Mutate ads / CRM / email** |

Page-load HTML + public JS / public GTM only. Full boundary: [`SCOPE.md`](./SCOPE.md).

---

## Package contents (sales-ready)

| File | Purpose |
|------|---------|
| [`report.html`](./report.html) | Sample client-facing deliverable (Virtual Coworker) |
| [`OFFER.md`](./OFFER.md) | One-page local offer / proposal |
| [`TEMPLATE.md`](./TEMPLATE.md) | Repeatable copy-and-run workflow + report skeleton |
| [`CHECKLIST.md`](./CHECKLIST.md) | Factual audit checklist |
| [`DISCOVERY.md`](./DISCOVERY.md) | Paid-audit client discovery questions |
| [`SCOPE.md`](./SCOPE.md) | Public-only scope boundary |
| [`PROOF.md`](./PROOF.md) | Findings → public evidence map (this sample) |
| [`raw/`](./raw/) | Cached HTML / GTM evidence |

---

## Copy-and-run (another domain)

See **[`TEMPLATE.md`](./TEMPLATE.md)** — full curl workflow. Short version:

```bash
DOMAIN=example.com
DIR=~/Developer/experiments/${DOMAIN//./-}-audit
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
mkdir -p "$DIR/raw" && cd "$DIR"
curl -sL -A "$UA" -D raw/headers.txt -o raw/home.html "https://$DOMAIN/"
# …paths, subdomain probe, optional GTM pull — then fill CHECKLIST → report → PROOF
open -a "Google Chrome" report.html
```

### Grep for

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

---

## This sample (Virtual Coworker)

- Audited **2026-07-29**
- US: `GTM-TTKNKT`, GA4 `G-JCQKGCTYCQ`, Ads `AW-962672995`, Meta `233132881256273`
- AU: `GTM-KNDLKVW`, GA4 `G-W57WKPRGV9`, Ads `AW-1010248779`
- PH: Zoho Recruit; no GTM on homepage HTML
- Admin: Rails Devise at `admin.virtualcoworker.com`
- Loud finding: buyer consult form accepts **job seekers**

Money path: George shows `report.html` + `OFFER.md` → prospect picks a domain → run template → paid discovery (`DISCOVERY.md`) → optional Phase 2 tracking hygiene SOW.

**Not this cycle:** push, email, LinkedIn, form submit, Ads mutations, Gmail.
