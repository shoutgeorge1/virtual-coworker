# Virtual Coworker — Phone / CRM forensic brief for ChatGPT

**Date:** 24 August 2026  
**Author:** George Aguilar (via Cursor read-only audit)  
**Purpose:** Paste this entire file into ChatGPT to draft emails (especially Braden meeting deflection), ops follow-ups, executive summaries, or stakeholder replies.  
**George’s role:** Paid-media and tracking QA only — **not** phone operations, CRM governance, or callback execution.

**Evidence labels used throughout:** LIVE · DERIVED · INFERRED · MANUAL · UNAVAILABLE.

---

## Punchline (say this first)

**Phone calls are not reliably becoming owned CRM enquiries with outcomes.** Zoho Voice and Zoho CRM are related products, not a proven sales pipeline. US ads show ~**62 phone-link clicks** (button taps), **not** verified completed calls. After **19 Aug 2026**, 888 forwards to Zoho Voice; before that, **Grasshopper**. CRM shows **partial** Call activity (often with the **888 number as caller**, not the real person), **no** auto Sales Enquiry, **empty** dispositions, **no** callback Tasks. Cheyenne **manually** logs only calls she considers legitimate and says **most US calls are job seekers/solicitors**.

**Grasshopper CSV (now processed):** Raffie’s open export `Detail_08.24.2026_11.15.58_AM.csv` covers **7 Aug – 18 Aug 2026** on the **888** line only (pre–Voice cutover). **23 inbound legs**, **15 unique external callers**, **14** forwarded/connected, **9** hangups, **0** voicemails on 888 in this file. **Does not** cover Aug 19+ (Zoho Voice) or full Aug 6 launch day.

**Bottom line for Braden:** The telephone system has logs outside CRM; CRM linkage is broken or partial; employer recovery count still needs Cheyenne classification — not automatic from call volume alone.

---

## What George fixed (tracking — LIVE)

- US microsite displayed `888-964-8644` on mobile while Google’s website-call tag expected `(888) 964-8644`. **Corrected and deployed** on live `/us`.
- That mismatch could block Google number replacement on mobile → phone **clicks** without attributed **calls**.
- **Does not prove** CRM logging or employer lead capture works.
- Offline conversion uploads to Google remain **deferred** until call/CRM records are clean (Ash).

---

## Full timeline (US 888 path)

| When | What happened | Evidence |
|------|----------------|----------|
| Pre–Aug 2026 | Legacy agency inventory; trickle spend; Brand deferred | MANUAL / George context |
| ~6 Aug 2026 | US paid campaign launch; public **888-964-8644** on microsite + Call asset | LIVE (ads package) |
| 7–10 Aug | Brief **310** Call asset on VC_US_* then **removed**; 888 restored | LIVE (Editor notes) |
| ~11 Aug | Braden divert **310-426-8776 → 310-730-9126** (Cheyenne handset) | MANUAL (Raffie email thread) |
| 7–18 Aug | **Grasshopper** IVR on 888; extensions (0 Operator, 1 Sales, Main, 703 Zoho Voice test) | DERIVED (Grasshopper CSV) + MANUAL (Raffie) |
| 11 Aug | Internal CRM demo call (Caitlin Instant Trial) — only pre–19 Aug inbound in CRM | LIVE (COQL) |
| **19 Aug** | Raffie: 888 → **Zoho Voice 323-300-2663**; new IVR (1 Cheyenne new client, 2 Jona support, 3 other, 4 menu) | MANUAL (Raffie) |
| 19–21 Aug | CRM **Calls** stubs appear: Caller ID = **+18889648644** (the DID), owner Cheyenne, Call_Result empty | LIVE (COQL) |
| 24 Aug | Raffie emails Grasshopper CSV (open) + password zips (Grasshopper Jul–18, Voice Aug 19–24) | MANUAL |
| 24 Aug | George read-only CRM COQL audit + Grasshopper CSV ingest | LIVE + DERIVED |
| **Gap** | Aug 19+ Voice export **not** ingested (password zip); Aug 6 single day may be missing from Grasshopper CSV | UNAVAILABLE |

**Week definition for sales ops (Cheyenne/Holly):** Monday–Sunday, 7 days — not Mon–Fri.

---

## Number inventory (narrative)

Public US marketing number: **(888) 964-8644** → E.164 `+18889648644`. Used on virtualcoworker.app/us, WordPress US pages, and Google Ads Call asset / website-call (60s).

**From 19 Aug:** 888 forwards to Zoho Voice DID **323-300-2663** (not a public ad destination). IVR routes press-1 to Cheyenne (VM if no answer); alerts to **us@virtualcoworker.com**.

**Before 19 Aug:** Grasshopper hosted IVR. CSV shows extensions: **Main** (9 inbound legs), **0 - Operator** (12), **1 - Sales and Client Services** (1), **703 - Zoho Voice** (1 leg on 18 Aug — cutover test). Forward target during period was often **310-730-9126** (Cheyenne).

**Other US numbers in play (not primary ad CTA):** 310-730-9126 (Cheyenne direct / former ad asset), 310-426-8776 (prior ad path, diverted), 310-638-5092 and 213-224-8353 (other Grasshopper DIDs in same export — mostly non-888 traffic). **888-954-8644** is a paused wrong-digit museum asset — do not use.

**AU:** **1300 886 740** — separate path; Holly Wallace; ~2 phone-link clicks in ads period; voicemail still says “Alex” (known ops issue). No AU Voice→CRM proof in this pass.

Full inventory table: `ads-launch/phone-number-inventory.csv`.

---

## Ads vs calls (do not combine)

| Metric | Value | Label | Meaning |
|--------|------:|-------|---------|
| US phone-link clicks (stated) | ~62 | MANUAL | User tapped `tel:` or call asset — **not** completed calls |
| Verified call conversions in Ads | Unverified / low | INFERRED | Tracking setup ≠ call volume |
| Grasshopper 888 inbound legs (7–18 Aug) | 23 | DERIVED | Inbound leg rows only |
| Grasshopper unique external callers (888, same window) | 15 | DERIVED | Distinct Caller ID on inbound legs |
| Grasshopper answered (forwarded connected) | 14 | DERIVED | Type: inbound leg of forwarded call |
| Grasshopper hangup (888 inbound) | 9 | DERIVED | Short abandon / no forward |
| Grasshopper voicemail (888) | 0 | DERIVED | In this export |
| CRM Calls since Aug 6 | 88 | LIVE | Mostly outbound ops |
| CRM inbound+missed since Aug 6 | 17 | LIVE | 12 DID-as-caller stubs + 5 demo |
| CRM Sales Enquiries Lead_Source=Phone since Aug 6 | 3 (all 13 Aug) | LIVE | Pre–Voice cutover; not Voice-shaped |

**Rule:** `phone_link_clicks ≠ unique_callers ≠ CRM_Calls ≠ Sales_Enquiries`.

---

## Zoho CRM read-only findings (COQL, 24 Aug 2026)

**Do not treat “a Call row exists” as “a qualified employer lead.”**

### Window counts (Calls module)

| Window | Total | Outbound | Inbound | Missed |
|--------|------:|---------:|--------:|-------:|
| Since Aug 6 | 88 | 65 | 8 | 9 |
| Since Aug 19 | 46 | 33 | 7 | 5 |
| Prior 90d | 407 | 390 | 8 | 9 |
| Prior 365d | 1170 | — | — | — |

### Aug 19+ inbound/missed pattern (LIVE sample)

- Subject lines: `Incoming call from +18889648644` / `Missed call from +18889648644`
- **Caller_ID / From_Number** resolve to the **US DID**, not external ANI
- **Who_Id** (Contact/Lead link): **empty** on DID-as-from rows
- **Call_Result:** **null** on all Aug 6+ grouped rows (82/82 null in probe)
- **Telephony_External_ID__s:** null on sampled Aug 19+ rows
- **CTI_Entry:** field exists in metadata but **unsupported in COQL**
- Owner on stubs: **Cheyenne** (6724032000001006001)

### Tasks (callbacks)

- Tasks since Aug 6: **106** total (all subjects)
- Tasks matching missed/callback/voicemail language since Aug 6: **0** (LIVE)

### Leads / Sales Enquiries

- Leads with phone since Aug 6: **79** (any source)
- Lead_Source=Phone since Aug 6: **3** rows, dated **13 Aug only** — before Voice cutover
- Dominant Lead_Source remains **Website**

### Other CRM notes

- Call_Result populated on only ~13 rows in 365d (mostly legacy outbound disposition labels)
- No gclid on Call rows — cannot tie to paid click directly in CRM

Raw redacted probes: `.local/zoho/phone-call-crm-forensic-probe*-2026-08-24.json` (gitignored).

---

## Zoho Voice → Zoho CRM integration matrix

| Capability | Status | Evidence |
|------------|--------|----------|
| Match inbound ANI to Contact/Account | **No** (888 CTI stubs) | Who_Id empty; Caller_ID = DID |
| Create Sales Enquiry for unknown caller | **No** | No Voice-era Phone-source Leads |
| Create Calls-module activity | **Partial** | 12 inbound/missed DID-as-from Aug 19–21 |
| Assign sales owner | **Partial** | Owner = Cheyenne on stubs |
| Direction / time / duration | **Partial** | Call_Type + durations present |
| Answered vs missed | **Partial** | Call_Type only; no rich Voice disposition in CRM |
| IVR selection | **No** in CRM | Not on Call fields sampled |
| Voicemail / transcription | **No** in CRM sample | Voice_Recording rare; not on DID stubs |
| Callback Task | **No** | Zero matching Tasks |
| Final disposition | **No** | Call_Result null |
| Link to Job Order / Placement | **No** | What_Id empty |
| Marketing attribution (gclid) | **No** on Calls | |

**Verdict:** **Partial CTI logging**, not a sales CRM intake pipeline. Raffie (MANUAL): known contacts may associate; unknown callers manual; process **still in testing**.

---

## Grasshopper CSV results (DERIVED — 24 Aug ingest)

**File:** `Detail_08.24.2026_11.15.58_AM.csv` (local: `.local/phone-call-forensic/`, gitignored)  
**Analyzer:** `ads-launch/analyze_grasshopper_export_readonly.py`  
**Summary JSON:** `.local/phone-call-forensic/grasshopper-export-summary.json`

| Metric | Value |
|--------|------:|
| Detail rows (all DIDs in file) | 46 |
| US 888 inbound legs | 23 |
| US 888 outbound legs (paired forwards) | 13 |
| Unique external callers (888 inbound) | **15** |
| Date range (888 inbound) | **7 Aug – 18 Aug 2026** |
| Answered / forwarded (888 inbound) | 14 |
| Hangup (888 inbound) | 9 |
| Voicemail (888 inbound) | 0 |
| Usage totals (file header) | 32 min in / 23 min out / 55 total |
| Inbound legs Aug 6–18 window | 23 |
| Inbound legs Aug 19+ | 0 (expected — Grasshopper ended) |

**Extension mix (888 inbound):** Main 9 · Operator (0) 12 · Sales (1) 1 · Zoho Voice test (703) 1.

**Interpretation:**

- Real call volume on 888 in this window is **modest** — not hundreds of callers.
- **15 unique numbers** ≠ 15 employers; Cheyenne says most US calls are job seekers/solicitors — **classification still required**.
- **9 hangups** are recovery-review candidates (masked queue in `.local/phone-call-forensic/recovery-review-queue.csv`) — **not** approved for outreach.
- Export **does not** prove Aug 6 launch-day coverage (starts Aug 7).
- **Aug 19–24** requires open Zoho Voice CSV (Raffie zip still password-protected in Gmail).

---

## Stakeholder statements (use their words)

### Raffie (MANUAL — 24 Aug email)

- 888→323 forwarding began **19 Aug 2026**
- Before that: **Grasshopper** IVR + extensions; VM to respective emails
- Press 1 → Cheyenne → VM; alerts → **us@**
- Attached password-protected Voice zip + Grasshopper Detail zip; also sent **open CSV**
- Voice→CRM: known contacts can associate; **unknown callers need manual save**; Call Disposition for outcome; process **still in testing**

### Cheyenne (MANUAL — 24 Aug)

- Only **legitimate** calls logged manually to CRM
- **Most US calls = job seekers / solicitors**
- Callbacks from her **mobile**
- Spam/test usually **not** logged unless helpful for analysis
- Willing to log junk if helpful

### Holly (MANUAL — AU)

- AU sales ops owner; 1300 path; weekly email updates (separate from US thread)

### Ash (expected — not on thread yet)

- Owns CRM audit per `ads-launch/ASH_ZOHO_AUDIT_HANDOFF.md`
- George asked: PhoneBridge config for unknown callers, duplicate Lead prevention, offline conversion readiness

### Braden (expected)

- Ops ownership + backup owner for missed US calls — **not yet named**
- George asked to approve workflow before CRM automation

### Caitlin

- On maternity leave; introduced Cheyenne (US) and Holly (AU)

---

## What is still missing / who must move

| Gap | Owner | Status |
|-----|-------|--------|
| Ash: CRM workflow / PhoneBridge — should unknown callers create Enquiries? | **Ash** | No reply on thread |
| Braden: backup owner when Cheyenne doesn’t answer | **Braden** | Not named |
| Braden: approve any CRM workflow before build | **Braden** | — |
| Raffie: **open CSV** for Aug 19+ Zoho Voice (not password zip only) | **Raffie** | Partial |
| Raffie: confirm Aug 6 day + Jul–early Aug if zip password unavailable | **Raffie** | Open |
| Cheyenne: classify legitimate vs junk on log period; employer recovery candidates | **Cheyenne** | Manual process confirmed |
| Controlled weekday call test (Ads + Voice + CRM) | **George** (tracking QA only) | After ops confirm |
| Zoho offline conversion uploads | **Deferred** | Until records clean — Ash |

---

## Recovery / reactivation (NOT launched)

- **No** automated calls, emails, texts, or cadences.
- High-priority review = recent missed/VM + IVR 1 + no callback evidence + not junk/seeker/test.
- Older = max **one** human-approved attempt, then stop.
- Requires: Braden + Ash approval, dedupe, DNC check, Cheyenne/Holly classification.
- Private queue: `.local/phone-call-forensic/recovery-review-queue.csv` (gitignored, masked ANI).
- Grasshopper hangup rows populate queue for **human review only** — not permission to call.

**Outcome classes (required going forward):** Potential employer · Qualified employer · Forwarded to sales · Discovery completed · Existing client/support · Job seeker · Vendor/competitor · Spam · Test · Missed — callback completed/pending/none · Voicemail — callback completed/pending · Unknown.

**Rules:** Email notification ≠ follow-up. Call log ≠ CRM enquiry. Answered ≠ qualified employer.

---

## Smallest safe future-state SOP (recommendation only)

1. Every inbound call logged (Voice **and** CRM) with **real external ANI**.  
2. Known ANI matched to Contact/Account.  
3. Unknown new-client (IVR 1) → Sales Enquiry or explicit review queue.  
4. Every missed legitimate call → callback Task + owner.  
5. Callback within agreed SLA.  
6. Every call gets final disposition.  
7. Employers can advance Discovery → Job Order → Placement.  
8. Separate seekers / spam / tests / support.  
9. Named backup for unanswered sales calls (Braden to assign).  
10. Weekly unresolved-call review (Ash + sales).

**Do not implement CRM automation during this audit phase.**

---

## What George does NOT own

George owns **paid-media tracking QA only**:

- Microsite `tel:` / website-call format consistency
- Read-only reconciliation (Ads clicks vs telco logs vs CRM)
- Documenting gaps for Braden/Ash/Raffie/Cheyenne

George does **not** own:

- Telephone routing, IVR, or Zoho Voice configuration  
- CRM module design, PhoneBridge, Lead creation rules  
- Callback execution, sales disposition, or recovery outreach  
- Password zip decryption or Raffie’s telco admin  
- Hiring Cheyenne/Holly to change manual logging habits  

---

## FAQ (for ChatGPT / stakeholders)

**Q: Are the ~62 Ads events phone calls?**  
A: **No.** They are phone-**link** clicks (MANUAL). Grasshopper shows 23 inbound legs and 15 unique callers on 888 for 7–18 Aug — a different metric and window.

**Q: Does Zoho log every call to CRM?**  
A: **Partially.** Some Call stubs exist after 19 Aug, but Caller ID is often the 888 DID, not the caller. No auto Sales Enquiry.

**Q: How many employer leads did we miss?**  
A: **UNAVAILABLE** as a number. Need Cheyenne to classify Grasshopper/Voice logs + CRM gaps.

**Q: Is Cheyenne the problem?**  
A: **No** — she described manual logging by design. The issue is **system + process + integration**, not one person.

**Q: Should we turn on offline conversions now?**  
A: **No** — deferred until CRM call records are trustworthy (Ash).

**Q: What about Brand campaigns?**  
A: **Deferred** — Stage 1 is clean VC_* package; Brand is separate.

**Q: AU parity?**  
A: **UNAVAILABLE** this pass — low click volume; Holly owns APAC.

---

## ChatGPT prompt templates

### A) Email to Braden — decline live meeting, async summary

```
You are drafting email for George Aguilar to Braden Yuill (Virtual Coworker).

Facts only from the forensic brief — do not invent numbers.

Goal: Thank Braden; decline a live call today; show homework is done; ask for async/written follow-up; no blame; George = tracking QA only.

Include:
1. George fixed US microsite phone format vs Google call tag; ~62 events are link clicks, not proven calls.
2. Grasshopper CSV (7–18 Aug): 23 inbound legs, 15 unique callers, 14 forwarded, 9 hangups on 888.
3. Since 19 Aug Zoho Voice: CRM has partial Call stubs but Caller ID = 888, no Leads, no callback Tasks, empty dispositions.
4. Cheyenne manually logs legitimate calls only; most callers job seekers/solicitors (her words).
5. Still need: Ash CRM note, Braden backup owner name, Cheyenne classification pass.
6. George is not phone or CRM owner.

Tone: Professional, calm, already in motion. 150–250 words.
```

### B) Follow-up to Raffie — open Voice export

```
Draft email from George to Raffie Ramos (cc Ash, Braden, Cheyenne).

Thank for open Grasshopper CSV — processed: 23 inbound legs, 15 unique callers, 7–18 Aug on 888.

Request:
1. Same format open CSV for Zoho Voice Aug 19–24 (not password zip only).
2. Confirm whether Aug 6 launch day is missing from Grasshopper export or in password zip.
3. Confirm IVR field availability in Voice export for post-cutover reconciliation.

George read-only; not changing routing. Professional, short.
```

### C) Ask Ash — CRM configuration (no duplicate Leads)

```
Draft email from George to Ash (cc Braden).

Context: read-only audit shows Voice creates Call stubs with DID as caller, no Contact link, no Call_Result, no callback Tasks.

Ask Ash to confirm in writing:
1. Required PhoneBridge/CRM config so inbound stores real external ANI.
2. Whether unknown callers should create Sales Enquiries vs Tasks vs review queue.
3. Safeguards against duplicate Leads and job-seeker flood.
4. When offline conversion upload is safe.

George not implementing CRM changes. Neutral, technical.
```

### D) Executive one-pager (Braden / board-style)

```
Write a 200-word neutral executive summary:

- US ads phone clicks ≠ calls.
- Grasshopper 7–18 Aug: 15 unique callers, modest volume.
- Post-19 Aug CRM integration partial; not a pipeline.
- Gap: disposition, callback tasks, employer classification.
- Owners: Raffie telco, Ash CRM, Cheyenne/Holly sales ops, Braden ops approval.
- George: tracking fix only.

No alarmist language. No PII.
```

---

## Reference links & files

| Resource | Path / URL |
|----------|------------|
| Full forensic audit | `ads-launch/PHONE_CALL_CRM_FORENSIC_AUDIT.md` |
| This ChatGPT brief | `ads-launch/PHONE-CALL-FORENSIC-CHATGPT-BRIEF.md` |
| Live dashboard (aggregates) | https://vc-xray.vercel.app/phone-call-forensic |
| Launch Control checklist | https://vc-xray.vercel.app/launch-control#phone-lead-recovery |
| Phone number inventory | `ads-launch/phone-number-inventory.csv` |
| Reconciliation summary | `ads-launch/phone-call-reconciliation-summary.csv` |
| Grasshopper analyzer | `ads-launch/analyze_grasshopper_export_readonly.py` |
| Ash Zoho handoff | `ads-launch/ASH_ZOHO_AUDIT_HANDOFF.md` |

---

## Guardrails for ChatGPT

- Read-only context — no proposing CRM writes, routing changes, or outreach without Braden/Ash approval.  
- Do not treat email notifications as proof of callback.  
- Do not treat answered calls as qualified employers.  
- Do not combine phone-link clicks with unique callers or CRM leads.  
- Do not publish raw caller phone numbers or zip passwords.  
- Cheyenne = **US** (U.S. Update); Holly = **AU** — do not swap.  
- Executive page = neutral scoreboard; no “watch / may be paid” chips on live stakeholder views.

---

## Suggested one-liner for George (Braden async)

*“I’ve finished the read-only phone/CRM homework — Grasshopper shows 15 unique callers on 888 for 7–18 Aug, and CRM after the 19th still isn’t a real pipeline. I’m not the phone or CRM owner, so before we jump on a call I need Ash’s CRM note and your backup-owner call on the async thread; happy to send the written summary today.”*
