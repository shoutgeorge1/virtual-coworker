# Executive incremental pass — 16 Aug 2026 (local only)

George’s ChatGPT brief, taken with a grain of salt. **Not deployed.** Local preview: `http://127.0.0.1:8770/executive.html`.

Bake: `python3 ads-launch/bake_xray_pages.py` → `xray/executive.html`. No Ads API, no Zoho writes, no GTM, no email.

---

## 1. Audit of the current dashboard (before this pass)

The page was already the right product: US / AU market cards, three unit-cost tiles, Ads KPI row, Cheyenne source chips, Zoho census footnote, CRM halo, agency contrast, Evidence drawer.

What was hurting stakeholder trust:

| Issue | Evidence |
|-------|----------|
| Ads KPI row used **rolling last 7 days** | US spend **$1,116** (Aug 8–14) while cost tiles used **$844.94** (Mon–Fri Aug 10–14) |
| US and AU rolling windows were **different dates** | US Aug 8–14 vs AU Aug 9–15 |
| US cost tiles were **not labeled estimated** | AU said estimated; US did not |
| Cost tiles could be read as Google Ads CPL | No compact attribution marker |
| CRM halo used **July 1–9** with red −4% / −31% | Prompt + VC rules: July is not an apples-to-apples Stage 1 baseline |
| Agency table showed **+512% / +809% better** | Fake improvement % against a ~2-year inflated-conversion window |
| No landing-page micro-funnel | Role / hiring brief / contact events are not in the GA4 snapshot |
| Refresh times were Ads-only | GA4 / Zoho / IS pulls were not on the header |

What was already correct and **left in place**: card layout, US/AU split, currencies never mixed, Cheyenne source chips as she labeled them, email + Zoho not added, Brand not mentioned, Max Clicks, Evidence IS tables.

---

## 2. Data sources and fields

One sales week on the hero: **Mon 10 Aug – Fri 14 Aug 2026**. Incomplete calendar week (Sat–Sun not in the sales report). First complete Stage 1 sales week = the operational baseline. Prior complete Stage 1 week: **not yet**.

| Metric | Source | Fields |
|--------|--------|--------|
| US/AU spend, clicks, impr, CTR, CPC | `executive-snapshot.json` `sales_ops_*` + `performance_*.by_date_stage1` | `spend_usd`, `clicks`, `impressions`, `avg_cpc_usd`; conversions summed from daily `conversions` |
| US Ads conv = 1 | `performance_us.by_date_stage1["2026-08-14"].conversions` | Google Ads primary |
| AU Ads conv | same window, no daily conversions | shown as — / Unavailable |
| Cost / enquiry, call, JO | `sales_ops_us` / `sales_ops_au` | spend ÷ Cheyenne 14 / 9 completed calls; AU Zoho 13 / 2 discovery / 3 JO |
| Enquiry sources | `sales_ops_us.sources` | Cheyenne labels unchanged |
| US Zoho census | `sales_ops_us.zoho_census` | 18 SE · 0 gclid — **not added** to 14 |
| Search IS / lost rank / budget | `impression-share.json` last 7 **complete** days ending 13 Aug | labeled in the market note; different window |
| Paid LP sessions | `ga4-snapshot.json` | US Paid Search **290**; AU `paid_search_sessions` **52**. Rolling `7daysAgo → today` — **Incomplete**, not the sales week |
| form_start = 10 | GA4 `events_interesting` | diagnostic, not a qualified lead |
| Thank-you sessions | GA4 `path_kind_sessions.thank_you` = 7 (US); AU 0 | page landings ≠ Ads conversions |
| Role / hiring brief / contact / placement | **not in snapshot** | “Not currently measured” + missing event name |
| CRM halo SE / JO / discovery / gclid | `zoho-stage1-halo.json` | Stage 1 Aug 6–14; July column labeled legacy / non-comparable |
| Agency CTR/CPC/spend / Zapier JO | `recovery-audit.json` | context only |

US $ and AU A$ never combined.

---

## 3. Incremental change list

**Untouched:** sidebar, card chrome, three hero cost tiles, six Ads tiles, source chips, Zoho footnote, IS evidence drawer, Max Clicks copy, Cheyenne/Holly ownership.

**Changed in place:**

1. Hero Ads row uses the **same Mon–Fri sales week** as the cost tiles ($845 / A$671, not $1,116 / A$811).
2. Week heading names the dates and marks the week incomplete (weekdays only).
3. `estimated` on **US and AU** cost tiles; compact **Directional** marker; “estimated blended acquisition cost” line.
4. Confidence pills: Verified / Directional / Incomplete / Unavailable.
5. Three-bullet executive summary + cold-start disclosure.
6. Compact funnel strip per market; missing GA4 events named, no fake step rates.
7. CRM halo: July not used as a performance delta; no red/green vs July.
8. Agency: “legacy / non-comparable”; sensational % deltas removed.
9. CRM readiness drawer (writes still off).
10. Header shows Ads / Zoho / GA4 / IS refresh times.
11. Conservative “watch next week” line per market.
12. Rolling last-7 moved under a secondary details block.

**Not done (grain of salt):** Mon–Sun lock without weekend sales data; weighted attribution; excluding job-seekers from the denominator (George has not picked a claim level); new design system; deploy.

---

## 4. Revised local implementation

- `ads-launch/bake_xray_pages.py` — bake + `verify_executive_html`
- `xray/executive.html` — static baked page

---

## 5. Screenshots

`ads-launch/research/executive-incremental-2026-08-16/screenshots/`

- `before-desktop.png`
- `after-desktop.png`
- `after-mobile.png`

---

## 6. Data-confidence matrix

| Layer | Examples | Status |
|-------|----------|--------|
| 1 Proven paid | Spend, clicks, CTR, CPC, Ads conv, Search IS | **Verified** (IS window ≠ sales week — noted) |
| 2 Landing-page | Paid sessions, form_start, thank-you sessions | **Incomplete** (rolling GA4 ≠ sales week) |
| 2 Landing-page | Role select, hiring brief, contact step, phone click, Calendly | **Unavailable** |
| 3 Business | Enquiries, completed/booked calls, JO | **Directional** |
| 3 Business | Placement, paid CAC with gclid | **Unavailable** |
| Context | Agency CTR/CPC, July CRM slice | **Legacy / non-comparable** |

---

## 7. Missing instrumentation and CRM dependencies

**GA4 events not in the snapshot:** `employer_gate_selected`, hiring-brief step two, contact-information step, `employer_inquiry_submitted`, `phone_cta_clicked`, `calendly_cta_clicked`.

**CRM:** `.app` not writing to Zoho; `utm_gclid` 0/51; gbraid/wbraid missing; `VC_Submission_ID` missing; offline import deferred; Zapier JO uploads not a complete audit. See CRM readiness drawer.

---

## 8. Test checklist

- [x] Cost tiles and Ads spend share Mon–Fri dates
- [x] US $ and AU A$ never mixed
- [x] Partial week labeled (weekdays; Sat–Sun not in report)
- [x] Missing JO / placement / micro-events render as — / Not currently measured
- [x] Business outcomes labeled estimated / directional, not Google Ads CPL
- [x] Cheyenne 14 and Zoho 18 not added
- [x] Organic chips not relabeled as paid
- [x] Ads / Zoho / GA4 / IS refresh times in the header
- [x] Mobile CSS: 2-col Ads tiles, wrapping funnel
- [x] Existing cards still present
- [x] `verify_executive_html` passes on bake
- [ ] George visual check in external Chrome (this pass)

---

## 9. Change log

- Align hero Ads KPIs to the sales-ops week.
- Label estimated / directional on US cost tiles.
- Confidence pills + disclosure + 3-line summary.
- Funnel strip with honest missing events.
- Stop using July and agency % as Stage 1 performance.
- CRM readiness drawer.
- Rolling 7d demoted.

---

## 10. Rollback

```bash
git checkout -- ads-launch/bake_xray_pages.py xray/executive.html
python3 ads-launch/bake_xray_pages.py   # only if you need to re-bake from old baker
```

Do not deploy a rollback. Do not revert other xray pages unless they were part of this pass.

---

## What I ignored from the ChatGPT brief

- Redesign / new card system / US–AU selector (panels already exist).
- Inventing a Mon–Sun week or a prior complete Stage 1 week.
- Weighted attribution / dropping job-seekers from the money tiles without George picking a claim level.
- Relabeling Cheyenne’s Google Organic as ads.
- Recommending Broad, PMax, DSA, or Maximize Conversions.
- Deploying to vc-xray.vercel.app.
