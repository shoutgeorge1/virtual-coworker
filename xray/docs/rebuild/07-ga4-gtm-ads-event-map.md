# 07 — GA4 / GTM / Ads event map

**Controlled launch hierarchy.** Stage 1 bids on clicks; conversions are wired for **observation** first.  
**Do not** mutate VC’s existing WP GTM containers for this pilot unless Braden explicitly asks later.

---

## Containers (target state)

| Layer | Spec |
|-------|------|
| Paid host GTM | New George-controlled container (or reclaim try.* `GTM-KSMWT6QM` if Option B LP) |
| GA4 | Pilot property (or clear market streams) — ID TBD |
| Google Ads | USA + AU accounts each get tag + conversion actions |
| WP GTM-TTKNKT / GTM-KNDLKVW | Leave alone for v1 |

---

## dataLayer contract (paid LP)

```js
dataLayer.push({
  event: "gate_answer",
  intent: "hire" | "job",
  gate_variant: "inline" | "quiz" | "modal",
  market: "US" | "AU"
});

dataLayer.push({
  event: "employer_form_start",
  market: "US" | "AU",
  gate_variant: "...",
  role: "..."
});

dataLayer.push({
  event: "employer_form_submit",
  market: "US" | "AU",
  gate_variant: "...",
  role: "...",
  company_size: "..."
});

dataLayer.push({
  event: "employer_lead",          // thank-you only, hire path
  market: "US" | "AU",
  lead_id: "..."                   // server id if available
});

dataLayer.push({
  event: "jobseeker_path",         // analytics only — NEVER Ads primary
  market: "US" | "AU",
  gate_variant: "..."
});

dataLayer.push({
  event: "call_click",
  market: "US" | "AU"
});
```

---

## Event → GA4 → Ads mapping

| Event | GA4 event name | Ads conversion action | Category | Counting | Primary “Conversions” Stage 1 | Stage 3 | Notes |
|-------|----------------|----------------------|----------|----------|-------------------------------|---------|-------|
| Page view LP | `page_view` | — | — | — | — | — | Engagement diagnostics |
| Gate hire | `gate_answer` (+param) | — | — | — | No | No | Funnel only |
| Gate job | `jobseeker_path` | — | — | — | **Never** | **Never** | No Zoho sales |
| Form start | `form_start` / `employer_form_start` | `employer_form_start` optional | Other | One | No | No | Micro |
| Form submit success | `generate_lead` / `employer_lead` | **`employer_lead_form`** | Submit lead form | One | **Observe only** | **Yes primary** | Thank-you or server confirm |
| Call click | `call_click` | `call_click` | Other | One | No | Secondary | |
| Call qualified | via CallRail | **`employer_lead_call`** | Phone call lead | One | Observe | **Yes primary** | Duration rule |
| Calendly book (if kept) | `calendar_booked` | `employer_calendly` | Other | One | Observe | Maybe | Prefer consolidating into form lead |
| Zoho qualified | offline import | **`zoho_qualified_lead`** | Qualified lead | One | No | Stage 4 prep | After CRM loop |
| Zoho opp/customer | offline | `zoho_opportunity` / `zoho_customer` | … | One | No | Stage 4 values | Later |

---

## Ads conversion settings (create before launch, bid later)

For each account (US + AU):

1. Create `employer_lead_form` — **Include in Conversions = OFF** at Stage 1  
2. Create `employer_lead_call` — Include OFF  
3. Create diagnostics as secondary goals / observe  
4. Account default goal: do **not** let legacy agency actions remain primary — audit & exclude (needs conversion export)  
5. Enhanced conversions: ON when email/phone hashed consent path ready  
6. Conversion linker: all paid pages  

---

## Hierarchy for controlled launch (read top-down)

```
DIAGNOSTICS (always on)
  CTR · search terms · CPC · GA4 engaged sessions · form funnel · manual lead QA

STAGE 1 BID SIGNAL
  Maximize Clicks only
  (conversions recorded but not used for bidding)

STAGE 2 TRUST BUILD
  Same bidding; weekly human accept/reject → contamination % 

STAGE 3 PRIMARY CONVERSIONS
  employer_lead_form + employer_lead_call (qualified)
  → only then Max Conv / tCPA consideration

STAGE 4 VALUE
  zoho_qualified / opp / customer values → value bidding
```

---

## Verification protocol (no spend)

1. GTM Preview on LP  
2. Tag Assistant (Ads)  
3. Submit **hire** test → Ads → Conversions shows 1 in Diagnostics / recent  
4. Submit **job** test → Ads employer actions **do not** increment  
5. Confirm no double-fire (GTM + Formspree + Calendly)  

**Owner:** George · **Blocker if fail:** do not enable campaigns
