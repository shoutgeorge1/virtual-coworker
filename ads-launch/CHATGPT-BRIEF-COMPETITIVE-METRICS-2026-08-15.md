# ChatGPT brief — VC Search competitive metrics (light Ads API pull)

_Pulled 2026-08-15T17:56 UTC · read-only · 2 GAQL calls (US customer 496-715-1855 + AU 573-539-1940) · complete days **Sat Aug 8 – Fri Aug 14** · no mutate · Brand deferred / not in this table_

**Ask:** Given these numbers, should we raise CPC caps, raise daily budgets, and/or switch Maximize Clicks → Maximize Conversions to get more auction coverage and conversion signal? Be conservative. Do not recommend Broad, Performance Max, or DSA. Do not invent competitor names (Auction Insights are not in this API). Any live change is Google Ads Editor / UI after George decides — not an API mutate.

---

## What is live (API, not notes)

All four Stage 1 campaigns are **Maximize Clicks** (`TARGET_SPEND`). Target CPA field is **$0**. They are **not** on Maximize Conversions.

| Campaign | Status | Bid strategy | Daily budget | API max CPC ceiling | Avg CPC (7d) |
|---|---|---|---:|---:|---:|
| VC_US_S_CORE | ENABLED | Maximize Clicks | **$150** | **$30** | $2.54 |
| VC_US_S_ROLES | ENABLED | Maximize Clicks | **$100** | **$30** | $3.61 |
| VC_AU_S_CORE | ENABLED | Maximize Clicks | **A$75** | **A$25** | A$3.41 |
| VC_AU_S_ROLES | ENABLED | Maximize Clicks | **A$50** | **A$25** | A$3.78 |

US combined cap **$250/day**. AU combined cap **A$125/day**. Do not mix USD and AUD.

Older operator notes said US CORE $15 / ROLES $12. **API now shows $30 / A$25.** Use the API ceilings.

---

## Competitive metrics (Search impression share)

Impression-weighted campaign Search IS. Competitor-domain Auction Insights **not available** via this API — do not invent who we lost to.

### Last 7 complete days (Aug 8–14)

| Campaign | Search IS | Lost to **rank** | Lost to **budget** | Top IS | Abs-top IS | Impr | Clicks | Spend | Ads conv (primary) | All conv |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| US Core | 29.9% | **38.8%** | 31.3% | 19.9% | 10.6% | 2362 | 278 | $705 | **1.0** | 2.0 |
| US Roles | 22.4% | **66.8%** | 10.8% | 13.7% | 10.0% | 1741 | 128 | $462 | **0** | 1.0 |
| AU Core | 33.2% | **35.0%** | 31.8% | 24.4% | 14.6% | 889 | 137 | A$467 | **0** | 0 |
| AU Roles | 26.6% | **46.9%** | 26.6% | 17.6% | 11.3% | 790 | 80 | A$302 | **0** | 0 |

US 7d spend **$1,167** vs $1,750 budget capacity (~67%). AU 7d spend **A$769** vs A$875 (~88%). Earlier days in the week were lighter; do not treat 7d as “we never hit budget.”

### Last 2 complete days (Aug 13–14) — current delivery

Budgets are **filling**. Rank loss is the hole.

| Campaign | Search IS | Lost to rank | Lost to budget | Avg CPC | Spend vs 2× daily budget |
|---|---:|---:|---:|---:|---|
| US Core | 29.6% | **58.7%** | 11.7% | $2.72 | $316 vs $300 |
| US Roles | 26.9% | **67.5%** | 5.6% | $4.26 | $209 vs $200 |
| AU Core | 34.5% | **50.1%** | 15.4% | A$2.97 | A$157 vs A$150 |
| AU Roles | 35.2% | **58.8%** | 6.0% | A$3.56 | A$96 vs A$100 |

Vs prior IS pull (complete days Aug 7–13): US Core was still **budget-heavy** (lost budget 39.1% / rank 29.7%). That has **flipped**. Last two days Core is rank-limited like Roles.

How to read the columns (plain):

- **Lost to budget** = Google would have shown the ad more, but the daily cap ran out. Raising budget buys more of the *same* auctions.
- **Lost to rank** = eligible, lost the auction (bid / expected CTR / landing / ad strength vs others). Raising budget does **not** fix this. Maximize Clicks with a high ceiling can still shop for cheap leftover clicks and skip expensive queries — that shows up here.

---

## Ads conversions vs sales activity (do not add these)

George is seeing ~**1 primary conversion** across US Core + Roles. API matches that: Core **1.0**, Roles **0**. All-conversions (includes non-primary) is only **2 + 1** US; AU **0**.

Sales side for the same Friday week (not Ads):

- **US sales ops** (Cheyenne, Mon Aug 10 – Fri Aug 14): **14 enquiries · 9 calls completed**. Labeled sources include 8 “Google Organic” — **0 of 18 US Zoho Sales Enquiries in that census have `utm_gclid`**. Do not treat email buckets and Zoho as additive. Do not tell Google that organic is paid.
- **AU** same week (Zoho census, not Holly’s labeled email): 13 enquiries · 2 discovery · 3 job orders.

That gap is expected during cold start: Maximize Clicks is sending traffic; the **Ads conversions column is not yet the business scoreboard**. Phone/thank-you/Calendly actions exist; Primary stack is meant to be 60s calls + thank-you, not leftover museum CRM. Zoho → Ads offline conversions are **deferred**.

Google’s Maximize Conversions / tCPA usually wants on the order of **15–30 conversions per month per campaign** (often more) before it has a stable learning signal. **1 in 7 days is not that.**

Locked cold-start stance (do not walk past this unless George explicitly overrides): keep **Maximize Clicks** while conversion definition is thin. Do not bid on Zoho Job Orders or old Zapier uploads. Do not make museum conversion actions Primary.

---

## Constraints for your recommendation

1. **Do not switch to Maximize Conversions now** unless you can show a conversion action that is (a) employer-true, (b) firing with click ID, (c) at enough volume. One Ads conversion is not enough; sales-ops 14 is a different dataset.
2. **CPC ceiling is already $30 US / A$25 AU** vs average CPC $2.50–$4.26. Argue carefully whether a still-higher ceiling would change Maximize Clicks behavior, or whether the strategy itself is filling cheap inventory.
3. **Roles budgets are not the bottleneck** (lost-to-budget 6–11%). Core 7d is mixed; Core last-2d is mostly rank.
4. Separate **US USD** and **AU AUD**. Four campaigns, not “both” lumped unless you mean US Core+Roles only.
5. Brand is deferred / paused. Do not center Brand, Target Impression Share brand defense, or “probe what’s still Enabled.”
6. No Broad, PMax, DSA. No Google Ads API mutations. If a change is worth doing, say “Editor / UI, George decides,” with one lever per campaign.

**Question to answer:** What is the smallest next lever (if any) to get more *useful* auction coverage this week — raise a budget, change Maximize Clicks behavior, wait for tracked conversions, or something else — without optimizing Google toward a fake or empty conversion number?
