# VC_US_S_🚫_Sniper

Logical / Ads list name for **sniper** negatives on live USA Search (**CORE + ROLES**).

## Naming convention

| Layer | Name | Notes |
|-------|------|-------|
| **Ads list / Comment label** | `VC_US_S_🚫_Sniper` | Emoji is intentional — scan-friendly in Editor Comment filter / Shared library if you create one |
| **Repo files (ASCII)** | `VC_US_S_Sniper_Negatives.csv` · `VC_US_S_Sniper_Negatives.md` | No emoji in filenames (scripts/shell-safe) |
| **Retired name** | `VC_US_S_Negatives_Sniper` | Thin starter — superseded |

Pattern: `VC_{MARKET}_S_🚫_Sniper` — market + Search + sniper cohort. Do **not** reuse for Broad Stage1 blobs or `PM_*` mega lists.

If Google Ads Shared library rejects the emoji when creating a real shared list, create ASCII `VC_US_S_Sniper_Negatives` and keep the emoji in this doc / Comment on campaign negatives.

**API writes = no. Editor = yes.**

## Files

- Import CSV: [`VC_US_S_Sniper_Negatives.csv`](./VC_US_S_Sniper_Negatives.csv)
- Account: USA `496-715-1855`
- Campaigns: `VC_US_S_CORE`, `VC_US_S_ROLES`
- Shape: campaign-level negatives (`Criterion Type = Campaign negative`)
- Label: Comment contains `VC_US_S_🚫_Sniper`

## Why the original 5 were thin (honest)

The starter `[va workers ph]`, `[virtual assistant work]`, `[i need a va careers]`, `[virtualstaff ph]`, `[virtual staff ph]` was assembled in a hurry on 2026-08-07 after George reported Washington bot clicks and asked for a sniper list **now**. Repo history:

1. **`va workers ph`** — flipped twice: first mistaken as job-seeker → Broad `workers` (wrong); George corrected as employer shorthand; then George killed Exact after ~50% Washington bot signal. Starter kept the kill with almost no write-up.
2. **`virtual assistant work` / `i need a va careers`** — flagged morning-of as quiet junk; zero spend at first look; tossed into the starter without a full ST pass.
3. **`virtualstaff ph` / `virtual staff ph`** — real live competitor clicks, but the starter stopped at those two spellings and ignored the rest of the VirtualStaff / brand-of-other cluster in historical ST.

No deep mine of `audit-data/performance/search_terms_usa_*.csv`, evidence kills, or Stage1 gaps happened on that first pass. This rewrite fixes that.

## Sources mined (0 API calls)

- `xray/data/executive-snapshot.json` — live VC_US LAST_7_DAYS top ST (48 unique; top 15 stored)
- `audit-data/performance/search_terms_usa_4967151855_2026-08-05.csv` — full historical USA ST
- `ads-launch/_evidence_search_terms.json` kills + `historical-performance-summary.json` waste
- `ads-launch/google-ads-editor-import-us.csv` — existing Stage1 Broad + `VC_Neg_JobSeekers_Live` Phrase (avoid dumb duplicates)
- Chat/repo decisions: bot kill on `va workers ph`; leave bare `workers` alone

## Competitor / brand-of-other hits

| Brand / query | Why it matters | In this sniper? |
|---------------|----------------|-----------------|
| **VirtualStaff.ph** (`virtualstaff ph`, `virtual staff ph`, …) | Live VC_US clicks + heavy hist spend | **Yes** — Exact variants + Phrase `virtualstaff` |
| **VirtualStaff365 / Finder** | Hist competitor spend | **Yes** — Exact compact forms |
| **20four7VA, Pearl Talent, GetMagic, Time Etc** | Hist competitor; **missing** from Stage1 Broad blob | **Yes** — Exact |
| **Remote Coworker** | Brand-of-other / name confusion vs Virtual Coworker | **Yes** — Exact |
| Bruntwork, MyOutDesk, Hello Rache, Wing, Wishup, Athena, Boldly, Upwork, Fiverr, OnlineJobs, VirtueStaff, Virtual Staff Finder | Hist waste | **No** — already Stage1 Broad campaign negs |

## Sniper terms (21 unique × 2 campaigns)

| Term | Match | Reason | Source |
|------|-------|--------|--------|
| `[va workers ph]` | Exact | Bot/spam click pile (~50% Washington); George kill 2026-08-07 — Exact only, not bare workers | live ST (exec snapshot) + judgment |
| `[va worker ph]` | Exact | Singular variant of the bot/spam query pattern | judgment (semantic) |
| `[va workers philippines]` | Exact | Same bot/spam pattern with PH spelled out | judgment (semantic) |
| `[virtual assistant work]` | Exact | Job-seeker intent — looking for VA work, not hiring | live ST (exec / Aug 7 sniper) |
| `[virtual assistants work]` | Exact | Plural job-seeker variant of virtual assistant work | judgment (semantic) |
| `[i need a va careers]` | Exact | Job-seeker / careers query (not employer hire) | live ST (Aug 7 sniper) |
| `[i need a va career]` | Exact | Singular careers job-seeker variant | judgment (semantic) |
| `[virtualstaff ph]` | Exact | Competitor brand VirtualStaff.ph — brand-of-other | live ST + hist USA ST (~$2.4k) |
| `[virtual staff ph]` | Exact | Competitor brand spaced variant | live ST + hist USA ST (~$1.7k) |
| `[virtualstaffph]` | Exact | Competitor brand concatenated typo/variant | hist USA ST |
| `[https www virtualstaff ph]` | Exact | Competitor URL typed as search query | hist USA ST |
| `[virtualstaff365]` | Exact | Competitor brand VirtualStaff365 | hist USA ST |
| `[virtual staff 365]` | Exact | Competitor VirtualStaff365 spaced variant | hist USA ST |
| `[virtualstafffinder]` | Exact | Competitor Virtual Staff Finder compact form (spaced form already Stage1 Broad) | hist USA ST |
| `"virtualstaff"` | Phrase | Competitor brand root — Phrase catches login/careers/reviews long-tail without bare 'virtual staff' employer language | hist USA ST + judgment |
| `[20four7va]` | Exact | Competitor brand 20four7VA — not in Stage1 Broad blob | hist USA ST |
| `[pearl talent]` | Exact | Competitor brand Pearl Talent — not in Stage1 Broad blob | hist USA ST |
| `[getmagic]` | Exact | Competitor brand GetMagic — not in Stage1 Broad blob | hist USA ST |
| `[get magic]` | Exact | Competitor GetMagic spaced variant | hist USA ST |
| `[time etc]` | Exact | Competitor brand Time Etc — not in Stage1 Broad blob | hist USA ST |
| `[remote coworker]` | Exact | Brand-of-other / confusion with Virtual Coworker (not our brand) | hist USA ST |

## Deliberately NOT negatived

| Term / cluster | Why leave it |
|---------------|--------------|
| Bare **`workers`** / **`ph`** | Blocks employer shorthand; George corrected this |
| Bare **`virtual staff`**, **`virtual staffing`**, **`virtual staffing agency`** | Employer language — would kill good hire intent |
| **`remote staffing agency/agencies`**, **`virtual bookkeeper`**, **`virtual assistant business`**, **`virtual assistant`**, hire/Filipino/PH VA keepers | Live or hist employer converters |
| Ambiguous **`administrative assistant remote`**, bare **`remote customer service…`** | Watch list — not clear junk yet |
| Cost / pricing / reviews **without** a competitor name | Held out pre-launch (employer research); competitor-named reviews stay Stage1 |
| Full WFH / `work as` cohort | Already `VC_Neg_JobSeekers_Live` Phrase |
| Stage1 Broad competitor blob (Bruntwork, OnlineJobs, …) | Already in main US import — don’t fatten sniper |

## API call count

**0** — built from repo ST dumps + Editor CSV negatives. No GAQL.

## Import → review → Post

1. Google Ads Editor → USA (`496-715-1855`) → **Get recent changes** (pull only).
2. **Import** `ads-launch/VC_US_S_Sniper_Negatives.csv`.
3. Filter Comment for `VC_US_S_🚫_Sniper` — confirm only CORE + ROLES.
4. **Post** when it looks right. Import ≠ live until Post.
5. Optional later: create Shared library list named exactly `{LIST}` and attach to CORE+ROLES — same terms.

If a button label doesn’t match your Editor build, send a screenshot — don’t guess.

