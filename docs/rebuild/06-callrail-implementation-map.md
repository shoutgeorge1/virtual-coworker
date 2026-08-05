# 06 — CallRail implementation map

**Status:** Spec only — **do not activate** CallRail in production until launch checklist says so.  
**Unknown until VC provides:** existing CallRail account?, numbers, company ID, swap vs DNI preference.

---

## Purpose

Phone is a first-class employer conversion next to form. Calls must be attributable to Google Ads Search and must not mix job-seeker or WP sitewide noise into the paid pilot pool.

---

## Number map

| Market | Pool | Where swapped | Forward to |
|--------|------|---------------|------------|
| USA | 1 tracking number (or small pool) | Canonical US paid LP only | VC US sales DID (Braden provides) |
| AU | 1 tracking number (or small pool) | Canonical AU paid LP only | VC AU sales DID |

**Do not** put paid tracking numbers on WordPress global header during v1 (avoids contaminating Ads call conv with organic/job traffic).  
Optional later: separate WP pools with separate Ads conversion actions.

---

## Event hierarchy (calls)

| Priority | Event | Ads action name | Include in “Conversions” at Stage 1? | Include Stage 3+? |
|----------|-------|-----------------|--------------------------------------|-------------------|
| 1 (observe) | Qualified connected call ≥60s (or VC threshold) | `call_qualified_employer` | No (observe) | Yes when volume + QA OK |
| 2 (observe) | Call from paid LP / Google click | `call_click_to_call` or CallRail Google Ads auto | No | Maybe as secondary |
| 3 (diag) | Call started / missed | GA4 only | No | No |
| Never | Job-seeker / spam flagged calls | — | Never | Never |

**Stage 1–2 bidding:** Maximize Clicks — call actions **observation only**.  
**Stage 3:** Add qualified calls into primary Conversions with form employer leads.

---

## CallRail → destinations

| Destination | Payload / behavior |
|-------------|-------------------|
| Google Ads | Native CallRail Google Ads integration **or** GTM phone events — pick one primary to avoid double-count |
| GA4 | `call_click`, `call_connected`, `call_qualified` via GTM |
| Zoho | Only if call is marked sales-qualified; create/update Lead with `lead_source=google_ads_call` — **not** auto-create on every 2s pocket-dial |
| Slack/email | Optional notify Braden on qualified call |

---

## Configuration checklist (when activating)

1. Company + US/AU numbers created  
2. Keyword spotting: job, salary, apply → tag `jobseeker_suspected`  
3. Min duration threshold agreed (default proposal: **60 seconds**)  
4. Recording on (counsel/privacy OK — Braden)  
5. Whisper/greeting: “Virtual Coworker — employer line” optional  
6. Source: Google Ads campaigns tagged via GCLID capture / CallRail integration  
7. Exclude internal test numbers  
8. Double-counting audit: form booked + call same session → one primary conv rule documented  

---

## Owner / access

| Role | Who |
|------|-----|
| Provide DIDs + CallRail seat | Braden / VC |
| Configure swap on paid LP | George |
| QA first 10 calls | Braden + George |
| Kill switch | George can remove swap snippet without touching WP |

**Do not** activate until LP thank-you + form events already pass Tag Assistant.
