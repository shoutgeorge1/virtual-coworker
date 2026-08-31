# Employer LP simplification plan — US / AU

**Date:** 2026-08-11 (updated: light-theme decision + Phase 0 locked)  
**Status:** Phase 0 decided — **implementing** (chips off).  
**Surfaces:** `https://www.virtualcoworker.app/us` · `/au` (shared `MarketLanding`)  
**Goal:** One clear hiring message + a simple form + phone. Park everything else for secondary / deeper LPs.  
**Visual (locked):** Simplified paid LPs use the **AU light theme** for **both** US and AU — mist/foam backgrounds, existing AU typography/color language. Do **not** keep US dark navy on the simplified money LP. Dark US chrome is optional later for non-paid / secondary pages only if George asks.

---

## Visual direction — AU light for US + AU (v1)

Competitors (MyOutDesk, Wing, Magic) read as **light, airy, premium**. Live `/au` already matches that better than dark `/us`. George’s call: lean into AU light on the simplified LP, including US paid traffic.

### Decision

| Surface | v1 simplified look |
|---|---|
| `/au` (form LP) | Keep AU light (already default) |
| `/us` (form LP) | **Same AU light shell** — not dark navy |
| Copy / phone / market labels | Still US vs AU voiced (CTA wording, hours, phone format) — only the **chrome** unifies |
| Dark US theme | **Park** on paid CORE LPs. Optional later revive only if George wants a dark variant |

### How it works in code today (for implementers later)

`MarketLanding` currently forks look with market:

```ts
const shell = market === "us" ? "us" : "au";
const light = market === "au";
```

That drives `SiteNav`/`SiteFooter` tone, hero veil (`us-hero-bg` vs `au-hero-veil`), and `light` props on bands. For simplified v1: **force light shell on both markets** (e.g. always AU layout classes + `light = true` for the paid form LP, while `market` stays `us`|`au` for copy, phone, tracking). Prefer reusing AU tokens over inventing a third palette.

### Reuse (AU light stack)

| Asset | Role |
|---|---|
| `vision/app/au/au.css` | Canonical light LP: `.au` tokens (`--mist`, `--foam`, `--ocean`, `--ink`, `--gold`, `--cyan`), `.au-hero` / `.au-hero-veil`, light sticky nav, light sell sections |
| `globals.css` → `.micro-light` | Same mist/daylight system on hub pages (how-it-works, thank-you AU). Pattern reference — paid LP should feel like `/au` home |
| Component `light` props | `TrustBand`, `PressBand`, `FaqAccordion`, `StopCloser`, `RoleQuiz`, `sell-grid-light`, `trust-row-light`, `industry-band-light` — already light-aware |
| `SiteNav` / `SiteFooter` `tone="light"` | Mist nav + light footer — use on US simplified LP too |
| Light badge assets | e.g. Forbes navy badge path already branched when `light` |

### Park (dark-US-only chrome on simplified paid LP)

| Asset | Why park |
|---|---|
| `vision/app/us/us.css` dark shell (`.us` `--deep` navy page, dark nav, dark sell) | Competitor-opposite; heavier than simplified goal |
| `.us-hero-bg` (dark hero wash) | Replace with `.au-hero-veil` (or shared light veil) on simplified US |
| Dark `SiteNav` / `SiteFooter` on `/us` money LP | Use light tone instead |
| Dark trust-chip / Forbes-white variants on that LP | Prefer light-row treatment |
| Dual visual systems on CORE Final URLs | Extra cognitive load; consolidates with competitor pattern |

**Do not delete `us.css`.** Keep dark US available for secondary surfaces or a later optional variant. Just don’t mount it on simplified `/us` paid LP v1.

### What does *not* change with the light decision

- Market copy (US punchy vs AU understated)  
- Phone numbers, GTM/GA4, thank-you routes  
- Form simplify + section park (below)  
- No full redesign — restyle shell + cut sections; don’t invent a new brand system  

---

## Competitor sources (CEO meeting brief)

From George’s **Post-CEO Meeting** mega prompt ([transcript](485a85cf-1ab0-4c80-87d4-bda816ffd6c6) context; full brief in [cea59e5f…](cea59e5f-b49f-47b6-a8e0-ff24596164c2)):

| Competitor | URL | Why it matters |
|---|---|---|
| **MyOutDesk** (primary CEO cite) | https://www.myoutdesk.com/ | White-glove managed staffing benchmark. Light hero → one CTA. |
| Wing Assistant | https://wingassistant.com/ | Clean managed-VA positioning; consultation CTA. |
| Magic / Get Magic | https://getmagic.com/ | Sparse; solo-op friendly — **pattern reference only**, not VC ICP. |

Also logged in `xray/data/growth-os.js` → `competitors` (MyOutDesk = “CEO-cited white-glove benchmark”).

### Pattern that matters (not clone)

**MyOutDesk signup** (`/signup/`): **Full name · Business email · Company · Phone** — then book. No role-chip quiz. No company-size chip bank on the form. Qual happens on the call.

**Homepage hero:** short headline, short bullets, one CTA (“Book a Free Strategy Call”), proof near CTA, lots of white space. Long proof/industry content lives *below* or on other pages — not competing with the form.

**What they leave out of the conversion moment:** mid-page quizzes, multi-step chip interrogations, industry research grids, competing CTAs.

Chrome tabs opened for review: MyOutDesk · Wing · VC `/us` · VC `/au`.

---

## What’s wrong on live VC today

Same component for US + AU (`MarketLanding.tsx`), but **two visual shells**: dark US (`us.css`) vs light AU (`au.css`). Headline is already good (“Hire Dedicated Virtual Assistants from the Philippines”). The page is overbuilt around it — and US dark fights the competitor light pattern.

### Form feels like a quiz (`LeadGate`)

Numbered steps the employer sees:

1. Hire vs job-seeker (gate)
2. Role chips (many)
3. **About the hire** — company size + positions + FT/PT (three chip rows)
4. Name / email / phone / company
5. Plus phone call block

That’s ~4 UI stages before submit. MyOutDesk does **4 text fields**. CEO still wants ICP signal (5–10 seats / established company) — but that can move to the consult / scoring later, not the first paint of the form.

### Page has too many jobs

Current order after hero form:

1. PressBand  
2. Industry stats (Deloitte / research cards)  
3. PainGain  
4. RoleOutcomes (category only)  
5. How hiring works (4 sell-cards)  
6. TrustBand  
7. **RoleQuiz** (another 3-step quiz on the same page)  
8. Long FAQ  
9. StopCloser  
10. StickyCta + EngageChat  

`lp_density` lean arm only hides some *copy* (`data-lp="secondary"`). It does **not** remove quiz / pain / industry / FAQ / stop-closer. So “lean” still feels heavy.

---

## v1 simplified LP — what stays

Keep infrastructure. Cut noise. One employer journey. **Light AU chrome on both markets.**

| Keep | Why |
|---|---|
| **AU light visual shell** (US + AU) | Matches competitor light pattern; George preference |
| Hero H1 + short sub | Already matches CEO direction; spell out “virtual assistant” |
| 3–4 benefit ticks | Dedicated · your hours · we handle recruit/payroll · since 2011 |
| Minimal trust near form | Google rating + Clutch (or one row). Drop the crowded chip strip if it fights the form |
| **Simple LeadGate** | Contact fields + phone option (see form plan below) |
| Job-seeker divert | Keep purity — but lighter UX (see form) |
| Phone — quiet secondary | Prefer to talk? link under form + footer. Not hero CTA; not co-equal sticky weight |
| Short “how it works” (4 steps **or** one paragraph + link to `/how-it-works`) | White-glove story without a second product tour |
| Thin trust strip | 1–2 review quotes **or** client logos — not both full bands |
| Nav + footer | Thin **light** tone; don’t add portals |
| Tracking / thank-you / GTM / phone click | Do not break |

**Primary CTA copy:** “Book a Free Strategy Call” (US) / “Book a free strategy call” (AU) — MyOutDesk energy; not “demo.”  
**CTA hierarchy (locked 2026-08-11 after competitor review):** form / book strategy call is primary → thank-you / calendar. Phone is quiet secondary only (“Prefer to talk?” under form, footer, small sticky text) — never hero CTA and never equal visual weight to the form.

---

## Park for later / secondary LPs

Do **not** delete components — stop mounting them on default `/us` + `/au` (and probably generic market home). Reuse on deeper pages when needed.

| Park | Reuse later on |
|---|---|
| Mid-page `RoleQuiz` | Keep `/us/quiz` · `/au/quiz` (ads paused). Not on CORE form LP |
| Industry stats band | Cost / research / lead-magnet LP |
| `PainGain` long before/after | Role or pain-intent LPs |
| Full FAQ accordion (10+) | `/how-it-works`, role LPs, or collapsed “3 FAQs” max |
| `StopCloser` variants | Secondary closer pages / brand |
| Heavy PressBand + full TrustBand together | About / trust page; pick one proof band for v1 |
| `QuizTeaser` / exit popup remount | Stay off until conversion volume exists |
| Cost calculator / readiness score (CRO backlog) | After simplify ships and form CVR is stable |
| Extra hero portals (services browse in hero, rate essay) | Below-fold one line or `/services` |
| **Dark US shell (`us.css` on money LP)** | Optional later variant / non-paid surfaces only if George asks |

Role category LPs (`/us/[category]`) can stay slightly richer than the generic home — but still inherit the **simple form** + **light shell**.

---

## Form simplification (less quiz)

**Target feel:** MyOutDesk signup — fill and submit in under a minute.

### Recommended v1 form (default `/us` · `/au`)

1. **Job-seeker filter (keep, lighten)**  
   - Option A (preferred): one line under title — “Hiring for a business? Continue. Looking for a job? → careers” (link divert, no step 1 wall).  
   - Option B: keep hire/job buttons but **don’t number it as “1” of a quiz**.

2. **Role** — single optional select or short chip row (pre-filled on category LPs). Required for routing is fine; don’t look like a survey.

3. **Contact (required)** — Name · Work email · Phone · Company. Same as MyOutDesk.

4. **Phone CTA** — quiet secondary only (“Prefer to talk?” + number). Not an “or” equal block; not sticky co-hero.

5. **Qualify chips (company size / seats / FT-PT)** — **remove from default form for v1.**  
   - Still collect on consult / Holly loop / optional “one more question” after submit if we need scoring.  
   - Keep `lead-value.ts` scoring tolerant of missing size/seats (already has defaults path — verify before ship).  
   - CEO ICP (5–10 seats) is a **sales filter**, not a homepage interrogation.

### Explicitly do not do in v1

- Add hiring timeline chips to the live form  
- Merge RoleQuiz into the hero form  
- Another multi-step wizard “to improve completion”

---

## Suggested section order

**Frame:** mist/foam light page (AU language) for both markets — calm light nav, light hero veil, form card readable on white/foam.

### First viewport (above the fold)

1. Thin **light** nav  
2. Kicker: US/AU · Employers · Philippines staffing  
3. **H1** — Hire dedicated virtual assistants from the Philippines  
4. One short sub  
5. 3–4 ticks  
6. **Form card** (simple) + phone  
7. Tiny proof under form (stars / years) — not five trust chips

Hero image: keep if it doesn’t shove the form below the fold on desktop; on mobile form must win.

### Below the fold (short)

1. Optional: one-line press / “As featured in”  
2. How hiring works — **one** compact strip (4 steps) **or** paragraph + link  
3. 1–2 testimonials **or** logo row (pick one)  
4. Footer  

**Hard cap:** no second quiz, no industry research grid, no StopCloser essay, no long FAQ on the money LP.

---

## Risks

| Risk | Mitigation |
|---|---|
| **Experiments** — `lp_density`, `quiz_copy`, `gate_headline`, `role_imagery` | Consolidating is what the CEO brief asked for. Make **lean = new control** (or force lean + unmount parked sections). Pause / freeze low-volume arms rather than adding more. Update `SITE-EXPERIMENTS.md`. |
| **Lead scoring / Zoho** — size & seats drop | Confirm API + `scoreLeadFromSignals` OK with blanks; Holly can ask on call. Don’t invent fake defaults that inflate Ads value. |
| **Job-seeker leak** | Keep divert path + API reject. Soft link is fine if careers exit still uses `replace`. |
| **SEO / FAQ JSON-LD** | Keep FAQ schema via `/how-it-works` or a short 3-question block if we strip the accordion. Don’t orphan breadcrumb/org JSON-LD. |
| **Quiz ads** | `VC_*_S_QUIZ` already paused; quiz routes stay for later. Don’t retarget CORE Final URLs to quiz. |
| **US dark → light switch** | Paid `/us` will look like `/au` chrome. Accept for v1; dark US stays in `us.css` if needed later. Smoke mobile contrast (ink on mist, gold CTAs). |
| **Shared shell / class reuse** | Prefer forcing AU light classes + `light={true}` on US form LP over a third theme. Watch CSS specificity if `.us` and `.au` ever nest. |
| **Tracking** | Same `#gate`, thank-you, phone labels, `employer_inquiry_submitted`. Smoke-test after unmount. |

---

## Phased ship order (when George says go)

### Phase 0 — decided (2026-08-11)

- **Qualify chips:** **OFF** on default form (size / seats / FT-PT). Match MyOutDesk — contact fields + phone; qual on the consult.  
- **Mid-page quiz:** unmount from form LPs (keep `/us/quiz` · `/au/quiz`).  
- **Visual:** AU light for US + AU simplified paid LPs (locked earlier).  
- **CTA language:** “Book a Free Strategy Call” / “Book a free strategy call” (MyOutDesk energy) — not “demo.”  
- **CTA hierarchy:** form/book primary; phone quiet secondary only (competitors do not hero phone).

### Phase 1 — cut page weight + unify light shell (half–1 day)

- Unmount from default `MarketLanding` (form surface): `RoleQuiz`, industry band, `PainGain`, long FAQ, `StopCloser` (or replace StopCloser with a one-line closer).  
- Collapse trust: one band only.  
- Force or retire `lp_density` so control = lean page.  
- **US + AU same structure and same AU light chrome** (`light=true`, AU hero veil / mist page, light nav/footer). Keep market-specific copy + phone.  
- Park dark `.us` shell on this surface only — do not delete `us.css`.

### Phase 2 — simplify form (half day)

- Drop size / seats / schedule chip banks from default LeadGate.  
- Lighten intent step.  
- Keep phone block + formatting.  
- Update tests (`lead-validation`, public-copy lint, gate snapshots if any).

### Phase 3 — polish (optional same sprint)

- Hero trust-chip diet on the light shell.  
- Contrast/QA pass on light US (badges, gate card, sticky CTA).  
- Smoke: form submit → thank-you · phone click · job-seeker divert · GTM events.

### Phase 4 — later LPs (not now)

- Reattach quiz / pain / stats / FAQ on role, cost, or quiz URLs (can stay light by default).  
- Lead magnets from `CRO-BACKLOG-2026-08-11.md` only after Phase 1–2 prove more form starts.  
- Optional: dark US only if George explicitly wants a secondary variant later.

**Do not:** full redesign, new routes, new experiment matrix, copy competitors’ layouts, publish unverified LinkedIn/Facebook counts, invent a third color system when AU light already exists.

---

## Success check (after ship)

- Form starts ↑ or hold; completes feel easier (fewer abandoned chip steps).  
- Phone clicks still fire.  
- Job-seeker divert rate not worse.  
- Holly: lead quality not collapsing (watch solo / junk).  
- Page length: first meaningful action without scrolling past a product brochure.  
- US and AU money LPs both read as **light / calm** (competitor-aligned), with market copy still distinct.

---

## Related docs

- CEO brief: Gmail mega prompt “Simplify Microsite + Conversion Strategy” (2026-08-11)  
- `vision/docs/SITE-EXPERIMENTS.md` — active A/Bs to consolidate  
- `vision/docs/CRO-BACKLOG-2026-08-11.md` — quiz/magnets parked behind this  
- `xray/data/growth-os.js` — competitor notes  
- Theme sources: `vision/app/au/au.css`, `vision/app/us/us.css`, `globals.css` `.micro-light`

**Next step:** Phase 1–2 shipped with this decision (light shell + cut sections + simple form). Park Phase 4 deeper LPs until form CVR is stable.
