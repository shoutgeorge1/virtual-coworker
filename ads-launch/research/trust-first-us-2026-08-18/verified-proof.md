# Verified proof vs confirmation needed

## Used on the preview pages

| Fact | Source | Where shown |
| --- | --- | --- |
| Founded 2011 | `TRUST_PROOF.sinceYear` | Strip, why, footer |
| US + AU employer markets | Published offices in `SITE` | Proof-heavy company block, footer |
| Philippines recruitment / screening | `SITE.addressPhLabel` (no invented street) | Footer, staffing copy |
| Recruit → vet → shortlist → employer interview | Existing hiring-process copy | How it works |
| Role-specific recruiting | Existing role LPs | Role cards |
| Full-time and eligible part-time (20 hours minimum) | Existing staffing candidate copy | Why / proof modules |
| Client time zone / US hours | Existing US LP copy | Hero bullets |
| Approved testimonials | `PUBLIC_QUOTES` (published success stories) | Proof-heavy only |
| Approved client marks | `CLIENT_MARKS` | Proof-heavy only |
| LinkedIn 450K+ / Facebook 290K+ floors | `TRUST_PROOF.socialReach` | Proof-heavy company block, labeled as floors |
| US phone (888) 964-8644 | George-verified | Header / footer |
| Legal names + ABN | `COMPANY_IDENTITY` | Footer |

## Not used (needs George if we ever want them)

See `PROOF_NEEDING_CONFIRMATION` in `vision/config/trust-first.ts`.

- Fresher exact social counts
- PH street address
- Client counts, savings %, placement volume
- SOC 2 / HIPAA / PCI
- Leading with “no recruitment fees”
- Clutch / Google star widgets on this challenger (documented elsewhere; omitted here so the page stays a company site, not a ratings billboard)

Never used: competitor 70%, 0.7%, their ratings, their pricing, invented testimonials, AI portraits, raw DKI.
