# Book consultation sitelink — 2026-08-27

**Status:** Booking pages live. Editor CSV ready. Show X-ray before import.

**Live pages**
- https://www.virtualcoworker.app/us/book
- https://www.virtualcoworker.app/au/book

**Calendly**
- US: https://calendly.com/cheyenne-virtualcoworker/30min
- AU: https://calendly.com/apac-virtualcoworker/30min

**Sitelink copy**
- Link text: Book a Consultation
- Description 1: Skip the form
- Description 2: Pick a time with our team

**Editor CSVs (add-only, Campaign Status blank)**
| File | Account |
|------|---------|
| `ads-launch/google-ads-editor-sitelink-book-us.csv` | USA `496-715-1855` |
| `ads-launch/google-ads-editor-sitelink-book-au.csv` | AU `573-539-1940` |

Campaigns: `VC_*_S_CORE` + `VC_*_S_ROLES` only. Not Brand. Not account-level. No Ads API.

**X-ray:** https://vc-xray.vercel.app/book-sitelink.html

**Ash / Raffie still owns:** Calendly → Zoho CRM create/update for bookings that skip the LP form (hidden fields / automation). App only fires `calendly_booking_complete` to the dataLayer.
