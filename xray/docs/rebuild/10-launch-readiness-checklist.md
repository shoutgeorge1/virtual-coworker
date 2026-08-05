# 10 — Launch-readiness checklist

Check boxes only when **Verified**. Do not enable paid Search until blockers clear.

---

## A. Access & commercial

- [ ] $3,000 pilot payment cleared (currently in transit to George’s bank)
- [x] Braden **Accepted** MCC Admin link — USA `496-715-1855` + AU `573-539-1940` under Shout George
- [ ] Verify Admin permission inside each US + AU account
- [ ] Spend payer named (VC card vs other)
- [ ] Day-to-day contact confirmed (Braden)
- [ ] Brand claims / “14 years” / pricing language approved for ads + LP

## B. Destination

- [ ] Canonical US + AU paid URLs chosen (microsite vs try.*)
- [ ] Thank-you URLs return **200**
- [ ] No `.ph` / careers dual-door on paid templates or thank-you
- [ ] Employer form fields match Zoho/email contract
- [ ] Gate Baseline (inline) live; variants ready but not required day one
- [ ] Spam: honeypot + server validation live

## C. Tracking

- [ ] George GTM + GA4 on paid host
- [ ] Ads tags + conversion linker verified (Tag Assistant)
- [ ] `employer_lead_form` created in both accounts — Include in Conversions **OFF**
- [ ] Job-seeker path test produces **zero** employer Ads conversions
- [ ] Enhanced conversions path decided (on/off)
- [ ] Legacy conversion actions audited/excluded (needs export or UI review)

## D. CallRail

- [ ] US + AU numbers + forward DIDs provided
- [ ] Swap on paid LP only
- [ ] `employer_lead_call` observe-only action ready
- [ ] Privacy/recording OK from Braden
- [ ] Double-count rule documented

## E. Campaign build (paused)

- [ ] Shared negative lists uploaded
- [ ] `VC_{US|AU}_S_BRAND` built — 1 AG · 1 RSA · Exact KWs · LP-only assets
- [ ] `VC_{US|AU}_S_CORE_hire_va` built — 2 AGs
- [ ] ≤3 role campaigns built
- [ ] Bid = Maximize Clicks
- [ ] Budgets set (George) — not copied blindly from Editor 100/30
- [ ] Networks: Search only; Partners off
- [ ] Legacy museum paused or isolated (George decision executed)
- [ ] No PMax / DG / DSA / broad in v1

## F. Lead ops

- [ ] Lead email US + AU working end-to-end
- [ ] Zoho write deferred OK with email interim **or** Zoho contract fields mapped
- [ ] Weekly QA ritual accepted by Braden
- [ ] Qualified-lead definition written (1 paragraph)

## G. Go-live sequence (exact order)

1. Final Tag Assistant + hire/job path tests  
2. Enable **US Brand** only (low budget)  
3. 48h diagnostics  
4. Enable **US Core**  
5. Enable **US Roles** (one at a time)  
6. Repeat AU when US search terms look employer-heavy  
7. Stay Stage 1 Max Clicks until ladder exit criteria  

## H. Explicitly NOT done in this package

- Live Ads edits · GTM publish to VC WP · Zoho connect · CallRail activate · campaign launch  

---

**Sign-off:** George (build) ______ date · Braden (business) ______ date
