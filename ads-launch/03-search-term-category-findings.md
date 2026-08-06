# 03 — Search-term / category findings

**Evidence:** Editor ST exports (UTF-16) · aggregated after dedupe · see `historical-performance-summary.json`  
**Limitation:** Classification is rule-based on term text + metrics; Editor “Conversions” are **not** job orders. Frequency ≠ quality.

---

## Category routing map (Stage 1)

| Category slug | Primary ST signals |
|---------------|-------------------|
| `administrative-support` | virtual assistant, hire VA, PH/filipino VA, EA |
| `digital-marketing` | marketing VA, digital marketing VA/manager PH |
| `social-media` | social media manager philippines, filipino SMM |
| `bookkeeping` | philippines bookkeeper, bookkeeper philippines |
| `accounting` | accounting outsourcing philippines |
| `customer-service` | customer service virtual assistant |
| `sales` | sales VA, lead generation VA, appointment setter PH |
| `hr` | human resources VA (thin ST) |
| `recruitment` | recruitment VA (near-zero ST — curated only) |

---

## KEEP examples (employer intent → package)

Metrics are from exports (USA+AU aggregated in prior v4 mining; re-validated present). Not invented.

| Search term | Why keep | Package home |
|-------------|----------|--------------|
| virtual assistant / hire virtual assistant | High employer volume + conv | Core + Admin |
| virtual assistant philippines / filipino VA | PH staffing intent | Core + Admin |
| how to hire a virtual assistant | Converting employer intent — **not** negatived | Core / Admin |
| social media manager philippines | Role + geo | Social |
| virtual marketing assistant | Role VA | Digital |
| philippines bookkeeper | Role + geo | Bookkeeping |
| lead generation virtual assistant | Sales support | Sales |
| customer service virtual assistant | Role VA | CS |
| philippines accounting outsourcing | Outsource intent | Accounting |

**Explicitly not kept as positives:** bare `social media manager` (no PH/hire/VA), competitor conquest brands, `free virtual assistant`, job-seeker variants, medical/tech.

---

## KILL / NEGATIVE examples (real waste)

| Cluster | Why kill | Treatment |
|---------|----------|-----------|
| onlinejobs ph (+ pricing) | Marketplace / wrong funnel | Negated |
| free VA · reviews · cost/pricing · top 10 | Research / junk | Negated |
| VA jobs / salary / careers | Job seeker | Negated |
| work from home / wfh (bare) | Fluff | Negated |
| asistente virtual / LATAM geos | Wrong geo language | Negated |
| hellorache · wing assistant · online ph | DSA bleed | Negated |
| upwork / fiverr / bruntwork… | Platforms / competitors | Negated |

**Intentionally not negatived:** bare `hire` / `hiring`; `how to hire a virtual assistant`.

---

## Class mix (unique normalized terms after dedupe)

See JSON `usa.class_counts` / `au.class_counts`. Large `other` bucket is expected — long-tail noise. Stage 1 package does **not** bid on unclassified junk.

---

## Evidence limitations (ChatGPT audit note)

1. ST rows missing for some spend → keep/kill tables understate total waste/opportunity.  
2. Conversions inflated vs business outcomes (All conv even higher).  
3. HR/recruitment thin — keywords curated, not “proven winners.”  
4. Brand terms converting historically ≠ proof current microsite converts — tracking was fragmented across WP/try.
