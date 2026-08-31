# VC_US_S — Job-seeker negatives to add (2026-08-07)

**API:** 1 read-only `search_term_view` call (`TODAY` only). No writes.

**Why this exists:** Today ~**$66 / 20 clicks** on clear job-seeker queries (≈ half of USA Search spend). Top leaks: `virtual assistant jobs`, `virtual assistant jobs remote`, WFH appointment-setter variants, `va jobs`, `virtual assistant careers`, `remote job philippines`. Many of these already sit in the Stage1 Editor CSV as campaign negatives — **they are not stopping live traffic**, so add them to your **shared negative group** (or confirm the list is applied to CORE + ROLES).

**Do not add:** `hire`, `hiring`, bare `remote`, bare `work`, bare `home`, bare `staffing`, bare `assistant`.

**Match types for shared list**

| Shape | Match | Why |
|-------|-------|-----|
| Single root (`job`, `jobs`, `career`…) | **Broad** | Catches any query containing that word (negatives do **not** expand to close variants — keep both singular + plural) |
| Multi-word (`work from home`, `job board`…) | **Phrase** | Safer; blocks the phrase in any query |
| One-off junk queries | **Exact** | Optional; Broad/Phrase roots usually enough |

Raw pull: `_today_search_terms.json`

---

## A. Must-add roots (Broad) — paste these first

```
job
jobs
career
careers
salary
salaries
wage
wages
resume
cv
employment
internship
intern
vacancy
vacancies
indeed
glassdoor
jobstreet
unemployment
```

## B. Must-add phrases (Phrase) — today’s leaks + high-yield

```
work from home
from home
at home
wfh
job board
job boards
job listing
job listings
job opening
job openings
entry level
no experience
part time
full time
looking for a job
looking for work
i need a job
hiring me
how to get a job
how to find a job
how to become
become a
work as
apply now
apply as
apply to be
job description
remote job
remote jobs
online job
online jobs
freelance job
freelance jobs
virtual assistant jobs
virtual assistant job
virtual assistant careers
virtual assistant career
virtual assistant salary
va jobs
va job
va careers
va career
va salary
job board
positions
```

## C. Role / WFH job-seeker phrases (Phrase) — seen live or classic VA waste

```
work from home appointment setter
appointment setter work from home
appointment setter from home
appointment setter jobs
work from home customer service
customer service work from home
work from home virtual assistant
virtual assistant work from home
work from home administrative assistant
administrative assistant jobs
administrative assistant jobs remote
remote assistant jobs
remote executive assistant position
virtual assistant positions
virtual assistant apply
virtual assistant apply now
find a virtual assistant job
freelance virtual assistant jobs
online job virtual assistant
online jobs va
remote job virtual assistant
remote virtual assistant jobs
virtual assistant jobs remote
virtual assistant job remote
virtual assistant jobs near me
digital assistant remote jobs
remote job philippines
social media assistant jobs
online social media manager jobs
personal assistant job
personal assistant jobs
bookkeeper jobs
bookkeeping jobs
customer service jobs
customer service remote jobs
```

## D. Boards / marketplaces / “looking for work” language (Phrase or Broad where single)

**Broad**

```
onlinejobs
seek
ziprecruiter
monster
careerbuilder
simplyhired
```

**Phrase**

```
onlinejobs ph
onlinejobs.ph
online jobs ph
online jobs philippines
linkedin jobs
upwork jobs
fiverr jobs
jobstreet philippines
indeed virtual assistant
```

## E. Extra comprehensive roots / phrases (Phrase unless noted)

Use these if you want the list **fat** (still job-seeker-safe):

**Broad**

```
applicant
applicants
recruiter for me
jobseeker
jobseekers
job seeker
job seekers
```

**Phrase**

```
looking for employment
seeking employment
seeking a job
need a job
want a job
get hired
get a job
find a job
find work
side hustle
make money online
earn money online
work at home
working from home
home based job
home based jobs
work from home job
work from home jobs
wfh job
wfh jobs
part time job
part time jobs
full time job
full time jobs
temp job
temp jobs
contract job
gig work
gigs
open roles
open positions
now hiring me
submit resume
submit my resume
upload resume
cover letter
interview tips
job interview
careers page
join our team
we are hiring me
```

*(Skip any line that feels wrong for your list UI — roots in A+B already do most of the work.)*

---

## F. Today’s search terms that drove the spend (for your eyes)

| Term | Cost | Clicks | Notes |
|------|------|--------|-------|
| virtual assistant jobs | $22.19 | 7 | #1 job leak |
| virtual assistant jobs remote | $9.04 | 3 | |
| work from home appointment setter | $6.79 | 2 | |
| appointment setter work from home | $4.26 | 1 | |
| virtual assistant job board | $4.24 | 1 | |
| appointment setter from home | $4.22 | 1 | needs **from home** Phrase |
| va jobs | $4.20 | 1 | |
| virtual assistant careers | $4.06 | 1 | |
| digital assistant remote jobs | $2.43 | 1 | |
| virtual assistant job | $2.37 | 1 | |
| remote job philippines | $2.35 | 1 | |

Also still bleeding (not job-seeker — separate sniper): **`va workers ph` ~$37 / 22 clicks**. Keep Exact sniper on that; don’t Broad `workers`.

---

## G. Leave alone (employer / dual-intent)

Do **not** negative these from today’s report without a second look:

- `virtual assistant hiring`, `hiring va`, `remote staffing agency/agencies`
- bare `remote executive assistant`, `remote appointment setter`, `virtual assistant talent`
- bare `virtual assistant`, `remote virtual assistant`, `filipino accountant near me`

---

## One UI step

In Google Ads → **Tools → Shared library → Negative keyword lists** → open your job-seeker list → **Add keywords** → paste **section A (Broad)** first → save → then paste **section B (Phrase)** → confirm the list is attached to **VC_US_S_CORE** and **VC_US_S_ROLES**.
