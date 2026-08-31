# Phone call → CRM forensic audit

**Date:** 24 August 2026  
**Operator:** Cursor agent (George Aguilar workspace)  
**Mode:** Read-only. No calls, emails, SMS, CRM writes, Ads/GTM/routing changes, offline uploads, or reactivation.  
**Aligns with:** `ads-launch/ASH_ZOHO_AUDIT_HANDOFF.md` (Ash owns CRM audit).

Evidence labels: **LIVE** · **DERIVED** · **INFERRED** · **MANUAL** · **UNAVAILABLE**.

---

## Executive answers (Braden / Ash)

| Question | Answer | Label |
|----------|--------|-------|
| Are inbound telephone calls entering Zoho CRM? | **Partially.** After ~19 Aug, some inbound/missed rows appear in the CRM **Calls** module (owner Cheyenne). They do **not** create Sales Enquiries (`Leads`), do **not** attach Contacts, and do **not** store the external caller’s number — Caller ID shows the US DID `+18889648644`. | LIVE |
| Since what date? | CTI-style CRM Call stubs for the 888 path appear from **19 Aug 2026** (same day Raffie says 888→Zoho Voice started). Pre-19 Aug inbound employer calls are **not** in CRM Calls (except an 11 Aug internal demo). | LIVE + MANUAL |
| Which numbers are covered? | Public US **888-964-8644** → Zoho Voice **323-300-2663** (from 19 Aug). AU **1300 886 740** not evidenced in this Voice cutover. Inventory: `ads-launch/phone-number-inventory.csv`. | LIVE + MANUAL |
| What happens to unknown callers? | Raffie: IVR → press 1 rings Cheyenne → VM if no answer; alerts to **us@**. CRM: Call activity may log without a Lead/Contact and without real ANI. **Unknown callers are not proven to become Sales Enquiries.** | MANUAL + LIVE |
| Are missed calls assigned and returned? | **Unproven.** Owner on CTI stubs = Cheyenne. No callback Tasks found. Call_Result empty. Cheyenne’s process confirmation still outstanding. | LIVE + MANUAL |
| Where are outcomes stored? | Not in `Call_Result` (null on these rows). Not in callback Tasks. Possibly email/VM/notes outside CRM — **UNAVAILABLE** until Cheyenne/Ash confirm. | LIVE |
| What historical data is missing? | **6–18 Aug US** — Raffie confirms **Grasshopper** (24 Aug); open CSV `Detail_08.24.2026_11.15.58_AM.csv` attached same day (local ingest pending). Aug 19+ Voice still password-zip in Gmail. Pre-divert 310 path; full AU inbound history. | PARTIAL + UNAVAILABLE |
| How many potential employer calls need review? | **UNAVAILABLE** as a number. Do not treat ~62 phone-link clicks as callers. Build review queue only after Voice ingest + human classification. | UNAVAILABLE |

**Bottom line:** Zoho Voice and Zoho CRM are related products, not a proven end-to-end lead system. Today’s evidence is **call log / CTI stub ≠ owned enquiry with disposition**.

---

## 1. Reality check (repo)

| Item | Finding |
|------|---------|
| Branch | `preview/trust-first-us-lps` (dirty tree unrelated to this audit) |
| Ash handoff | `ads-launch/ASH_ZOHO_AUDIT_HANDOFF.md` — CRM modules, read-only scopes, no Voice section |
| Zoho env | `ZOHO_CRM_*` refresh token present; `ZOHO_CRM_ENABLED=false`; **no Zoho Voice API credentials** |
| Private data | `.local/zoho/` (gitignored); new `.local/phone-call-forensic/` for Voice PII |
| Prior phone docs | Call-asset 888/310 notes; CallRail map is **spec only**; lead-routing is form/email-first |
| Launch Control | Had phone conversion QA items; **no** “Phone lead recovery” parent until this pass |

---

## 2. Architecture (as evidenced)

```text
[Ads / microsite / WP]
   tel: +18889648644  or  +611300886740
        │
        ├─ Google Ads: Call asset / website-call 60s / phone-click  (measurement)
        │     ≠ CRM record
        │
        ▼
US 888 ──(from 19 Aug)──► Zoho Voice 323-300-2663 ──IVR──► Cheyenne / Jona / VM
        │                      │
        │                      ├─ email alerts → us@
        │                      └─ ? PhoneBridge/CTI → CRM Calls activity
        │                            (Caller = DID, no Lead, no Call_Result)
        │
        └─(before 19 Aug)──► Prior IVR + extensions + VM-to-email  [logs UNAVAILABLE]

Forms (separate path) ──► us@ / apac@ / GitHub Issues ──► (Zoho Sales Enquiry writes deferred)
```

**Do not infer** Voice→CRM completeness from shared “Zoho” branding.

### CRM objects touched by this audit (LIVE)

| Object | API | Role |
|--------|-----|------|
| Calls | `Calls` | Activity log; fields include `Call_Type`, `Call_Result`, `Caller_ID`, `From_Number__s`, `To_Number__s`, `Telephony_External_ID__s`, `Who_Id`, `What_Id`, `Owner` |
| Sales Enquiries | `Leads` | Front door — **not** auto-filled by Voice in this evidence |
| Tasks | `Tasks` | Would hold callbacks — **none** matching missed/VM language since Aug 6 |

`CTI_Entry` exists in field metadata but is **unsupported in COQL** (`unsupported column`). `Telephony_External_ID__s` readable but null on sampled Aug 19+ rows.

---

## 3. Zoho Voice → Zoho CRM integration matrix

| Capability | Status | Evidence |
|------------|--------|----------|
| Match inbound ANI to Contact/Account | **No** (for 888 CTI stubs) | Who_Id empty; Caller_ID = DID |
| Create Sales Enquiry for unknown caller | **No** | Lead_Source=Phone: 3 rows since Aug 6, all Aug 13, not Voice-shaped |
| Create Calls-module activity | **Partial** | 12 inbound/missed DID-as-from rows Aug 19–21; owner Cheyenne |
| Assign sales owner | **Partial** | Owner set to Cheyenne on those stubs; not a classified enquiry owner workflow |
| Direction / time / duration | **Partial** | Call_Type Inbound/Missed; durations present; start times present |
| Answered vs missed | **Partial** | Call_Type only; no rich Voice disposition in CRM |
| IVR selection | **No** in CRM | Not on Call fields sampled |
| Voicemail / transcription | **No** in CRM sample | Voice_Recording rare; not on DID stubs |
| Callback Task | **No** | Zero matching Tasks |
| Follow-up attempts | **No** evidence | |
| Final disposition | **No** | Call_Result null (82/82 Aug 6+ grouped null in first probe; 365d almost all null) |
| Link to Job Order / Placement | **No** | What_Id empty on DID stubs |
| Marketing attribution (gclid) | **No** on Call rows | |

**Verdict:** Integration is **partial CTI logging**, not a sales CRM intake pipeline.

Raw (redacted) probes: `.local/zoho/phone-call-crm-forensic-probe*-2026-08-24.json`.

---

## 4. Historical coverage

| Window | Voice / telco | CRM Calls | Notes |
|--------|---------------|-----------|-------|
| US launch (~6 Aug) → 18 Aug | **Grasshopper** (Raffie). Detail zip attached (~1 Jul–18 Aug) | Demo-only inbound/missed in CRM (11 Aug Caitlin Instant Trial) | Files password-protected — George requested open CSV/Excel |
| 19 Aug → audit | Zoho Voice; Voice zip in Gmail (pw-protected); **not ingested** | 46 Calls (33 out / 7 in / 5 missed) | Export range in filename: 19 Aug 09:20 → 24 Aug 09:20 |
| Prior 90 days | Partial via Grasshopper export claim | 407 Calls | Dominated by Outbound in CRM |
| Prior 12 months | UNAVAILABLE | 1170 Calls | Disposition field almost unused |

**Raffie (MANUAL, 24 Aug email — updated):**

1. 888→323 forwarding began **19 Aug 2026** (scheduled Zoho Voice project)  
2. Before that: **Grasshopper** IVR + extensions; VM to respective emails  
3. Press 1 → Cheyenne → VM; alerts → **us@**  
4. Attached password-protected Voice zip + Grasshopper Detail zip (passwords only in email — **never commit**)  
5. Voice→CRM: known contacts can associate; **unknown callers need manual save**; Call Disposition for outcome/follow-up; process **still in testing** after rollout

---

## 5. Call ↔ CRM reconciliation (method)

1. Normalize company DIDs to E.164 (inventory CSV).  
2. Prefer deterministic matches: exact ANI, Telephony external id, explicit related record.  
3. **Blocked for Aug 19+ CRM stubs:** ANI is the DID — cannot match Leads by phone.  
4. Weaker matches (same-day timestamp, name-only) — **not used**; would silently merge people.  
5. Voice export ingest (when local): mask ANI to last-4 in any public artifact; full queue stays in `.local/phone-call-forensic/`.

### Outcome classes (required going forward)

Potential employer · Qualified employer · Forwarded to sales · Discovery completed · Existing client/support · Job seeker · Vendor/competitor · Spam · Test · Missed — callback completed/pending/none · Voicemail — callback completed/pending · Unknown  

**Rules:** Email notification ≠ follow-up. Call log ≠ CRM enquiry. Answered ≠ qualified employer.

---

## 6. Failure / opportunity measure

| Metric (US) | Value | Label |
|-------------|------:|-------|
| Ads phone-link clicks (stated) | ~62 | MANUAL — **not calls** |
| CRM Calls since Aug 6 | 88 | LIVE |
| CRM Inbound + Missed since Aug 6 | 17 | LIVE (12 DID stubs + 5 demo) |
| Unique external callers (Voice) | — | **UNAVAILABLE** |
| Answered / missed / VM (Voice) | — | **UNAVAILABLE** |
| Calls with owner (CTI stubs) | 12/12 Cheyenne | LIVE |
| Calls with callback Task | 0 | LIVE |
| Calls with Call_Result | 0 (sample) | LIVE |
| Sales Enquiries Lead_Source=Phone | 3 (Aug 13) | LIVE |
| AU inbound | — | **UNAVAILABLE** |

Aggregate CSV: `ads-launch/phone-call-reconciliation-summary.csv`.

---

## 7. Recovery-queue design (not launched)

**High priority (human review only):** recent Voice missed/VM · IVR=1 · employer-shaped · no callback evidence · not junk/seeker/test/client · no DNC.

**Older reactivation:** stricter filters · **one** human-approved attempt max · Braden + Ash + sales owner · no automation.

**Status now:** Queue file reserved at  
`.local/phone-call-forensic/recovery-review-queue.csv`  
— **empty** until Voice export is analyzed. Public dashboard shows **UNAVAILABLE**, not zero.

---

## 8. Smallest safe future-state SOP (proposal only)

1. Every inbound call logged (Voice **and** CRM).  
2. Known ANI matched to Contact/Account.  
3. Unknown new-client (IVR 1) → Sales Enquiry or explicit review queue.  
4. Missed legitimate → callback Task + owner.  
5. Named owner attempts within agreed SLA.  
6. Final disposition on every call.  
7. Employers advance Discovery → Job Order → Placement.  
8. Separate seekers / spam / tests / support.  
9. Named backup when Cheyenne unavailable (Braden to assign).  
10. Weekly unresolved-call review (Ash + sales).  

**Do not** implement CRM workflows in this audit.  
**Keep** Zoho offline conversion uploads **deferred** until records are clean.

---

## 9. Ownership (next actions)

| Action | Owner |
|--------|-------|
| Read-only CRM linkage validation | **Ash** |
| Telco inventory + pre-19 Aug export + Voice access | **Raffie** |
| US classification + callback confirmation | **Cheyenne** |
| AU classification + 1300 path | **Holly** |
| Ops ownership + reactivation approval | **Braden** |
| Paid-media / tracking QA only | **George** |

George does **not** own telephone operations, CRM governance, or callback execution.

---

## 10. Deliverables index

| File | Contents |
|------|----------|
| `ads-launch/PHONE_CALL_CRM_FORENSIC_AUDIT.md` | This report |
| `ads-launch/phone-number-inventory.csv` | Company DIDs only |
| `ads-launch/phone-call-reconciliation-summary.csv` | Aggregate / masked |
| `xray/data/phone-call-forensic.json` | Dashboard aggregates |
| `xray/phone-call-forensic.html` | Aggregate UI |
| `.local/phone-call-forensic/` | Private Voice zip + recovery queue (gitignored) |
| `ads-launch/analyze_zoho_voice_export_readonly.py` | Local Voice zip analyzer |
| `.local/phone-call-forensic/DRAFT-BRADEN-ASH-EMAIL.md` | Draft only — not sent |

---

## 11. Definition of done — checklist

| Required statement | Status |
|--------------------|--------|
| Whether Voice is integrated with CRM | **PARTIAL** — evidenced |
| Whether inbound creates/matches CRM records | **Does not create Leads; Call stubs without ANI/match** |
| Historical periods / numbers covered | Documented; gaps labeled UNAVAILABLE |
| Unique callers / answered / missed / VM | **UNAVAILABLE** until Grasshopper CSV + Aug 19+ Voice ingest (Raffie open CSV received 24 Aug) |
| Callback attempts | **0 CRM Task evidence** |
| Represented in CRM as enquiries | **Not evidenced** |
| Potential employers / recovery review count | **UNAVAILABLE** (not zero) |
| Operational change + owners | SOP + ownership table above |
