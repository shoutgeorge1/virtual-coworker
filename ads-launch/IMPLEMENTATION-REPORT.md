# Stage 1 implementation report (short)

Shipped the smallest safe paid machine: US/AU employer LPs with inline gate, server-validated leads, Stage 1 dataLayer events, paused Editor import, and one launch-control page.

## Built

- `vision/` `/us` + `/au` employer LPs (inline gate, short form, thank-you after server accept)
- `/api/lead` protections: honeypot, validation, min time, rate limit, duplicate window, reject logging
- Attribution: GCLID/GBRAID/WBRAID/UTMs/LP version/market/referrer
- `ads-launch/` paused Editor CSV + launch sheet
- `xray/launch-control.html` single control center

## Corrected facts

Enabled brand ads in Editor exports point to **WordPress**, not try.* (try.* ads paused; AU try.* also disapproved on enabled campaign). Docs updated.

## Not done (intentionally)

No live Ads/GTM/Zoho/CallRail/DNS mutations · no PMax/broad/DSA · no quiz/modal gates · no role campaigns enabled · no invented phones/pricing.
