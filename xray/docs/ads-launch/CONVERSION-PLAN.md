# Conversion plan — VC_US_* (prepare / don’t claim live)

**Status:** Prepared docs + microsite dataLayer. **Not** live Ads Primary yet.  
**Stay on Maximize Clicks** until phone routing works and call conversions are tested.  
**Do not** create conversions via Ads API. **Do not** attach legacy Zoho/Zapier actions.

---

## Measurement order

1. **Phone routing first** — Cheyenne answer path, missed-call owner, hours, E2E test (Raffie = IT; Ash ≠ owner).
2. **Phone call conversions** — first meaningful Primary **after** routing works (60–90s).
3. **Form submit** — Secondary / observation only (fire after durable delivery).
4. **GTM + basic call tracking** — paste container IDs; map events; website-calls via GTM number replace when ready (don’t deploy untested tags).
5. **Zoho Qualified lead offline** — discovery/mapping next; quality signal after immediate setup is stable.

---

## Named Google Ads conversion actions (create in Ads UI)

| Name | Type | Duration | Count | Value | Goals |
|------|------|----------|-------|-------|-------|
| `VC_US_Phone_Call_From_Ads` | Calls from ads | 60–90s | One | None invented | Campaign-specific on `VC_US_*` only |
| `VC_US_Phone_Call_From_Website` | Calls from website | 60–90s | One | None invented | Campaign-specific on `VC_US_*` only |
| `VC_US_Employer_Form_Submit` | Website / GTM event | — | One | None | **Secondary** — not bidding Primary |

**Hard rules**

- Do **not** attach old Zoho/Zapier / account legacy conversions to `VC_US_*`.
- `tel:` click (`phone_click` / `phone_cta_clicked`) = Secondary micro only — not a qualified call.
- Don’t triple-count form + Calendly + Zoho Qualified as Primary for one enquiry.
- Public LP number stays `310-426-8776` until GTM call-tracking replace is tested — don’t hardcode a forwarding # as the public number.

### Ads UI steps (Calls) — George clicks

1. Google Ads → **Goals** / **Conversions** → **+ New conversion action**.
2. Choose **Phone calls** → **Calls from ads** → name `VC_US_Phone_Call_From_Ads` → set **Call length** 60–90s → Count **One** → no value (or Leave blank).
3. Repeat for **Calls from website** → name `VC_US_Phone_Call_From_Website` (website path needs GTM / Google forwarding number later — prepare, don’t claim live).
4. **Campaign settings** on `VC_US_S_CORE` + `VC_US_S_ROLES` → use **campaign-specific** conversion goals → include only the new `VC_US_*` actions (exclude account defaults / legacy).
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
| `NEXT_PUBLIC_GTM_US` / `NEXT_PUBLIC_GA4_US` | **Empty** — paste IDs in Vercel vision env, redeploy |
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
