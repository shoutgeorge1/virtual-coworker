# 03 — Keyword + negative launch set

**Labeling:** Positive lists below are **curated launch candidates** from Editor archaeology (structure frequency) + pilot strategy docs — **not** ranked by clicks/cost.  
**Match at launch:** Exact only. Phrase = post search-term QA. Broad = never in v1.

Scratch dumps: `_scratch_keywords.json` · `_scratch_negatives.json` (do not upload blindly).

---

## A. Positives — Brand (both markets)

| Keyword | Match | US | AU |
|---------|-------|----|----|
| virtual coworker | Exact | ✓ | ✓ |
| virtualcoworker | Exact | ✓ | ✓ |
| virtual coworker usa | Exact | ✓ | |
| virtual coworker australia | Exact | | ✓ |
| virtual coworker staffing | Exact | ✓ | ✓ |
| virtual coworker pricing | Exact | ✓ | ✓ |
| virtual coworker reviews | Exact | ✓ | ✓ |

Optional Phrase after QA: `"virtual coworker"` only if Exact is clean and volume is tiny.

---

## B. Positives — Core · Hire VA PH (`Hire_VA_PH`)

Employer-leaning Exact set (curated; dropped job/home-based/part-time variants that appeared as positives in old accounts):

```
[hire virtual assistant philippines]
[hire a virtual assistant in the philippines]
[hire filipino virtual assistant]
[hire filipino va]
[hiring virtual assistant philippines]
[filipino virtual assistant]
[filipino virtual assistants]
[virtual assistant philippines]
[philippines virtual assistant]
[virtual assistant company philippines]
[virtual assistant companies philippines]
[virtual assistant services philippines]
[outsource virtual assistant philippines]
[hire va philippines]
[filipino va]
[va philippines]
[philippines va company]
[hire offshore virtual assistant]
[offshore virtual assistant philippines]
```

---

## C. Positives — Core · Hire VA General (`Hire_VA_General`)

Keep tighter than old accounts — prefer hire/company/agency language:

```
[hire virtual assistant]
[hire a virtual assistant]
[hiring a virtual assistant]
[virtual assistant for business]
[virtual assistant company]
[virtual assistant agency]
[virtual assistant services]
[offshore virtual assistant]
[remote virtual assistant for business]
[hire remote virtual assistant]
[virtual staffing company]
[virtual assistant recruitment]
[outsource virtual assistant]
[dedicated virtual assistant]
```

**Watchlist (Exact only if search terms prove employer):** `[virtual assistant]` · `[virtual assistants]` — high dual-intent; add later with heavier negatives, not day one if Core PH is live.

---

## D. Positives — Role (≤3 campaigns)

### Bookkeeping

```
[virtual bookkeeper philippines]
[hire virtual bookkeeper philippines]
[philippines bookkeeping outsourcing]
[outsource bookkeeping philippines]
[filipino bookkeeper]
[hire filipino bookkeeper]
[virtual bookkeeping philippines]
[offshore bookkeeper]
```

### Executive Assistant

```
[hire executive assistant philippines]
[filipino executive assistant]
[virtual executive assistant]
[hire virtual executive assistant]
[offshore executive assistant]
```

### Social Media VA

```
[social media virtual assistant]
[hire social media virtual assistant]
[social media manager philippines]
[filipino social media manager]
[social media va philippines]
```

### Deferred roles (do not launch v1)

Web/dev · graphic design · CSR/tech support · content writer · lead gen · recruitment assistant — large Editor presence, higher dual-intent / portfolio spray risk.

---

## E. Negatives — shared lists (campaign-level apply to Core + Role; Brand gets jobseeker + platforms)

### `VC_SHARED_NEG_jobseeker` (Phrase unless noted)

From Editor high-frequency job-seeker negatives + pilot list — **curated**:

```
job
jobs
salary
salaries
wage
pay rate
career
careers
apply
application
resume
cv
employment
intern
internship
hiring me
i need a job
work from home
wfh
remote job
job description
job listings
indeed
linkedin jobs
glassdoor
how to become
no experience
online jobs
onlinejobs
onlinejobs.ph
virtual assistant jobs
virtual assistant job
virtual assistant careers
virtual assistant salary
apply as virtual assistant
```

**Do not** add `hire` / `hiring` as account-wide negatives on employer campaigns.

### `VC_SHARED_NEG_info`

```
what is
how to
tutorial
course
courses
training
certification
template
example
examples
definition
meaning
diy
```

### `VC_SHARED_NEG_platforms` (Phrase/Exact mix)

```
upwork
fiverr
freelancer
onlinejobs
onlinejobs ph
wishup
athena
boldly
myoutdesk
zirtual
magic
bruntwork
```

**Note:** Platform/competitor negatives protect Core; Brand may omit competitor brand names if trademark policy requires — confirm with Braden. Large competitor **conquest campaigns** stay deferred; negatives ≠ conquest.

### `VC_SHARED_NEG_junk` (light)

```
free
cheap
cheapest
torrent
reddit
youtube
pdf
```

Review `free`/`cheap` after 14 days — can block price-shopping employers; start Phrase, not Broad account-level if unsure.

### Brand-only extras

Negative Exact any role-job spam that matched brand+job in search terms (add from report). Keep Brand negatives thinner than Core.

---

## F. What not to import from Editor

| Editor artifact | Why skip |
|-----------------|----------|
| `PM_Generic Non-Qualified` (~3496) | Opaque mega-list; may block good queries |
| `geo_irrelevant` scratch bucket | Mining mislabeled PH hire terms as geo |
| Positives containing `jobs`, `home based`, `part time … jobs` | Dual-intent / job-seeker |
| Broad / modified broad syntax (`+virtual +assistant`) | v1 Exact only |
| Competitor Exact farms | Deferred strategy |

Useful archaeology only: `PM_Job Seekers`, `Jobseekers`, informational lists — **diff against** curated lists above, then merge.

---

## G. Search-term ops (first 14 days)

Daily (or every 48h if volume low):

1. Add job-seeker terms → `VC_SHARED_NEG_jobseeker`  
2. Promote clean Exact variants into Core/Role  
3. Pause KW with pure job-seeker queries  
4. Never expand to Broad to “fix” low volume  

**Owner:** George · **Quality flag:** Braden (is this an employer?)
