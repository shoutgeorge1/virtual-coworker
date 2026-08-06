# 12 — Blocker / decision list (v7)

**Status: NOT READY FOR PAID TRAFFIC** while hard blockers remain.

| # | Blocker | Owner | Decision needed |
|---|---------|-------|-----------------|
| 1 | **AU phone** | ~~open~~ | **Locked:** form-primary — no fake AU number (`DECISIONS.md`) |
| 2 | **Lead recipients** | George / Braden | **Hard blocker.** Real `LEAD_EMAIL_*` / Resend / webhook. Log-only is blocked mode — not paid-ready |
| 3 | **Response time SLA** | Ops | Who answers inquiries, how fast? |
| 4 | **Durable delivery verified** | George | End-to-end success + failure paths tested with real channel |
| 5 | **Zoho** | George | **Open/waiting:** access exists (level unknown). Audit modules / fields / ownership (download/export OK for later). Access ≠ integration. Plan offline conversion actions later (job order $200–$400 TBD · placement $500–$800 TBD — **not approved**; unique Zoho IDs; no double-count without rules; GCLID path). Stage 1 primary = employer inquiry + qualified call — not order/placement. |
| 6 | **Architecture / budgets** | ~~open~~ | **Locked:** 2 campaigns/account; Core→`/us`/`/au`; Roles→category; Brand deferred |
| 7 | **Max CPC** | ~~open~~ | **Locked defaults:** US $8 · AU A$6 |
| 8 | **Proof / content** | Marketing | Badges OK as badges; no invented testimonials/pricing |
| 9 | **CallRail timing** | George | Later-ready — don’t treat phone clicks as qualified until live |
| 10 | **Careers URL** | ~~open~~ | **Locked:** `/ph` microsite (never WP) |
| 11 | **US + AU paid domains** | George | Buy/attach on Vercel; keep path structure |
| 12 | **GTM / GA4 / GSC per market** | George | Separate containers; map `employer_inquiry_submitted` only after durable delivery |
| 13 | **Legacy live brand / museum campaigns** | George | Pause/coexist decision outside this CSV |
| 14 | **ENABLE anything** | George | Explicit approval only — package ships Paused |
| 15 | **Brand Search** | George | Deferred — add later only with explicit scope |
| 16 | **Ads conversion firing** | George | Keep disabled until GTM mapping tested |

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
