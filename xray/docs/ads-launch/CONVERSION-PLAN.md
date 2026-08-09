# Conversion plan — VC_US_* (prepare / don’t claim live)

**Status:** Prepared docs + microsite dataLayer. **Not** live Ads Primary yet.  
**Stay on Maximize Clicks** until phone routing works and call conversions are tested.  
**Do not** create conversions via Ads API. **Do not** attach legacy Zoho/Zapier actions.

---

## Measurement order

1. **Phone routing first** — Cheyenne answer path, missed-call owner, hours, E2E test (Raffie = IT; Ash ≠ owner).
2. **HIGH PRIORITY — Website calls 60+ seconds** — Ads conversion type “calls to a phone number on the website”; Google forwarding number swaps the site phone for Ads visitors; wire via GTM or site; **not** a `tel:` click. US 888 + AU 1300. No CallRail required. Test: ad → LP → forwarding # shows → connect 60+ sec → conversion in Ads.
3. **Calls from ads (60+ seconds)** — US live; AU still needed — early Primary alongside website duration.
4. **Form submit** — Secondary / observation only (fire after durable delivery).
5. **GTM + basic tags** — AU parity; needed for number replace / visit tracking (don’t deploy untested tags).
6. **Zoho Qualified lead offline** — after call duration wiring; then booked consult; value later when deals pay.

---

## Named Google Ads conversion actions (create in Ads UI)

| Name | Type | Duration | Count | Value | Goals |
|------|------|----------|-------|-------|-------|
| `VC_US_Phone_Call_From_Ads` | Calls from ads | 60–90s | One | None invented | Campaign-specific on `VC_US_*` only |
| `VC_US_Phone_Call_From_Website` | Calls from website | **60s** | One | None invented | Campaign-specific on `VC_US_*` only — **HIGH PRIORITY to finish** (Google forwarding + tag) |
| `VC_US_Employer_Form_Submit` | Website / GTM event | — | One | None | **Secondary** — not bidding Primary |
| AU website + ad-call actions | Create in AU Ads UI | **60s** | One | None invented | Don’t invent IDs in docs — name in Ads when creating |

**Hard rules**

- Do **not** attach old Zoho/Zapier / account legacy conversions to `VC_US_*`.
- `tel:` click (`phone_click` / `phone_cta_clicked`) = Secondary micro only — **never** Primary website-call win.
- Website wins = **connected call duration** via Google forwarding number (dynamic replace for Ads visitors).
- Don’t buy CallRail just for this Stage 1 signal.
- Don’t triple-count form + Calendly + Zoho Qualified as Primary for one enquiry.
- Public site numbers stay **888** (US) / **1300** (AU); Google replaces them for Ads visitors only — don’t hardcode a forwarding # as the public number.

### Ads UI steps (Calls) — George clicks

1. Google Ads → **Goals** / **Conversions** → **+ New conversion action**.
2. Choose **Phone calls** → **Calls from ads** → name `VC_US_Phone_Call_From_Ads` → set **Call length** **60s** → Count **One** → no value (or Leave blank). *(US: already created.)*
3. **HIGH PRIORITY:** **Calls from website** → `VC_US_Phone_Call_From_Website` (or confirm existing) → **60s** → implement Google website call tracking / forwarding number via GTM or site → test end-to-end. Repeat equivalent for AU (create names in Ads UI — don’t invent IDs here).
4. **Campaign settings** on `VC_US_S_CORE` + `VC_US_S_ROLES` → use **campaign-specific** conversion goals → include only the new `VC_US_*` actions (exclude account defaults / legacy). Same idea for AU when ready.
5. Leave Maximize Clicks. Do **not** switch to Max Conversions yet.

---

## Form (Secondary)

- dataLayer (live on microsite code when deployed): `employer_inquiry_submitted` + alias `form_submit_success` — only after durable delivery (Resend and/or GitHub).
- Ads action name when mapped: `VC_US_Employer_Form_Submit` — **Secondary**.
- Delivery today: Resend → `us@` / `apac@` (+ George CC) · GitHub Issues backup.

---

## GTM / GA4 / GSC

| Item | Status |
|------|--------|
| `NEXT_PUBLIC_GTM_US` / `NEXT_PUBLIC_GA4_US` | **Live** — `GTM-M92DX9BJ` → `G-2V3V0BS6JW` (`g/collect` 204 on `/us`) |
| dataLayer events | Code ready: `form_submit_success`, `phone_click`, `calendly_click` (+ canonical names) |
| GTM tags → Ads | **Do not deploy untested** |
| GSC `virtualcoworker.app` / `www` | George may need to Verify — checklist `ads24` |

---

## Zoho Qualified (quality / later)

- Discovery/mapping **next** — **no live CRM writes** until module, fields, and dupes confirmed.
- Future Ads quality signal: sales marks **Qualified** → offline / import to Ads with **GCLID**.
- Attribution fields to carry: `gclid`, `gbraid`, `wbraid`, `utm_*`, landing URL, referrer, market, category, variant, submission id, timestamp.
- Form payload already captures GCLID; Zoho `$gclid` mapping exists in code stubs — enable only after discovery.

---

## Negative keyword architecture (maintain; don’t mass-apply without George)

| Layer | Rule |
|-------|------|
| A. Job-seeker shared list | Controlled Phrase/Exact (`VC_Neg_JobSeekers_Live` in package — posting not prioritized tonight) |
| B. Observed-query Exact | Exact negatives of bad queries from ST review — **not** broad `workers` / remote / VA |
| C. Shared strategic | Reviewed exclusions only — don’t guess |
| D. Role-specific | Don’t contaminate other roles |

**DoD for “Build and maintain negative keyword lists”:** lists exist and are labeled; bare Broad `workers` absent (builder asserts); Exact-query negs for ambiguous ST junk; no mass-post without George.

---

## Safety

No mass-pause KW/RSA · no budget/bid change · no Brand · no AU Enable · no broad workers/remote · no legacy conv attach · no Ads API mutate · no token exposure.
