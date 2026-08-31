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

## Used in the 18 Aug ATF upgrade

| Fact | How shown |
| --- | --- |
| Google 5.0 / 39 (West Hollywood GBP) | Yellow stars + mid-page badge. No outbound link. |
| Clutch 4.9 / 7 | Yellow stars + mid-page badge. No outbound link. |
| 15 years / since 2011 | Stat chips |
| LinkedIn 450K+ / Facebook 290K+ floors | Stat chips (wow proof instead of invented client counts) |
| Approved client marks | Logo row in the hero |
| One published client quote | ATF highlight |
| PH EF EPI 2025 high band, 28/123, score 569 | PH page only, labeled as a country ranking |
| IBPAP ~1.68M contact-center / BPS FTEs | PH page only, labeled as industry headcount, not our roster |

## Skipped

| Asset | Why |
| --- | --- |
| People photos | No named CEO, staff, or client headshot in the repo. `va-face-*`, `va-us.jpg`, `va-team.webp`, `talent-*`, and `/roles` portraits read as stock or AI LP art (`IMAGE-CHOICES.md` documents GenerateImage). `talent-arvin` / `talent-john` are named PH staff with unknown ad permission. Client marks stay in the hero. Testimonials use initials. |
| Video testimonials | None on disk. Inventory 16 Aug: no official YouTube channel confirmed. |
| Testimonial videos | CRO backlog: no approved sales-video file yet. Do not fake embeds. |
| Client counts, dollars saved, 70% cost cut | Not documented for Virtual Coworker. |
| Mid-page client logo strip | Removed 18 Aug. Same marks already sit in the hero. |

## Not used (needs George if we ever want them)

See `PROOF_NEEDING_CONFIRMATION` in `vision/config/trust-first.ts`.

- Fresher exact social counts
- PH street address
- Client counts, savings %, placement volume
- SOC 2 / HIPAA / PCI
- Leading with “no recruitment fees”
- Clutch / Google star widgets on this challenger (documented elsewhere; omitted here so the page stays a company site, not a ratings billboard)

Never used: competitor 70%, 0.7%, their ratings, their pricing, invented testimonials, AI portraits, raw DKI.
