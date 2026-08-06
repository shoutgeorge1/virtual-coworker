# 12 — Blocker / decision list (v7)

**Status: NOT TRAFFIC READY** while hard blockers remain.  
Sequencing lock: **TRAFFIC READY** ≠ **CRM READY** ≠ **OPTIMIZATION READY** (`DECISIONS.md`).

| # | Blocker | Owner | Decision needed |
|---|---------|-------|-----------------|
| 1 | **AU phone** | ~~open~~ | **Locked:** form-primary — no fake AU number (`DECISIONS.md`) |
| 2 | **Lead recipients** | George / Braden | **TRAFFIC READY hard blocker.** Real `LEAD_EMAIL_*` / Resend / webhook / sheet. Log-only ≠ TRAFFIC READY |
| 3 | **Named responder + process** | Ops | Who answers inquiries, practical response process |
| 4 | **Durable delivery verified** | George | Live-format test reaches destination; failure paths honest |
| 5 | **Zoho (CRM READY — parallel)** | George | **Not a traffic gate.** Access exists (level unknown). Bootstrap/inventory when ready. Access ≠ CRM READY. Offline values TBD — not approved. |
| 6 | **Architecture / budgets** | ~~open~~ | **Locked:** 2 campaigns/account; Core→`/us`/`/au`; Roles→category; Brand deferred |
| 7 | **Max CPC** | ~~open~~ | **Locked defaults:** US $8 · AU A$6 · Maximize Clicks |
| 8 | **Proof / content** | Marketing | Badges OK as badges; no invented testimonials/pricing |
| 9 | **CallRail timing** | George | OPTIMIZATION later — don’t treat phone clicks as qualified until live |
| 10 | **Careers URL** | ~~open~~ | **Locked:** `/ph` microsite (never WP) |
| 11 | **US + AU paid domains** | George | Nice-to-have for TRAFFIC READY; preview host OK. OPTIMIZATION path when bought |
| 12 | **GTM / GA4 / GSC per market** | George | **OPTIMIZATION READY** — separate containers; map inquiry after durable delivery |
| 13 | **Legacy live brand / museum campaigns** | George | Pause/coexist decision outside this CSV |
| 14 | **ENABLE anything** | George | Explicit approval only after TRAFFIC READY — package ships Paused |
| 15 | **Brand Search** | George | Deferred — add later only with explicit scope |
| 16 | **Ads conversion firing** | George | Keep disabled until GTM mapping tested (OPTIMIZATION READY) |

---

## Non-blockers (already handled locally)

- Three microsites: `/us`, `/au`, `/ph` · `/` → `/us`  
- Category LP routes + A/B  
- Core Final URLs = market home (v7)  
- HR alias `/human-resources` → `/hr`  
- Double UTM fixed (`{lpurl}` + suffix once)  
- WP-link audit test  
- Log-only cannot fire primary conversion  
- Exit-intent behind flag; no fake chat  
- 2-campaign architecture + RSA×3  
