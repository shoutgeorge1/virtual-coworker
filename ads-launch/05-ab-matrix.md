# 05 — A/B matrix

**Assignment:** middleware cookie `vc_ab_variant` = `a`|`b` · ~50/50 from seed when unset  
**QA override:** `?variant=a` or `?variant=b` (sets cookie)  
**SSR:** server reads same cookie via `resolveLpVariant` → **no hydration mismatch**  
**Persist:** cookie 90 days · attribution session stores variant  
**Capture:** submit payload + dataLayer events include `variant`

---

## What differs by variant

| Element | Variant A | Variant B |
|---------|-----------|-----------|
| H1 | Category/market hire framing (“Hire Philippines {role}…”) | Capacity / staffing-partner framing |
| Subhead | “Tell us the role…” shortlist language | “Not a freelance marketplace…” partner language |
| Primary CTA | Tell us who you need → | Start your hiring request → / Request a hiring shortlist → |
| Hero image | Category-relevant asset | Alternate talent/team asset |

Generic `/us` `/au` still assign a variant (affects sticky/form CTA defaults; H1 uses market headline).

---

## Events carrying variant

- `employer_gate_selected`
- `employer_form_started`
- `employer_inquiry_submitted`
- `phone_cta_clicked` (US only when phone shown)

---

## What A/B is **not**

- Not a server experiment platform  
- Not multivariate beyond A/B  
- Not proof of lift until GTM/GA4 wired and sample size exists  
