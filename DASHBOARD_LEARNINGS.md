# Dashboard learnings (pointer)

Company X-ray dashboard UX is a **durable George preference**, not a one-off for Virtual Coworker.

**Canonical skill (follow this next time):**

[`~/.cursor/skills/company-xray-dashboard/SKILL.md`](/Users/george/.cursor/skills/company-xray-dashboard/SKILL.md)

Covers: Overview = simplified map + platforms; Findings = organized cards (website mistakes → contamination); Tracking = inventory with separate-per-market-as-correct; Action plan = Dime-like wire-up; steal DIME concrete QA + CEC simple Overview; no GTM jargon soup; no dead tabs.

This repo’s `xray/` shell is the reference implementation — copy the pattern, don’t rebuild from scratch.

## Engagement variant (2026-08-02)

`xray/` has been restructured from interview-prep X-ray into a **paid acquisition command
center** ([`docs/paid-command-center-plan.md`](./docs/paid-command-center-plan.md)). Reusable
pieces if a future engagement needs the same shape:

- **Shared sidebar via `nav.js`** — one array, `data-page` on `<body>`. Nav can't drift across pages.
- **One status vocabulary** (`.st` chips): Not started · Needs access · Needs validation · Ready ·
  In progress · Blocked · Live · Verified · Deferred · Handed off. Legend on the landing page.
- **Honest empty states** (`.empty`) instead of placeholder metrics — "Requires X access" plus what
  is needed. Never fabricate account data.
- **Ownership columns** (`.own-grid`) — owns / shared / hand off makes scope arguments visual.
- **Findings become an archive**, not the roadmap, when the engagement is forward-looking. Move the
  evidence, keep the proof chips, reframe the header.
