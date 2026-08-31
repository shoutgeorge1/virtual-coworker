# Trust-first US landing pages — what this is

**PREVIEW ONLY — NOTHING LAUNCHED.**  
Look here: http://127.0.0.1:4321/preview/trust-first

---

## Pasteable (for George)

This is a company landing-page family for US paid Search. It looks like Virtual Coworker, not MyOutDesk.

We took their **structure**: white company header, logo, form in the first view, proof under the fold, a compare table, how it works, FAQ. We refused their **claims and orange**: no 70%, no SOC 2, no HIPAA, no one-week hire, no “8,500 clients.” Copy is ours. Reviews are ours (Google 5.0 / 39, Clutch 4.9).

Default view is **proof-heavy**. Simple is only `?v=simple`. Ten pages under `/preview/trust-first/…`. Forms go to a preview sink, not Zoho. These are not live `/us` URLs and not Ads destinations.

Headline: first sentence navy — “A local hire costs more.” Second sentence light blue `#0071c9`, page-specific (who / where). One idea each. Not two savings lines. Not orange. Not gold. Type is Century Gothic Paneuropean Bold like live `/us` (tighter tracking, color splits the two sentences). Cyan `#33ded8` stays on the dark footer.

We are **not launching**. Color just got corrected (again). Preview forms are still fake. Routes are still `/preview/…`. Do not change Final URLs until `/us` events are trusted. Brand stays deferred.

---

## What the system is

One template, ten configs. Same page machine for:

| Preview now | Future prod path (not live) |
| --- | --- |
| `/preview/trust-first/us` | Challenger only — do not swap live `/us` |
| `/preview/trust-first/philippines-virtual-assistants` | `/us/philippines-virtual-assistants` |
| `/preview/trust-first/virtual-assistant-agency` | `/us/virtual-assistant-agency` |
| `/preview/trust-first/staffing` | `/us/staffing` (page exists, not Ads yet) |
| `/preview/trust-first/real-estate` | `/us/real-estate` (measurement gate) |
| `/preview/trust-first/bookkeeping` | `/us/bookkeeping` (already live) |
| `/preview/trust-first/customer-service` | `/us/customer-service` |
| `/preview/trust-first/sales` | `/us/sales` |
| `/preview/trust-first/administrative-support` | `/us/administrative-support` |
| `/preview/trust-first/digital-marketing` | `/us/digital-marketing` |

Proof-heavy shows extra modules (reviews, compare, quotes, press). It does not change the H1, the URL, or the intent.

## What we took from MyOutDesk vs refused

**Took (structure):** light company site, sticky header, logo not a phone-hero, employer form first, compare table below the fold, process, objections, noindex paid twins later if ever approved.

**Refused:** orange, 70% overhead, SOC 2 / HIPAA / PCI, 0.7% pass, one-week hire, free rematch, MyTimeIn, flat monthly theater, DKI in the H1, quiz-on-the-form, generic `virtual assistants` head-term page.

## Brand color

Logo is navy `#214873` (`#1e4272` in the PNG) plus cyan `#33ded8` on **COWORKER** — **no gold in the mark**. Live `/us` is a dark navy shell, so H1 accents and links are cyan. That cyan washes out on white (vision already switches light quiz eyebrows to `--vc-blue`). This preview is a light company page, so the H1 accent is the palette’s light blue, not cyan and not gold.

Tokens we use:

| Role | Token | Hex |
| --- | --- | --- |
| Sentence 1, buttons, checks | `--vc-navy` | `#214873` |
| Sentence 2, links, section ticks, form top, header stripe | `--vc-blue` | `#0071c9` |
| Compare VC column | light-blue wash | `#e7f3fb` |
| Cream check wells | cream | `#f6f3ea` |
| Footer links on navy | `--vc-cyan` | `#33ded8` |
| Google stars only | — | `#fbbc04` |

We do **not** use `--vc-orange` (`#f7630c`) or `--vc-gold` (`#fac056`) anywhere on these pages except the Google star glyphs.

## Form / job-seeker

Company, name, work email, US phone, role. Careers link sends job-seekers to `virtualcoworker.com.ph`. Preview POST is `/api/lead-preview` only. No Zoho. No email. Documented Ads negatives (`job`, `jobs`, `salary`, `career`, `careers`, `apply`, `resume`, `work from home`) — **not uploaded**. Do not global-negative `hire` / `hiring`.

## Why not launching

1. George just asked for a color/headline correction — that is not a launch signal.
2. Forms still hit `/api/lead-preview`.
3. Routes are still `/preview/trust-first/*`.
4. Do not change Ads Final URLs until `/us` events are trusted.
5. Brand remains deferred.

Keyword plan is a recommendation + a **paused/review-only** CSV. Do not import it to the live account.
