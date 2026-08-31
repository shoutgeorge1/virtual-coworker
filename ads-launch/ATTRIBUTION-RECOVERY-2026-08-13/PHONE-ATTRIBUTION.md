# Phone attribution — 13 August 2026

A telephone call does **not** naturally carry a Google click id. Treat every layer as a different object.

---

## The ladder (do not collapse)

| Step | What it is | What it is not |
|------|------------|----------------|
| Phone-number click | Someone tapped `tel:` | Not a conversation |
| Call connected | The line rang and someone picked up | Not 60 seconds |
| Call lasting 60 seconds | Google’s duration rule on a forwarding / ad-call action | Not a qualified employer |
| Qualified employer conversation | A human says this caller is a real hiring company | Not a Zoho enquiry until logged |
| Sales enquiry | A row in Sales Enquiries | Not a job order |
| Job order | A recruiting request | Not a placement |
| Placement | A hire in ops | Not the ad click |

---

## Current paths

| Path | US | AU | Attribution to the ad / keyword | In Zoho? |
|------|----|----|----------------------------------|----------|
| **Call asset on Search** | Live. Public number **888-964-8644**. Asset `49435983302`. 10 Aug probe also showed **310-730-9126** still ENABLED on CORE/ROLES — later restore may have changed this (**UNKNOWN now**). | Live **1300 886 740** | Google “calls from ads” if the action exists | Only if someone types an enquiry |
| **Calls from ads 60s** | `VC_US_Phone_Call_From_Ads` id `7713239223` · Primary · **0** in 2y window | **Missing** on 13 Aug inventory | Campaign / ad, not landing page | No automatic join |
| **Website 60s + Google forwarding** | `VC_US_Phone_Call_From_Website` id `7716194324` · GTM label `Sf71CJSQr98cEOPyhMsD` · **0** conv. Test: visible number stayed 888 without a real ad-click cookie | **Missing** (#16) | Session-ish via forwarding cookie. Fake `?gclid=test` did not swap | No |
| **Website click-to-call** | `VC_US_Phone_Click_Website` · 0 conv / 2 all-conv | `VC_AU_Phone_Click_Website` (GA4 type on disk) | Shallow | No |
| **Static number, no swap** | Anyone can call 888 from a billboard, email, or organic page | Same for 1300 | **None** | Manual |
| **CallRail** | **Not in repo, not in Zoho modules** | Same | — | — |
| **Zoho Voice / telephony** | Not found. Sinch SMS is installed (text, not voice attribution) | Same | — | — |
| **Zoho Calls module** | **379 calls in 90 days** — sales does log calls. Duration fields exist. **No gclid / campaign fields** | Included in the 379 | **None** | The log itself |
| **Missed calls / voicemail** | **UNKNOWN** who owns the tree | **UNKNOWN** | — | — |
| **Callers → Sales Enquiries** | Cheyenne has logged source = Phone (7 in 90d). Not proven to be the Ads line | **UNKNOWN** | Lost unless typed | Sometimes |

Public numbers to keep: **US 888-964-8644** · **AU 1300 886 740**. Never publish 888-864, 888-954, or 310 as the public line.

---

## Option comparison (later — do not purchase from this memo)

| Option | Ad / session | Keyword / LP | DNI | US+AU | Recording | 60s rule | Spam / job-seeker | Zoho | Offline return | Cost / burden | Fit for this pilot |
|--------|--------------|--------------|-----|-------|-----------|----------|-------------------|------|----------------|---------------|--------------------|
| **1. Google calls from ads** | Strong for the asset | Campaign/ad, not LP | n/a | US live; AU action missing | No | Yes | Weak | Manual | Native Ads | Free | **Pilot minimum for ad-button calls** |
| **2. Google website-call + forwarding** | Strong if the number swaps | Better than static | Google swap | US tag live, 0 conv; AU not wired | No | Yes | Weak | Manual | Native Ads | Free | **Pilot minimum for LP calls** |
| **3. CallRail DNI** | Strong | Strong | Yes | Yes if bought | Yes, extra legal | Yes | Better classification | Possible later | Possible | Paid + ops | **Later**, ~1–2 months per existing lock — not now |
| **4. Zoho Voice / supported telephony** | Weak unless they pass gclid | Weak | Unlikely | Maybe | Maybe | Maybe | CRM-native disposition | Native log | Still need click id | Unknown | Not evidenced as installed |
| **5. Static numbers + manual disposition** | None | None | No | Yes | If the phone system does | Human | Depends on Cheyenne/Holly | Already happening (379 calls) | No | Cheap, blind | What organic/direct callers already are |
| **6. Other company platform** | **UNKNOWN** | — | — | — | — | — | — | Sinch is SMS | — | — | Ask Cheyenne what they actually answer |

---

## Minimum viable for the current pilot

Keep Maximize Clicks.

1. Leave US 60s ad-call and US 60s website-call as pipe checks. Confirm in the Ads UI that a **real** ad click swaps the number and that a 60+ second call appears. 0 conversions so far means “not proven,” not “broken.”
2. Add the AU twins in the Ads UI when George is ready (#16 / #17). Same public 1300. No GTM required for ad-call.
3. Do **not** treat tel: taps as quality.
4. Ask Cheyenne/Holly who answers, who gets missed calls, and whether they create a Sales Enquiry after a useful call.
5. Do **not** buy CallRail this week. Do **not** make Zoho Calls a Google conversion — there is no click id on those rows.

## Later, more complete

CallRail (or equivalent) dynamic numbers **after** the form pipe and a named Zoho outcome exist — so you can mark spam/job-seeker and send a **Secondary** qualified-call or qualified-job-order back to Google. Recording/transcripts need a privacy decision first. Still never a second Primary for the same inquiry.
