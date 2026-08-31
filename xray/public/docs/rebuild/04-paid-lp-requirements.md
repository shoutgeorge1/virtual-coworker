# 04 — Paid landing page requirements

**One canonical paid LP per market.** Ads Final URL + sitelinks must not spray WordPress.

---

## Recommendation (decision still required)

| Option | Status | Verdict for v1 paid |
|--------|--------|---------------------|
| **A. George-controlled microsite** (e.g. vision / Next on Vercel) | Pilot concepts already exist (`vision-three-alpha.vercel.app/us` · `/au`) | **Preferred** — full event control, employer gate experiments, no WP dual-door |
| **B. `try.virtualcoworker.com/{us\|apac}`** | Live Next + Formspree + Calendly · GTM-KSMWT6QM · thank-you **404** | Acceptable only if thank-you + Ads events fixed before spend |
| **C. WP `/contact-us/`** | Gravity Forms exist | **Reject for paid** — dual-door chrome, wrong primary historical spray target |

**Open decision for George + Braden:** A vs B. Do not run both as competing Final URLs in the same campaign.

---

## Canonical URLs (placeholders until decision)

| Market | Canonical paid URL | Notes |
|--------|-------------------|-------|
| USA | `https://{paid-host}/us` | Single host; https; no www split |
| AU | `https://{paid-host}/au` | Use `/au` consistently (prefer over `/apac` for clarity) |

If keeping try.*: US=`/us`, AU=`/apac` **or** add `/au` redirect — pick one AU path and stick to it.

---

## Must-have requirements (both markets)

### 1. Positioning

- Employer / hire offshore staff only above the fold  
- Clear market cue (US or AU)  
- No careers / “Looking for a Job?” / `.ph` links in nav, footer, thank-you, or sticky bars  
- Job-seeker path, if any, is a **separate non-Ads conversion** dead-end (see gate plan)

### 2. Form (employer)

| Field | Required |
|-------|----------|
| First name · Last name | Yes |
| Work email | Yes (block freemail optionally later) |
| Phone | Yes |
| Company | Yes |
| Country / market | Pre-filled from LP |
| Role / need | Yes (select) |
| Company size or headcount band | Yes |
| Timeline | Yes |
| Message | Optional |
| Hidden: utm_* · gclid · gbraid/wbraid · landing_url · gate_variant · employer_confirmed | Yes |

**Consent:** Privacy link + processing consent checkbox if AU/US counsel requires.

### 3. Phone

- Visible Click-to-call with **CallRail** swap number for that market  
- No raw corporate number on paid LP once CallRail is live  
- `tel:` clicks fire GA4 + Ads secondary events (see maps)

### 4. Thank-you / success

- Dedicated URL **200** (not 404): `/{market}/thank-you`  
- Fire Ads `generate_lead` / `employer_lead` **only** on employer success  
- No Calendly-only success without a measurable page or dataLayer event  
- No `.ph` dual-door on thank-you

### 5. Tracking containers

| Need | Spec |
|------|------|
| GTM | One George-controlled container on paid host (temp OK) |
| GA4 | One property or clear market property — document ID |
| Google Ads tag | `AW-` present via GTM; conversion linker on |
| Do not depend on | WP GTM-TTKNKT / GTM-KNDLKVW for pilot conversions |

### 6. SEO / ads hygiene

- `noindex,nofollow` OK for pure paid LP  
- Fast LCP on mobile  
- Single primary CTA  
- Proof (logos/years) allowed below fold — no card soup that dilutes CTA

### 7. Spam controls (page layer)

- Honeypot field  
- Time-to-submit minimum  
- Server-side validation  
- Optional Turnstile/hCaptcha after abuse appears  
- Bot path must not create Zoho sales lead

### 8. Ad → LP consistency

| Ad theme | LP behavior |
|----------|-------------|
| Brand | Same LP; brand-safe H1 |
| Core hire VA | H1/subcopy mention Filipino / offshore VA hiring |
| Role | `?role=` preselects role field; headline can soft-match |

---

## Explicit non-requirements (v1)

- Full WP redesign  
- Blog / SEO farm  
- Multi-step sitewide nav  
- Shopify / PH careers integration on paid host  

---

## Acceptance tests before spend

1. Tag Assistant: Ads tag + conversion linker on LP + thank-you  
2. Submit employer test lead → thank-you 200 → Ads test conversion (include in observations, not bidding)  
3. Job-seeker path test → **zero** employer Ads conversion · **zero** Zoho sales lead  
4. CallRail test call from mobile → recording + sourced to Google Ads  
5. No `.ph` link in view-source on paid templates  
6. Final URL in Ads Editor preview = canonical only  

**Owners:** George (build/tags) · Braden (copy claims / phone numbers / privacy OK)
