# Selective ad-group recommendation (read-only)

**Do not implement. No Editor import. No Ads API. Brand deferred.**

19 Aug social/marketing follow-up is a separate paused add-on: `ads-launch/research/social-marketing-va-2026-08-19/REPORT.md`. This 18 Aug table is unchanged.

Evidence: `ads-launch/_rsa_challenger_review.json`, `ads-launch/US-LP-DESTINATION-MAP-2026-08-18.md`, `ads-launch/research/myoutdesk-2026-08-18/virtual-coworker-opportunity-map.md`, local GA4 notes (10–16 Aug). No invented volume or CPC.

Shared negatives to document later (not uploaded): job, jobs, salary, career, careers, apply, application, resume, work from home.

| Status | Existing / new | Campaign | Ad group | Cluster | Candidates (account language, not a bid list) | Match | LP (preview now) | Experiment | RSA | Job-seeker | Evidence | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Repair | Existing | `VC_US_S_CORE` | `Offshore_VA_PH` | PH / Filipino VA hire | philippines virtual assistant, virtual assistant in the philippines, filipino VA | Exact first | `/preview/trust-first/philippines-virtual-assistants` → future `/us/philippines-virtual-assistants` | Eligible later | Reuse existing RSAs; do not clone competitor H1 | Medium | Competitor exact on this theme; we still land `/us` | Observed |
| Preserve | Existing | `VC_US_S_CORE` | `Hire_VA_PH` | Hire a VA, 3+ word employer phrases only | hire a virtual assistant, hire dedicated VA | Exact only on long employer phrases | Master preview `/preview/trust-first/us` until PH page is approved | No generic `virtual assistants` test | Reuse | High on short heads | ST already included `virtual assistant jobs` | Observed |
| Test later | Existing | `VC_US_S_CORE` | `Staffing_Agency_PH` | Remote / PH staffing | remote staffing agency, philippines staffing agency | Exact | `/preview/trust-first/staffing` → `/us/staffing` | After `/us` measurement is trusted | Reuse | Medium (temp/job bleed) | Buyer ST exists; competitor staffing `/lp/` 404 | Observed |
| Test later | Existing | `VC_US_S_CORE` | `VA_Agency_Firm_PH` | VA agency / firm / company | virtual assistant agency, VA company, Filipino VA agency | Exact | `/preview/trust-first/virtual-assistant-agency` | Eligible later | Reuse | Low–medium | Agency ST exists; competitor agency slug 404 | Observed |
| Preserve | Existing | `VC_US_S_CORE` | `Agency_PH` | PH outsourcing agency | philippines outsourcing agency | Exact | Staffing or agency preview, not a third URL | No | Reuse | Medium | Keep; do not duplicate | Observed |
| Preserve | Existing | `VC_US_S_ROLES` | `Bookkeeping_Hire_PH` | Bookkeeping | bookkeeping VA, philippines bookkeeper | Exact | `/preview/trust-first/bookkeeping` → keep `/us/bookkeeping` | Eligible as page test | Reuse | Low | GA4 ~40 sess / 47.5% eng | Observed |
| Preserve | Existing | `VC_US_S_ROLES` | `Customer_Service_Hire_PH` | Customer service | CS / support PH | Exact | `/preview/trust-first/customer-service` | Eligible as page test | Reuse | Medium | GA4 ~22 / 68.2% | Observed |
| Preserve | Existing | `VC_US_S_ROLES` | `Sales_Hire_PH` | Sales support / follow-up | sales support VA, CRM follow-up | Exact | `/preview/trust-first/sales` | Eligible | Reuse | Medium | Do not expand setters | Observed |
| Repair | Existing | `VC_US_S_ROLES` | `Administration_EA_PH` | Admin / EA | administrative support, virtual assistant admin | Exact | `/preview/trust-first/administrative-support` | Page fix first | Reuse | Medium | GA4 ~14 / 21.4% weakest | Observed |
| Test later | Existing | `VC_US_S_ROLES` | `Digital_Marketing_Hire_PH` | Marketing execution | digital marketing VA, campaign ops | Exact | `/preview/trust-first/digital-marketing` | Eligible | Reuse | Low | GA4 ~17 / 29.4% soft | Observed |
| Test later | None live | n/a | Do not invent a duplicate RE group | Real estate VA / admin / TC | real estate virtual assistant, real estate admin | Exact if a group is ever added | `/preview/trust-first/real-estate` → `/us/real-estate` | After measurement | n/a | Low–medium | Competitor has RE LP; our page exists; restructure = WATCH | Observed / policy |
| Reject | New generic VA | — | Do not create `Virtual_Assistants` | Head term `virtual assistants` | — | — | No page built to chase it | No | — | High | Competitor has this LP; we do not want the mix | High |
| Reject | Brand | `VC_US_S_CORE` | `Brand_VC` | Brand | — | — | Deferred | No | — | Low | Brand deferred | Policy |
| Reject | Existing | `VC_US_S_ROLES` | `Appointment_Setter_Hire_PH` | Setter / cold-call | — | — | Do not lead sales LP with this | No | — | Medium-high | Prior pause guidance | Observed |
| Reject | Existing | `VC_US_S_ROLES` | `Recruitment_Hire_PH` | Careers / hiring talent | — | Negative, do not land on hire LPs | — | No | — | Very high | Job-seeker contamination | Observed |

Phrase only where the account already proved the phrase. No Broad. No new Editor file.
