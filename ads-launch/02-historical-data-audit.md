# 02 — Historical data audit

**Sources:** `audit-data/performance/*_2026-08-05.csv` (UTF-16 LE, tab-separated Editor exports)  
**Window:** ~2024-08-01 → 2026-08-04  
**Machine summary:** `ads-launch/historical-performance-summary.json`  
**Re-run:** `python3 ads-launch/analyze_historical_performance.py`

---

## Honesty first

| Metric | Meaning |
|--------|---------|
| **Conversions** | Account primary conversion column in export — **not** proven job orders |
| **All conv** | Broader conversion set — **≠** Conversions |
| **Job orders / placements** | **Not present** in these exports — do not equate |
| ST vs campaign totals | Search-term cost usually **&lt;** campaign cost (missing ST rows, PMax/DSA mix) |

---

## Raw vs deduped counts

### Dedupe method

1. Normalize Search term: casefold + collapse whitespace.  
2. Drop rows with **identical** metric tuple `(Impr., Clicks, Cost, Conversions, All conv)` **and** same Campaign + Ad group + normalized Keyword.  
3. Rationale: Editor Exact / close-variant duplicate rows often repeat the same metrics for the same term binding.  
4. When metrics **differ**, keep all rows (different campaigns can share a term).

### Counts

| Account | Raw ST rows | Deduped ST rows | Dropped identical dupes | Unique normalized terms |
|---------|------------:|----------------:|------------------------:|------------------------:|
| USA `496-715-1855` | **66,869** | **66,465** | **404** | **39,106** |
| AU `573-539-1940` | **26,211** | **26,132** | **79** | **16,931** |

---

## Campaign totals (export)

| Account | Cost | Clicks | Conversions | All conv |
|---------|-----:|-------:|------------:|---------:|
| USA | **$723,838.59** | **87,060** | **2,597.32** | **4,629.39** |
| AU | **$457,489.46** | **49,457** | **1,412.66** | **3,505.46** |

**All conv ≫ Conversions** in both accounts — treating “conversions” as job orders would be false.

---

## Prior benchmark validation (v4 FULL-BUILD-REPORT cites)

| Metric | Prior cite | Actual | Delta |
|--------|-----------:|-------:|------:|
| USA cost | ~$724k | $723,838.59 | **0.0%** |
| USA clicks | ~87k | 87,060 | **0.1%** |
| USA conversions | ~2,597 | 2,597.32 | **0.0%** |
| USA ST raw | ~66.9k | 66,869 | **0.0%** |
| AU cost | ~$457k | $457,489.46 | **0.1%** |
| AU clicks | ~49k | 49,457 | **0.9%** |
| AU conversions | ~1,413 | 1,412.66 | **0.0%** |
| AU ST raw | ~26.2k | 26,211 | **0.0%** |

**Cause of any micro-diff:** rounding / prior “~” approximation — not a different export window.

---

## Campaign pattern (do not clone)

Worst CPA traps (from metrics): DSA generic catch-alls and thin `PM_*_RSA_*` role/pain/competitor farms.  
Better context cores (still not proof of Stage 1 quality): Brand Search, SKAG VA / specific services — used as architecture hints only.

See `03-search-term-category-findings.md` for keep/kill tables with limitations.
