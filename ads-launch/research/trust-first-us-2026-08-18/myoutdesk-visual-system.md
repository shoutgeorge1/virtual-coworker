# MyOutDesk visual-system analysis

Internal. 18 August 2026. Five confirmed paid LPs only. Cached HTML under `ads-launch/research/myoutdesk-2026-08-18/cache/lp-google-*.html`. No tracking-parameter fetches. Do not copy sentences, stats, or claims.

## 1. Header, ATF, logo, nav

Sticky white header (`paid-nav`), thin gray bottom border, logo left, almost no nav. It reads like a company site header that forgot to add a menu, not like a dark PPC squeeze. The logo is the only brand object in the first strip. Phone is not the hero. Trust sits in the body, not as a flashing badge row above the fold.

## 2. H1, copy, CTA, form, phone

H1 is written English, not a raw keyword token. PH and generic pages add an offer clause after the noun. Real estate is a short industry H1. Brand says “trusted leader.” Brand-b names the search itself. Supporting copy is one paragraph. Primary action is a strategy-session form: full name, business email, company name, phone. Hidden fields copy `gclid`, `gbraid`, `wbraid`, UTMs, and first landing URL. No `tel:` in the cached paid HTML. Form is the conversion.

## 3. Trust near the hero

Proof starts immediately under the fold: years, process, comparison, then volume/security theater. The emotional effect is “this company has been doing this a long time,” even when the page is visually plain. PH leans geography. Generic leans awards/services. Real estate swaps in industry tasks. Brand-b piles certifications and speed.

## 4. Section order, width, color, cards

Shared master, not unique templates. Typical order: form + H1 → partner/proof → roles as cards → comparison → how it works → trust/security → objections → closer form. Content width is modest (container, ~920px max in CSS). White/light paper, dark text, one accent. Cards are ordinary bordered blocks. Radius and shadow come from a utility system, not giant floating glass. Photos exist but do not dominate the ATF the way a SaaS hero does.

## 5. Proof modules and variants

Roles are modules on PH/generic, not their own paid URLs (bookkeeping and CS `/lp/google-*` 404). Testimonials and logos are present. Stats and compliance claims are heavy (do not reuse). Process is short. FAQ/objections are written as “reasons owners wait.” Brand vs brand-b is the same visual language with a louder proof stack on B. Generic vs PH vs RE changes the H1 and a few modules, not the chrome.

## 6. Mobile, sticky, what to steal vs refuse

Sticky header stays. Form stays in the first conversation on desktop; on a narrow screen it must not push the H1 into a tiny leftover column. Steal: white company header, restrained nav, literal H1, employer form, hidden attribution, noindex paid URLs, one primary action. Refuse: 70% overhead, 0.7% pass, client counts, savings, SOC 2 / HIPAA / PCI, ratings we do not own, DKI, quiz-on-the-form, chat bubbles, and cloning every keyword into its own LP.

## Lesson for Virtual Coworker

Trustworthy master format + a few deliberate configs. Not hundreds of role SKAGs. Not an AI landing-page experiment.
