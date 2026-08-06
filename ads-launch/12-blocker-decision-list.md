# 12 — Blocker / decision list

**Do not declare launch-ready while these remain.**

| # | Blocker | Owner | Decision needed |
|---|---------|-------|-----------------|
| 1 | **AU phone** | ~~open~~ | **Locked:** form-primary — no fake AU number (`DECISIONS.md`) |
| 2 | **Lead recipients** | George / Braden | Still open for paid. QA uses TEMPORARY `ALLOW_LOG_ONLY_LEADS=true` (logs only; not a real inbox) |
| 3 | **Response time SLA** | Ops | Who answers inquiries, how fast? |
| 4 | **Temp delivery method** | George | Log-only for QA now; replace with email/webhook before paid traffic |
| 5 | **Zoho** | George | Unresolved — optional; must not fake sync |
| 6 | **Budgets** | ~~open~~ | **Locked defaults:** US Brand $40 / Core $60 / Role $25; AU Brand+Core A$40 / Role A$20 |
| 7 | **Max CPC** | ~~open~~ | **Locked defaults:** US $8 · AU A$6 |
| 8 | **Proof / content** | Marketing | Badges OK as badges; no invented testimonials/pricing |
| 9 | **CallRail timing** | George | Later-ready — don’t treat phone clicks as qualified until live |
| 10 | **Careers URL** | ~~open~~ | **Locked:** `NEXT_PUBLIC_CAREERS_URL=/ph` (microsite PH path) |
| 11 | **Paid host / domain** | George | Keep vision host or attach custom paid domain |
| 12 | **GTM / Ads conversion mapping** | George | Map `employer_inquiry_submitted` carefully — observe first |
| 13 | **Legacy live brand / museum campaigns** | George | Pause/coexist decision outside this CSV |
| 14 | **ENABLE anything** | George | Explicit approval only — package ships Paused |

---

## Non-blockers (already handled locally)

- Category LP routes exist  
- A/B assignment exists  
- Double UTM fixed in package  
- Consult/demo language removed from Stage 1 RSA + LP CTAs  
- Historical ST mined into Exact/Phrase (with limitations documented)
