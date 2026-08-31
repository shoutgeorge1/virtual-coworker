# Version One — long-page reshape (16 Aug, local mock)

Not a live replace. Folder kept: `ads-launch/mocks/paid-lp-replacements-2026-08-16/`.

## What changed

- Hero is short: one hiring headline, one support line, one large staff photo, Google/Clutch stars, the first guided-match question, the phone, and one job-seeker line.
- Core question: “What role are you hiring for?” (six Stage 1 roles). Bookkeeping skips that and starts on hours/workload; role is in the headline.
- Page continues: logos + ratings, four hiring steps, role cards, why VC, a large team photograph, four real quotes, FT/PT + rates (no live prices), six employer FAQs, closing CTA + phone.
- Clean preview: `?preview=1` hides the concept ribbon and switcher. `?review=1` brings controls back.

## Events (unchanged contract)

Role / hours clicks = `quiz_step` only. First name/email/phone = `employer_form_started`. Submit waits on mocked `/api/lead`. No Ads mappings added.

## Missing assets to request (do not invent)

- Client or staff **video** testimonials (none approved on disk)
- Named employee photos cleared for advertising (`.com.ph` portraits stay unused)
- Extra official office/event stills from LinkedIn / Facebook / Instagram (login-walled this pass)
- Headshots of the quoted clients (College Hunks, Good Co., etc.) — text quotes only today
