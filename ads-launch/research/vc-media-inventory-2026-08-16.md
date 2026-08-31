# Virtual Coworker media inventory — 16 Aug 2026

Purpose: authentic proof for **local paid-LP prototypes only**. No live `vision/public` adds. No competitor media. No personal employee social accounts.

Sources inspected (public / repo): `vision/public`, `ads-launch/assets`, live `virtualcoworker.app`, `virtualcoworker.com`, `virtualcoworker.com.au` (fetch timed out — treated as unavailable this pass), `virtualcoworker.com.ph`, official LinkedIn company page. Facebook and Instagram official URLs exist but **login-walled** to this crawler. YouTube: no official channel URL found in repo HTML or a working `@VirtualCoworker` handle (404). Did not scrape employee profiles.

Copy destination (mock-only): `ads-launch/mocks/assets/`.

Approval key: **known** = already on live paid `/us` `/au` or official brand files used in marketing; **likely** = company-published on .com / .ph / LinkedIn company page but ad-creative permission not separately confirmed; **unknown** = employee/candidate likeness — placeholder only.

| Local filename or source URL | What it shows | US/AU/PH | Dimensions / quality | Company-owned? | Ad-use approval | Recommended use | Permission concern |
|---|---|---|---|---|---|---|---|
| `ads-launch/mocks/assets/logo-vc.png` (from `vision/public/brand/logo-vc.png`) | VC wordmark | All | 320×100 PNG, logo quality | Yes | **Known** | All prototypes, nav | None |
| `ads-launch/mocks/assets/fonts/CenturyGothicPaneuropean*.woff2` | Live `/us` display font | All | woff2 | Yes | **Known** | Match live `/us`, not IBM Plex | None |
| `ads-launch/mocks/assets/people/va-us.jpg` | Existing paid-LP portrait (woman at desk) | US | 900×1350, usable | Yes (live `/us`) | **Known** (already paid LP) | Prototype A/C supporting image — **not** a third competing hero column | Person likeness already public on paid LP; do not crop into a fake “named candidate card” |
| `ads-launch/mocks/assets/people/va-au.jpg` | Same pattern, AU LP portrait | AU | 900×1350 | Yes (live `/au`) | **Known** | AU supporting image | Same |
| `ads-launch/mocks/assets/people/va-face-1.jpg` … `va-face-3.jpg` | Tight headshots already in brand | All | 480×480 | Yes (brand folder) | **Likely** | Small supporting faces only, not “available now” candidate tiles | Do not invent names, roles, or availability |
| `ads-launch/mocks/assets/people/trust-team-office.png` | Team/office activity (existing trust choice) | PH/all | 1536×1024, high | Yes | **Likely** | Prototype C “how we work / team” — not a fake office tour claim | People in frame unidentified; OK as “our team/office” only if VC already used this asset that way. Prototypes caption it as existing company photo. |
| `ads-launch/mocks/assets/people/trust-consult.png` | Consult / desk scene | All | 1536×1024 | Yes | **Likely** | C process/proof | Same |
| `vision/public/brand/hero-us-2026.jpg` | Wide US hero photo 1800×1200 | US | High | Yes | **Known** (OG image on `/us`) | Background-only if needed; C optional texture | Not copied if unused |
| `vision/public/brand/hero-au-2026.jpg` | Wide AU hero | AU | 1800×1200 | Yes | **Known** | AU C optional | Same |
| `vision/public/brand/vc-stop-va-v2.png` | Large stop-LP portrait | US | 1536×1024, 2MB | Yes | **Likely** (brand, stop LP) | Not used in these mocks (too “campaign poster”) | Avoid treating as a named hire |
| `ads-launch/mocks/assets/clients/client-good-co.png` | Good Co. mark | US | 1500×638 | Logo published by client/VC | **Known** (live TrustBand) | Logo strip | Do not imply Fortune 500 or endorsement beyond “teams we’re proud to work with” |
| `client-credit-card-compare.png` | Credit Card Compare | AU+US | Logo | Yes / live | **Known** | Strip | Same |
| `client-buzinga.png` | Buzinga Apps | AU+US | Logo | Yes / live | **Known** | Strip | Same |
| `client-proactive-media.png` | ProActive Media | AU+US | Logo | Yes / live | **Known** | Strip | Same |
| `client-learning-deli.png` | The Learning Deli | AU+US | Logo | Yes / live | **Known** | Strip + caption | Icon-only mark — keep caption |
| `client-recruitloop.png` | RecruitLoop | AU+US | Logo | Yes / live | **Known** | Strip | Same |
| `client-college-hunks.svg` (`vision/public/brand/trust/`) | College Hunks | US | SVG | Yes | **Known** | Optional; Kyrstin H. quote already used live | Keep quote text from Success Stories |
| `ads-launch/mocks/assets/clutch-us.webp` / `badge-google-5star.webp` / `badge-clutch-au.webp` | Rating badges | US/AU | Small webp | Yes | **Known** | Stars + rating. Print **Google 5.0 (39)** US / **4.8 (23)** AU; **Clutch 4.9 (7)** — do not invent counts | None |
| Press SVGs (`press-brw`, Startup Daily, Anthill, SMH, OA) | Featured-in marks from .com | All | Mixed | Yes (mirrored from VC library) | **Known** on .com | Prototype C footer/press row | Display only, no outbound |
| `ads-launch/mocks/assets/permission-unknown/talent-arvin.jpg` | Named PH staff (Arvin, Administration Officer) from `.com.ph` careers quotes | PH | 1460×1460 | Company-published on careers | **Unknown** for advertising | **Do not use in paid creative.** Inventory only | Employee likeness for ads not confirmed |
| `permission-unknown/talent-john.jpeg` | Named PH staff (John, Web Developer) from `.com.ph` | PH | 768×868 | Company-published | **Unknown** | Do not use | Same |
| Live quote text (Kyrstin H. / College Hunks; Laura W. / Good Co.; David Boyd; Logan Merrick) | Published success stories | US+AU | n/a | Company-published | **Known** (already on `/us`) | One quote in first viewport of A/B/C | Text only |
| Process copy | Consult → recruit/vet → you interview → we stay (payroll/HR/time tracker) | All | n/a | Yes | **Known** | All prototypes | No invented SLAs |
| Phones / NAP | US (888) 964-8644, 750 N San Vicente; AU 1300 886 740, York St, ABN 49 154 746 004 | US/AU | n/a | Yes | **Known** | Nav gold call button | Never invent numbers |
| Founded 2011 · 450K+ LinkedIn · 290K+ Facebook | Audience floors | All | n/a | LinkedIn live **453,979** (2026-08-16) supports 450K+ display floor | **Known** | Badges, not buttons that dump paid traffic onto LinkedIn | Facebook exact count still login-walled; keep approved floor 290K+ |
| Official LinkedIn `linkedin.com/company/virtualcoworker` | Company page, West Hollywood HQ, 2011, ~454k followers | US | Public | Yes | **Likely** for screenshots; **don’t harvest employee faces** | Proof of a real company; not candidate photos | Page says it is the only official LI. Do not use Braden/Niña/Caitlin personal posts as ads. |
| Official Facebook `facebook.com/virtualcoworkerinc` (also `/virtualcoworker`) | Company page | All | Login-walled 16 Aug | Yes | Not inspected this pass | Counts: keep 290K+ floor | Do not scrape posts |
| Official Instagram `instagram.com/virtualcoworker` | Company IG | All | Login-walled 16 Aug | Yes | Not inspected | Later, if George pulls stills | Do not scrape |
| YouTube | **No official channel URL confirmed this pass** (`@VirtualCoworker` 404; none in repo HTML) | — | — | Unknown | Unknown | Wishlist: video testimonials remain **not available** | Do not grab random PH VA YouTube |
| `.com` How it works + testimonial wall | Long company proof, role grid, Featured In | US mothership | HTML | Yes | **Known** for copy already in repo | Reference for C “full company” feel — do not import WP artwork blindly | `.com` still says “top 1%” in places — **do not copy that claim** onto `.app` prototypes |
| `.com.ph` | Job-seeker careers; staff quotes | PH | HTML | Yes | Job-seeker only | Job-seeker exit, never paid employer hero | Talent quotes are not employer ads |
| `.com.au` | Intended AU mothership | AU | **Fetch timed out this pass** | Yes | Not re-audited | Use `/au` + ABN from live app | Retry if needed; do not invent AU-only photos |
| Video testimonials (wishlist in `site.ts`) | Face + name + company + outcome | US | **None on disk** | n/a | Missing | Prototype C uses a **labeled placeholder**: “Video testimonials not in the library yet” | Do not fake a reel |
| Candidate availability cards | Ready-this-week VAs | — | **None approved** | n/a | Do not invent | Placeholder only if used: “No public candidate cards — you interview a shortlist after we recruit” | Copying OutsourcingSuccess-style fake Maria/Carla cards is forbidden |

## Gaps that actually matter

1. **No approved video** of a real client or a real introduction format for paid use.
2. **No extra authorized US client marks** beyond the current TrustBand set.
3. **Named PH staff portraits** exist on `.com.ph` but **ad permission is unknown** — prototypes do not use them as “meet your VA.”
4. **Social stills** (office, events, staff) live on LI/FB/IG but cannot be harvested from personal accounts and were login-walled on FB/IG this pass. George can export official page stills later if needed.
5. Live `/us` already has a **large portrait competing with the form**. We have faces. The gap is **composition + outcome**, not “we have no people.”

## What the prototypes are allowed to show

- Logo, live fonts, live portraits at **supporting** size, office/team still already in brand, existing client marks, existing quotes, Google/Clutch numbers as stored, 2011, US+AU offices, 888 / 1300, 450K / 290K floors, real four-step hiring process.
- Job-seeker routing to `virtualcoworker.com.ph`.
- Clearly labeled placeholders where permission is unknown (C video; no fake candidate grid).
