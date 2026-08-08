# Landing-page image choices — LIVE

Generated via Cursor **`GenerateImage`** (same tool as prior set — not a separate OpenAI API call).

Experiment: `role_imagery` in `lib/experiments.ts`  
Force: `?vc_exp=role_imagery&vc_var=a|b`

**Rule:** every `/services` title gets a **unique** image — no two titles share a src.

Minimal A/B only: **one default + one challenger** — no extra experiments.

---

## Live defaults (arm A) — unique per title

| Title | File | Routes |
|-------|------|--------|
| Digital Marketing | `public/roles/marketing-v2.png` | `/services` + `/us\|au/digital-marketing` |
| Social Media | `public/roles/marketing-a.png` | `/services` + `/us\|au/social-media` |
| Accounting | `public/roles/accounting-v2.png` | `/services` + `/us\|au/accounting` |
| Bookkeeping | `public/roles/bookkeeper-v2.png` | `/services` + `/us\|au/bookkeeping` |
| Administrative Support | `public/roles/admin-a.png` | `/services` + `/us\|au/administrative-support` |
| Customer Service | `public/roles/customer-service-v2.png` | `/services` + `/us\|au/customer-service` |
| Human Resources | `public/roles/hr-v3.png` | `/services` + `/us\|au/hr` |
| Recruitment | `public/roles/sales-a.png` | `/services` + `/us\|au/recruitment` |
| Sales | `public/roles/sales-v2.png` | `/services` + `/us\|au/sales` |
| Late trust | `public/trust/choices/trust-consult.png` | Market LPs (when shown) |

## Challenger set (arm B) — also unique per title

| Title | File |
|-------|------|
| Digital Marketing | `public/roles/marketing-b.png` |
| Social Media | `public/roles/marketing-a.png` |
| Accounting | `public/roles/bookkeeper-b.png` |
| Bookkeeping | `public/roles/bookkeeper-a.png` |
| Administrative Support | `public/roles/admin-b.png` |
| Customer Service | `public/brand/support.jpg` |
| Human Resources | `public/brand/ea.jpg` |
| Recruitment | `public/roles/sales-b.png` |
| Sales | `public/brand/talent-john.jpeg` |
| Late trust | `public/trust/choices/trust-team-office.png` |

Kept on disk (not deleted): `talent-arvin.jpg`, `va-face-*`, `marketing.webp`, `trust-company.png`, etc.

---

## Where they appear

- Category LP heroes (`/us|au/{category}`) via `config/role-imagery.ts` + `RoleHeroCard`
- Services grid portraits via `ServicesRoleGrid` (one thumb per title)
- Gray client logos / TrustBand strip unchanged

## Ads

Search Stage 1 does **not** need these in Ads yet. Assets staged under `ads-launch/assets/role-portraits/` for later Editor / Display / PMax manual upload — **never** via Ads API mutate.
