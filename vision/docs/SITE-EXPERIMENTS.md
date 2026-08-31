# Site experiments (living A/B)

Like Ads — run 2–3 variants on key engagement pieces, measure, keep winners, refresh. **Not** one-and-done A/B death.

## Status — mostly parked (2026-08-12) · selective live (2026-08-21)

**Most background A/B tests stay off.** Exit popup / chat / density chaos stays frozen.

**Selective live:** `us_hero_portrait` on `/us` only — female navy (`va-us`) vs male portrait (`va-au`). Flip via `SELECTIVE_LIVE_EXPERIMENTS` in `vision/lib/experiments.ts`. Preview: `?vc_exp=us_hero_portrait&vc_var=a|b`.

**Marketing orange (not A/B):** `/us/digital-marketing` and `/us/social-media` heroes use **Marketing A** (`/roles/marketing-a.png`, orange sweater) as the live control. Compare form CVR week-over-week.

Frozen arms for everything else:

| ID | Frozen to | Why that letter |
|---|---|---|
| `lp_density` | **B lean** | Form money LPs already force lean |
| `gate_headline` | A | Current form title |
| `role_imagery` | A | Current default portraits (Marketing A on digital-marketing) |
| `exit_popup` | A | Current popup copy (**widget off** 2026-08-14) |
| `chat_launcher` | A | “Chat with us” (**widget off** 2026-08-14) |
| `quiz_copy` | A | Quiz LP framing |
| `?variant=` (LP creative) | **A** | Category H1/sub A; query still works for QA |

Do **not** treat parked as “restore dark US” or “restore chip-quiz form.” Those stay unmounted.

## How it works

- Module: `vision/lib/experiments.ts`
- Assignment: sticky in `localStorage` (`vc_exp_<id>`) + cookie (90 days)
- Force override: `?vc_exp=<id>&vc_var=<a|b|c>` (Site tests preview links) — sticky, before first paint
- Same visitor keeps the same letter until storage is cleared
- Events go to `dataLayer` (GTM) **and** a GA4 collect beacon (`MarketGtm`
  `__vcSendExpGa4`) so `experiment_*` reaches GA4 even when GTM Event tags are
  not mapped (gtag `event` is swallowed when GTM owns the same measurement ID)

## Parked experiments (Aug 2026 — not serving random arms)

| ID | Variants | Surface | What changes |
|---|---|---|---|
| `exit_popup` | A / B / C | Soft popup | Image + headline + body + CTAs. **Hold 2026-08-14** — off live (`NEXT_PUBLIC_ENABLE_EXIT_INTENT=false`). A/B vs clean LP later. |
| `quiz_copy` | A / B / C | Role quiz (`/us/quiz` · `/au/quiz` only) | Benefit headline, lead, teaser, win-screen kicker. Mid-page quiz **unmounted** from form LPs 2026-08-11 (LP simplify). |
| `chat_launcher` | A / B | Chat bubble | Launcher label — must say **Chat**, not live agent. **Hold 2026-08-14** — off live (`NEXT_PUBLIC_ENABLE_CHAT=false`). A/B vs clean LP later. |
| `gate_headline` | A / B | Form card (generic LP) | Headline + “2 minutes” framing |
| `lp_density` | A / B | Quiz / secondary (form LPs force lean) | A = wordy, B = lean. **Form money LPs force lean** as of LP simplify 2026-08-11. |
| `role_imagery` | A / B | Category heroes + services + late trust | Portrait set A (defaults) vs set B |
| `us_hero_portrait` | A / B | **US `/us` hero only** | **Selective live 2026-08-21.** A = female navy `va-us`. B = male `va-au`. |

Category role pages keep role-specific gate titles (not A/B’d).

### `us_hero_portrait` — female vs male on `/us`

Gut from AU: male hero may lift trust. US hub only — role LPs unchanged (marketing LPs use Marketing A orange).

- **A** — `/brand/va-us.jpg` (female, navy blouse) — historic converting path
- **B** — `/brand/va-au.jpg` (male) — AU portrait as US challenger
- Sticky 50/50 · `experiment_view` / `experiment_convert` when form/phone fires
- Force: `https://www.virtualcoworker.app/us?vc_exp=us_hero_portrait&vc_var=b`

### Marketing A orange (live swap, not random A/B)

`/us/digital-marketing` + `/us/social-media` heroes → `/roles/marketing-a.png`. Ads asset CTR for this face was soft; testing on the LP where conversion happens.

### `lp_density` — wordy vs lean

The question: does more explanation help or hurt form starts?

- **A `wordy`** — supporting copy visible (staffing explainer, section sub-copy).
- **B `lean`** — everything marked `data-lp="secondary"` removed; section rhythm tightened.

**Form money LPs (`/us`, `/au`, role category form surfaces):** lean is forced
(LP simplify 2026-08-11). Parked sections (mid-page quiz, industry stats, PainGain,
long FAQ, StopCloser) are unmounted — not merely hidden by density.

**What never changes between arms:** the lead form, the phone number, every CTA,
the proof counters, recognition badges, client marks and review quotes.

How it is wired:

- `assignExperiment("lp_density")` → sticky `a`/`b` (see `lib/experiments.ts`)
- An inline script in `app/layout.tsx` writes `<html data-lp-density>` **before
  first paint**, so the lean arm never flashes the wordy layout
- `app/components/LpDensity.tsx` re-confirms the attribute and fires
  `experiment_view` once per session
- `globals.css` hides `[data-lp-density="lean"] [data-lp="secondary"]`

Elements currently marked secondary: the hero staffing explainer, the “how hiring
works” sub-line, the FAQ **cards** (not the FAQ heading), and the industry-stats
block in the trust band. **Never secondary:** recognition badges, client marks,
review quotes + 4.9 Clutch pill, and Featured In (`PressBand`, below the quiz).
Both density arms keep the public reviews George wants visible.

### `quiz_copy` — benefit-led headlines (refreshed Aug 2026)

All three arms lead with the payoff rather than the quiz itself.
**Question logic is shared** (branching by drain) — A/B/C only skin
headline / lead / teaser / win-screen kicker.

| Variant | Quiz headline | Hero teaser |
|---|---|---|
| A | Who should you hire first? | Hiring quiz · Take the hiring quiz — who should you hire first? → |
| B | See which teammate to hire. | Take the hiring quiz · Who should you hire first? → |
| C | Find the teammate that gets you your week back. | Hiring quiz · Take the hiring quiz → |

**Branching quiz (3 taps):** Q1 picks the drain (admin / marketing /
books / support / sales). Q2–Q3 are path-specific (e.g. marketing →
channels + load; books → AP/AR/payroll + software). Result copy follows
those answers. Force preview:
`?vc_exp=quiz_copy&vc_var=a`

### `chat_launcher` — must say Chat (Aug 2026)

Scripted assist chat — **not a live agent**. Launcher copy has to say Chat.

| Variant | Launcher |
|---|---|
| A | Chat with us |
| B | Chat — hiring help |

Panel header: “Chat / Quick answers · not a live agent.”

## Events

| Event | When |
|---|---|
| `experiment_view` | Variant shown (once per session per experiment) |
| `experiment_click` | CTA / start / open on that experiment |
| `experiment_convert` | Fan-out on durable form success or phone CTA click |

Payload fields: `experiment_id`, `experiment_variant`, plus `convert_reason` (`form_submit` \| `phone_click`) and market/source extras.

Also still fire existing assist events (`exit_intent_shown`, `quiz_started`, etc.).

## How to check your variant (dev)

**Force via URL** (preferred — used by xray Site tests preview links):

```
https://www.virtualcoworker.app/us?vc_exp=lp_density&vc_var=b
https://www.virtualcoworker.app/au?vc_exp=quiz_copy&vc_var=c
```

Params: `vc_exp=<id>` + `vc_var=a|b|c`. Applied **before first paint** (sticky
localStorage + cookie). Same pattern works for every live experiment:
`exit_popup`, `quiz_copy`, `chat_launcher`, `gate_headline`, `lp_density`,
`role_imagery`.

In browser console on `/us`:

```js
Object.fromEntries(
  ["exit_popup","quiz_copy","chat_launcher","gate_headline","lp_density","role_imagery"]
    .map(id => [id, localStorage.getItem("vc_exp_"+id)])
)
```

Force a letter: `localStorage.setItem("vc_exp_quiz_copy","b"); location.reload()`

See the lean page: `localStorage.setItem("vc_exp_lp_density","b"); location.reload()`
(`"a"` puts the wordy page back.)

Force role imagery B: `?vc_exp=role_imagery&vc_var=b`

## Dashboard (xray)

- Page: **Site tests** → `xray/experiments.html` (nav after Checklist)
- Snapshot: `xray/data/experiments-snapshot.json`
- Pull stub: `ads-launch/pull_experiments_snapshot.py`
  - Local: drop events at `xray/data/experiments-events.json`, then run the script
  - Or set `GA4_PROPERTY_ID=549075481` (US / G-2V3V0BS6JW; script default) + ADC for a GA4 Data API pull
    (`gcloud auth application-default login`)
- Primary KPI now: **clicks / CTR** (`experiment_click` ÷ `experiment_view`)
- Converts column is reserved (`experiment_convert`) — no fake winners

## Weekly review with George (until GA4 is comfortable)

1. Open Tag Assistant / GA4 DebugView on `www.virtualcoworker.app/us`
2. Confirm `experiment_view` → click → convert funnel for each ID
3. Compare convert rate by `experiment_variant` (form + phone)
4. Kill losers: leave winner as sole copy in the component, or rebalance variants
5. Refresh xray **Site tests** after a pull; note winners on Launch Control stub if useful
6. Ship 1–2 new challengers next week — keep the living loop


### `role_imagery` — live (Aug 2026)

Arm **A** = v2 defaults (younger marketing, focused books, CS headset, dedicated HR, sales guy + trust-consult).  
Arm **B** = prior set (`*-a.png` / `admin-b` for HR + trust-team-office) — sole challenger.

Surfaces: category LP heroes, `/services` cards, late trust photo above FAQ.  
Relevant face → relevant role only (see `IMAGE-CHOICES.md`).  
End-of-page closer is copy + CTAs only (stop-sign photo retired).

See `IMAGE-CHOICES.md` + `config/role-imagery.ts`.

## Popup timing (not an experiment — product rule)

**Status (2026-08-14):** Chat launcher and exit popup are **on hold**. They obscure the LP, especially on mobile. Flags default off unless explicitly `true`. Revisit later as an A/B vs the clean LP (form / phone / gate) to pick conversions. Do not remount without George.

Shared constants: `lib/conversion-assist.ts` (`CONVERSION_ASSIST`). Code stays in repo.

- Absorb first: ~20s before exit-intent; chat launcher ~22s or ~32% scroll
- Desktop: exit-intent after absorb; timed fallback ~40s; scroll ~32% also OK after absorb
- Mobile: scroll ~32% **or** ~40s timed — never immediate
- Form busy / already filling / chat panel open / chat already engaged → don’t show exit
- Chat OR exit modal — never stack (`vc-popup-open` hides chat; exit skips while chat open)
- CTA → light binary (hiring vs job) → hirers scroll to `#gate` with employer path open on **What do you need help with?** + gold flash (`focusGate`); job seekers leave to `virtualcoworker.com.ph`
- Sticky CTA (mobile): only when `#gate` / quiz target leaves the viewport

## CRO backlog

Lead magnets, quiz experiments, sales video, Veo: `vision/docs/CRO-BACKLOG-2026-08-11.md` + Launch Control **CRO / lead quality**.

## Related

- xray **Site tests** dashboard: `experiments.html` — clicks/CTR first; converts when wired
- Launch Control stub still has the winner notepad
- LP creative A/B (`?variant=a|b`) is separate (ads landing creative) — do not confuse with site experiments
