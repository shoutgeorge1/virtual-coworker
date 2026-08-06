# Virtual Coworker Stage 1 — ChatGPT Debrief (v6)

**Paste this whole file into ChatGPT.** Ask it to stress-test honesty, architecture, Final URLs, conversion definitions, and launch blockers — not to rewrite ads for vibes.

| Field | Value |
|-------|-------|
| Date | 2026-08-05 |
| Branch | `vision-demo` |
| Repo | `/Users/george/Developer/virtual-coworker` |
| Package | `ads-launch/google-ads-editor-import.csv` · `lp_version=stage1-v6` |
| LP host | `https://vision-three-alpha.vercel.app` |
| Launch Control | `https://vc-xray.vercel.app/launch-control` |
| Accounts | USA `496-715-1855` · AU `573-539-1940` |
| Ads enable | **NOT approved** — all CSV entities **Paused** |
| Deep dive | `ads-launch/CHATGPT-MEGA-AUDIT.md` |

---

## 1. What we’re launching (and why 2/account)

**Per market (USA + Australia separate accounts):**

| Campaign | ~Budget share | Job |
|----------|--------------:|-----|
| `VC_{US\|AU}_S_CORE` | **~60%** | High-intent VA / hire / Philippines-offshore staffing |
| `VC_{US\|AU}_S_ROLES` | **~40%** | Role intent: **Digital · Social · Admin · Controlled** |

**Controlled** = accounting, bookkeeping, customer service, HR, recruitment, sales (separate ad groups + category Final URLs under the Roles campaign).

**Brand is deferred** — not in this launch package. Historical brand campaigns (`PM_*_RSA_Brand`) may still be live outside this CSV; ops should pause them separately.

**Why 2 campaigns (not 22):** George approved collapsing Brand+Core+9 role campaigns into Core + Roles so budget is controllable (~60/40), Core owns the densest employer ST cluster, and Roles keep role intent / Final URL hygiene without nine separate daily budgets. Exact build left to the builder; structure is locked.

**Settings (all):** Search · Exact + Phrase only · Maximize Clicks · Max CPC US $8 / AU A$6 · **Paused** · category Final URLs · tracking template `{lpurl}` only · UTMs once on Final URL suffix · employer CTAs · curated negatives from ST evidence.

**Budget placeholders (George-decidable):**

| Market | Core | Roles | Day total | ~Monthly |
|--------|-----:|------:|----------:|---------:|
| US | $75 | $50 | $125 | ≈ **$3.8k** |
| AU | A$75 | A$50 | A$125 | ≈ **A$3.8k** |

These sit inside a **$10–20k per account / month** budget story — Stage 1 pace, with headroom to raise dailies after inquiry quality is trusted. Not an enable approval.

---

## 2. LP system

| Piece | Spec |
|-------|------|
| Host | `vision-three-alpha.vercel.app` (custom paid domain optional later) |
| Routes | `/us`, `/au` + 9 category slugs each (`digital-marketing`, `social-media`, `accounting`, `bookkeeping`, `administrative-support`, `customer-service`, `hr`, `recruitment`, `sales`) |
| Ads Final URLs | Category paths only in this package (Core → `administrative-support`; Roles → matching slug). No Brand generics. |
| Compat | `/us?role=bookkeeping` → 308 `/us/bookkeeping`; `/consult` → `#gate` |
| Gate | Employer vs job seeker → job seekers divert to careers `/ph` (no employer conversion) |
| A/B | Cookie `vc_ab_variant` a\|b · `?variant=` QA override · differs H1/subhead/CTA/hero |
| Casting | Filipino aspirational brand assets (commit `8705ff0` on prod). Plastic / white-HR heroes killed. |
| Phone | US `310-426-8776` · AU **none** (form primary) |
| Lead API | Validates → delivery channel **or** TEMPORARY log-only · Zoho not live · Ads conversions **off** |

**Conversion truth:**

```
Ad click → employer_inquiry_submitted (= server-accepted inquiry)
         → human follow-up → job order (CRM — not wired) → placement (ops — not wired)

form submit ≠ job order ≠ placement
phone_cta_clicked ≠ qualified call
Editor "Conversions" / "All conv" ≠ job orders
```

---

## 3. Historical evidence used

**Sources:** Editor exports ~2024-08-01 → 2026-08-04 (`audit-data/performance/`, UTF-16).  
**Machine summary:** `ads-launch/historical-performance-summary.json`

| Account | Cost | Clicks | Conversions | All conv | ST raw → deduped |
|---------|-----:|-------:|------------:|---------:|-----------------:|
| USA | $723,838.59 | 87,060 | 2,597.32 | 4,629.39 | 66,869 → 66,465 |
| AU | $457,489.46 | 49,457 | 1,412.66 | 3,505.46 | 26,211 → 26,132 |

**Keep examples (employer intent → package):** virtual assistant / hire VA / PH·filipino VA · how to hire a virtual assistant (**not** negatived) · social media manager philippines · virtual marketing assistant · philippines bookkeeper · lead gen VA · CS VA · PH accounting outsourcing.

**Kill / negative clusters:** onlinejobs.ph · free/reviews/pricing · VA jobs/salary/careers · bare WFH · Spanish/LATAM · Upwork/Fiverr/competitors · DSA bleed brands.

**Limitations ChatGPT must not ignore:** ST cost &lt; campaign cost; Conversions inflated vs business outcomes; HR/recruitment thin (curated, not proven winners); historical brand conversion ≠ proof current microsite converts.

---

## 4. Package counts (v6 machine)

| Entity | Count | Status |
|--------|------:|--------|
| Campaigns | **4** | Paused |
| Ad groups | **40** | Paused |
| Positive keywords | **1,568** (Exact 1,182 · Phrase 386) | Paused |
| RSAs | **78** (15 headlines + 4 descriptions each — **no blanks**) | Paused |
| Unique campaign negatives | **191** × 4 = 764 rows | Broad |
| Callouts / sitelinks / snippets | 24 / 16 / 4 | |
| CSV rows | **2,498** | |

Rebuild: `python3 ads-launch/build_stage1_editor_package.py`

---

## 5. What’s paused / not enabled

- **Everything in the CSV** — Campaign, Ad group, Keyword, Ad status = **Paused**
- **No Google Ads enable** from this work
- **No Ads conversion firing** (`NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false`)
- **Brand Search** — deferred (not imported)
- **WordPress** — untouched; paid Final URLs must not use WP
- **Zoho / CallRail / real inbox** — not launch-ready (QA log-only on prod is TEMPORARY)
- **Legacy live outside CSV (Aug 5 UI read):** `PM_US_RSA_Brand` / `PM_AU_RSA_Brand` still spending small with 0 conversions — recommend pause in Ads UI separately

---

## 6. Decisions locked

See `ads-launch/DECISIONS.md`.

| Decision | Locked |
|----------|--------|
| Architecture | 2 campaigns × 2 markets; Brand deferred |
| AU phone | Form-primary |
| US phone | 310-426-8776 |
| Careers | `/ph` |
| Lead QA | Log-only TEMPORARY |
| Ads conversions | Off |
| Pilot | noindex |
| Budgets | Core $75 / Roles $50 (US); Core A$75 / Roles A$50 (AU) |
| Max CPC | US $8 · AU A$6 |
| Enable | **Not approved** |

---

## 7. Blockers (still open)

1. Real lead email / webhook recipients (log-only ≠ paid-ready)  
2. Response-time SLA / who answers  
3. Zoho (optional — must not fake)  
4. CallRail / qualified-call tracking  
5. GTM → Ads conversion mapping  
6. Custom paid domain (optional host swap)  
7. Explicit George approval to enable any campaign  
8. Pause legacy `PM_*` Brand bleed  
9. Brand Search scope (when/if added later)

---

## 8. Honesty: v1–v4 fuck-ups → what v5/v6 fixed

| Era | Mistake | Fix |
|-----|---------|-----|
| Early | Double UTM (template **and** suffix) | Template `{lpurl}` only; suffix once |
| Early | Final URLs `?role=` inert on LP | Real `/us\|au/{slug}` + middleware 308 |
| Early | Template / boilerplate RSAs | Unique RSAs; builder QA rejects spam + blanks |
| Early | Fake AU phone placeholder | No AU phone UI; form primary |
| Early | “Consult” / “book a demo” SaaS language | Employer staffing CTAs |
| Early | Plastic / white-HR heroes | Recast Filipino aspirational assets |
| Early | Silent log-only accept by default | 503 unless channel **or** explicit flag |
| Early | Dishonest event names | `employer_inquiry_submitted` etc. |
| v4→v5 | Brand deferred while Core thin; role-only sprawl | v5 added Brand+Core + category URLs (22 campaigns) |
| **v5→v6** | 22 campaigns too many for Stage 1 ops/budget | **Collapsed to 2/account**; Brand deferred again by design; Core owns VA cluster; Roles owns Digital·Social·Admin·Controlled; budgets Core $75 / Roles $50 |

We are **not** claiming: launch-ready, Zoho sync, job-order ROI, or that historical Ads conversions equal placements.

---

## 9. What ChatGPT should stress-test

1. **Is 2-campaign topology sane** vs returning to Brand + many role campaigns? Challenge Core → `administrative-support` Final URL for “hire VA.”  
2. **Is log-only acceptable for any paid click?** (Our answer: **No**.)  
3. **Are Max CPC $8 / A$6 and $75/$50 dailies sane** vs historical CPC / $10–20k monthly story?  
4. **Controlled-tier thin ST (HR/recruitment)** — keep Paused longer / strip from Stage 1?  
5. **RSA claims** — sample for invented savings, “top 1%”, consult language.  
6. **Keyword hygiene** — job-seeker / medical / Spanish / competitor leaks in positives? Bare `hire` negatived by mistake?  
7. **Double UTM / WP Final URL / generic Brand URL** regressions in CSV.  
8. **Conversion mapping risk** if GTM maps wrong events before Max Conv.  
9. **Legacy PM_* Brand still Enabled** — parallel bleed.  
10. **Careers `/ph` divert** — real careers product or Stage 1 placeholder risk?

### Do **not** invent requirements we never claimed

- Live Zoho writeback · CallRail qualified calls · WP redesign · Broad/PMax “for volume” · Fake AU phone · Brand Search in this CSV

---

## 10. Spot-check commands

```bash
python3 ads-launch/build_stage1_editor_package.py

python3 - <<'PY'
import csv
from collections import Counter
rows=list(csv.DictReader(open('ads-launch/google-ads-editor-import.csv',encoding='utf-8-sig')))
print('campaigns', sorted({r['Campaign'] for r in rows}))
print(Counter(r['Row Type'] for r in rows))
assert {r['Campaign'] for r in rows} == {
  'VC_US_S_CORE','VC_US_S_ROLES','VC_AU_S_CORE','VC_AU_S_ROLES'}
assert not any('?role=' in (r.get('Final URL') or '') for r in rows)
assert not any('[APPROVAL_' in (r.get('Budget') or '')+(r.get('Max CPC') or '') for r in rows)
ads=[r for r in rows if r['Row Type']=='Ad']
assert all(r[f'Headline {i}'] and r.get(f'Description {j}')
           for r in ads for i in range(1,16) for j in range(1,5))
print('RSA', len(ads), 'all full 15/4 OK')
PY
```

---

## 11. Operator next (not Ads enable)

1. Hostile audit of **this** debrief (optional: also MEGA).  
2. Replace log-only with real lead delivery.  
3. Import CSV **Paused**; human review matrix `09`.  
4. Pause legacy `PM_*` Brand if still bleeding.  
5. Enable only per `07-phased-activation-recommendation.md` after **explicit** George approval.

**Ads remain Off.**

---

*End of ChatGPT debrief (v6). Shorter index: `FULL-BUILD-REPORT.md`. Deep audit: `CHATGPT-MEGA-AUDIT.md`.*
