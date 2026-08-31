# US Brand Defense — read-only audit (13 Aug 2026)

**Status:** Planning only. **No live Ads / WP / Zoho / URL / budget changes.**  
**Live Brand_VC inside CORE:** left Enabled. Not paused, split, or edited.  
**New campaign:** Editor CSVs **Paused**. Do not Import/Post/Enable until George says.

This does **not** replace Core/Roles employer lead-gen. Medium / controlled follow-up.

Checklist: [Launch Control → Brand Defense](https://vc-xray.vercel.app/launch-control.html#brand-defense)

---

## Decision: **B — prepare paused `VC_US_S_BRAND`. Keep A live until George Approves.**

| Option | Verdict |
|--------|---------|
| **A. Keep Brand inside Core** | **Current live state.** Volume is tiny. Do not pause `Brand_VC`. |
| **B. Split to paused `VC_US_S_BRAND` (.com + TIS)** | **Permanent architecture to prepare.** TIS cannot run on one AG inside CORE Maximize Clicks. Brand CTR will paint Core healthy if left mixed. Isolated budget is the only way Brand cannot eat Core/Roles. |
| **C. Do not run paid Brand** | **Not now.** Current spend is $8.68 / 7d — not irrational. Historical ~$803 CPA is **untrusted** (not proof the leads were junk, not proof they were qualified). C is the **stop rule after a controlled test**, not the plan today. |

**Do not Enable B in this pass.** `.com` Ads/GA4/form/gclid/Zoho are not verified. RSA stays off WordPress contact until that gate is true.

---

## 1. Temporary Brand ad group (live)

| Field | Evidence |
|-------|----------|
| Account | `496-715-1855` |
| Campaign | `VC_US_S_CORE` (Enabled) · Maximize Clicks · $75/day |
| Ad group | `Brand_VC` · `205906384984` · **Enabled** |
| Keywords | 36 Exact+Phrase (19 texts). No Broad. |
| Ads | 3 RSAs → `https://www.virtualcoworker.app/us` |
| Last 7d (13 Aug read) | **15 impr · 5 clicks · 33.33% CTR · $1.74 CPC · $8.68 · 0 conv** |
| Search terms | Only `virtual coworker` (Added) — same 15 / 5 / $8.68 / 0 |
| Isolated Brand IS | **Not available.** API rejects `search_budget_lost_impression_share` on `ad_group`. |

Sources: `ads-launch/_us_brand_ag_draft.json`, `xray/us-brand-ag-review.html`, `ads-launch/_us_brand_ag_readonly.json` (3 read-only GAQL; call 1 failed on AG IS fields; not retried).

George’s “extremely high CTR” is real. **Do not treat 33% as Core health.**

---

## 2. Campaign-mixed impression share (not Brand)

`VC_US_S_CORE` last 7d (13 Aug campaign pull) **includes Brand_VC**:

- Search IS 31.2% · top 20.7% · abs top 10.9%
- Lost rank 25.2% · **lost budget 43.6%**
- 1782 impr · 234 clicks · $539.61 · $2.31 CPC

Auction overlap: **not pulled**. Same fields failed 13 Aug. Do not retry.

Brand IS / top / abs top / lost rank / lost budget at ad-group grain: **cannot get cheaply**. Any CORE IS number is mixed.

---

## 3. Historical `PM_US_RSA_Brand` (Editor export ~1 Aug 2024 – 4 Aug 2026)

| | |
|--|--|
| Bid | Maximize conversions |
| Budget field | 100 |
| Enabled RSA URL | `https://virtualcoworker.com/` (WordPress homepage). try.`/us` existed **Paused**. |
| Enabled keywords | `[virtual coworker]` · `[virtual coworker usa]` · `[virtual coworker staffing]` · `"virtual coworker reviews"` · `"virtual coworker pricing"` |
| Cost | **$12,845.43** |
| Clicks | **1,134** |
| Avg CPC | **$11.33** |
| Conversions | **16** (Ads “Conversions”) |
| All conversions | **133.72** |
| Cost / conv | **$802.84** on the 16 — **not** a qualified-lead CPA |

George paused this 7 Aug (~$1k/lead order of magnitude). **SEO owns brand** was the operating rule until this planning ask.

**The one Exact that historically converted:** **cannot isolate.** No keyword-level conversion export in repo. Closest search-term evidence: `virtual coworker reviews` (30 clicks · $831 · 3 conv in one rollup; another rollup 13 clicks · $509 · 1 conv). That was Phrase in the remnant, not proven Exact. Current live Exact that is working: `[virtual coworker]`.

**What those 16 conversions were:** **cannot verify.** Conversions ≠ All conversions ≠ job orders ≠ Zoho qualified leads. Do not treat $500–$1,000 as a qualified employer lead.

**Zoho reconcile:** **cannot verify** from repo.

**Competitors on brand queries:** **cannot verify** (no extra API; auction fields already failed).

---

## 4. WordPress landing page

| URL | What the saved HTML shows | Still unknown |
|-----|---------------------------|---------------|
| `https://virtualcoworker.com/` | Historical Enabled Brand RSA | Tracking once? |
| `https://virtualcoworker.com/contact-us/` | “Free Consultation” Gravity Form. GTM `GTM-TTKNKT`. Employer-lean copy. | Form works desk+mobile today; gclid/UTM survive; fires once; Zoho source |
| `https://virtualcoworker.com/contact/` | Different footer “Contact Us” form — **not** the consultation CTA | Same |

Rebuild note: US WP has a dual-door to `.ph` (job-seeker leakage risk). Public HTML did **not** show an `AW-` Ads tag.

**Do not send Brand RSA to `/contact-us/` until the tracking/Zoho gate is true.** CSV RSA = homepage. Sitelink Contact = `/contact-us/` (not `/contact/`). Cold Core/Roles stay on `.app`.

---

## 5. Why TIS, not Max Conv / Max Clicks

- **Max Conv:** 16 untrusted conversions over two years. All-conversions was 8× larger. Not enough trusted signal.
- **Max Clicks:** current Brand CPC $1.74 is cheap. That buys clicks, not the top-of-page coverage Braden wants. CORE is already Max Clicks.
- **TIS · top of page · ~85% (80–90% band):** coverage objective. Not Absolute Top. Isolated budget.

---

## 6. Evidence-based settings (Paused CSV — George can change before Post)

| Setting | Value | Why this number — not invented from thin air |
|---------|--------|-----------------------------------------------|
| Campaign | `VC_US_S_BRAND` · Search only · US Presence · Paused | Isolated TIS + isolated budget |
| Ad group | `BRAND_CORE` | One AG |
| Daily budget | **$15** | Between current ~$1.24/day discovery and historical ~$18/day smear ($12,845 / ~2 years). Remnant $100 field is too big. **George sets the number before Post.** |
| Bid | Target Impression Share · **Top of page** · **85%** | Mid of the 80–90% band George asked for. Not 100% abs top. Set location/percent in Editor after import. |
| Max CPC cap | **$12** | Historical Brand avg CPC $11.33 (1,134 clicks). Current $1.74 is 5 clicks — too thin to cap TIS. Matches CORE’s $12 cap. Review Lost IS (Rank) after 2–3 live days. |
| Final URL | `https://www.virtualcoworker.com/` | Historical Brand RSA. Contact is a sitelink. |
| Match | Exact + one Phrase `"virtual coworker"`. No Broad. | Evidence-supported only |
| Goals | Campaign-specific. Do not attach CORE/ROLES goals. | TIS does not need junk Primary actions to launch |

**Keywords (Exact)**

- `[virtual coworker]` — live term + historical remnant
- `[virtualcoworker]` — current Brand_VC
- `[virtual coworker usa]` · `[virtual coworker staffing]` · `[virtual coworker reviews]` · `[virtual coworker pricing]` — historical remnant

Misspellings / extra intent terms stay out until search terms prove them.

**Negatives (MMC only, not Account Import):** jobs / careers / login / employee / payroll portal / application status / salary / apply / resume / PH job-seeker variants. Not the PM_* mega list. Bare `hiring` omitted (can be employer).

**Sitelinks (manual .com only):** Book Consultation → `/contact-us/` · How It Works · Services · About. No careers, login, quiz, `.app`, old subdomains.

**Call asset:** attach existing `(888) 964-8644` in Editor after import. No new number.

---

## 7. Campaign-specific goals (do not contaminate Core/Roles)

**Primary (only after `.com` is verified):**

- One WordPress employer-form conversion
- Qualified-duration call (60s) — existing US actions, **campaign-specific**
- Booked consultation when it exists and is trusted

**Secondary or excluded:** phone clicks · old thank-you · GA4 duplicates · job-seeker · engagement micros · legacy Zoho/Zapier · Job Orders / Placements until offline import is real

TIS does not bid to conversions. Do not promote junk to Primary just to launch.

**Zoho identifier if/when wired:** `utm_campaign` / campaign `vc_us_brand` · form `wordpress_contact_brand` · Market = US · Lead source = Google Ads Brand. **Cannot verify fields exist today.**

---

## 8. Success / stop (after Enable — not this week)

**Success:** Brand Search IS in the 80–90% top-of-page band at a controlled CPC · clean brand terms · verified `.com` employer conversion · Zoho can tell Brand from Core · no sitelink leakage · Core/Roles budgets untouched · Brand and non-brand reported apart.

**Stop or revise if:** CPC stays above the $12 cap with no coverage gain · spend hits ~$150 with no credible employer lead · traffic is mostly jobs/login/employee · `.com` double-counts · Zoho cannot mark Brand · Brand steals Core/Roles money · TIS bids irrationally.

---

## 9. Reporting split (must stay visible)

Last 7d, same window, **approximate** (Brand AG pull vs CORE campaign pull):

| | Impr | Clicks | CTR | CPC | Spend | Conv |
|--|------|--------|-----|-----|-------|------|
| **Brand** (`Brand_VC`) | 15 | 5 | **33.3%** | $1.74 | $8.68 | 0 |
| **Non-brand US** (CORE+ROLES minus Brand) | ~3,197 | ~338 | ~10.6% | ~$2.63 | ~$889 | — |
| **CORE mixed** (includes Brand) | 1,782 | 234 | 13.1% | $2.31 | $540 | — |

CORE CTR looks better than Roles because Brand is inside it. Always show **BRAND · NONBRAND · TOTAL**.

---

## 10. Editor files (Paused)

Rebuild: `python3 ads-launch/build_us_brand_campaign.py`

| File | Use |
|------|-----|
| `google-ads-editor-brand-us.csv` | Account Import — new **Paused** campaign |
| `google-ads-editor-brand-negatives-us.csv` | Keywords, Negative → Make multiple changes **only** |
| `google-ads-editor-brand-pause-core-ag-us.csv` | **Enable-day only.** Do not import now. Pauses `Brand_VC` so two brand systems do not bid against each other. Campaign Status blank (does not pause CORE). |

No Ads API mutate. No AU brand. No Braden email from this pass.
