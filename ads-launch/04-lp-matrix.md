# 04 — Landing page matrix

**Host (placeholder until custom domain):** `https://vision-three-alpha.vercel.app`  
**LP version:** `stage1-v5`  
**Engine:** `vision/config/categories.ts` + `MarketLanding`

---

## Routes

| Route | Market | Category | Form preselect | Phone |
|-------|--------|----------|----------------|-------|
| `/us` | US | generic (all roles) | none | **310-426-8776** (brief NA / env override) |
| `/au` | AU | generic (all roles) | none | **None** — form primary |
| `/us/digital-marketing` | US | digital-marketing | Digital marketing support | US phone |
| `/us/social-media` | US | social-media | Social media support | US phone |
| `/us/accounting` | US | accounting | Accounting support | US phone |
| `/us/bookkeeping` | US | bookkeeping | Bookkeeping support | US phone |
| `/us/administrative-support` | US | administrative-support | Administrative / VA support | US phone |
| `/us/customer-service` | US | customer-service | Customer service support | US phone |
| `/us/hr` | US | hr | HR support | US phone |
| `/us/recruitment` | US | recruitment | Recruitment support | US phone |
| `/us/sales` | US | sales | Sales support | US phone |
| `/au/{same 9 slugs}` | AU | same | same | **No phone** |

**Also retained:** `/us` `/au` generics.  
**Compat:** `/us?role=bookkeeping` → **308** `/us/bookkeeping` (middleware).  
**Legacy:** `/us/consult` `/au/consult` → redirect `#gate` (no demo booking page).

---

## Per-page content system

Each category supplies: title, meta description, H1 A/B, subhead A/B, primary CTA A/B, hero image A/B, benefits, FAQ, form role label.

Capture on submit: market, category, variant, UTMs, GCLID, WBRAID, GBRAID, referrer, landing URL, timestamps.

---

## Gate

1. Employer vs job seeker  
2. Job seeker → careers divert (**no** employer conversion)  
3. Employer → role chips (preselected on category) → details → submit  

Careers URL: `NEXT_PUBLIC_CAREERS_URL` or fallback `/ph` (**blocker** until real careers URL set).
