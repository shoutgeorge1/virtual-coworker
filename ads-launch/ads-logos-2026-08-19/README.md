# Ads logos — checklist item 8 — 19 Aug 2026

Forbes, Google 5-star, Clutch, plus the new hopper marks from Media.

**Editor only. You Post. Do not upload with the Ads API. Do not change live campaigns from a script.**

Look first on X-ray: `xray/ads-logos.html`. After you look, add these as logos in Editor, then Post.

## Google Ads logo format (published — not a new invention)

- **Square logo (required):** 1:1. Min **128×128**. Recommended **1200×1200**.
- **Landscape logo (optional):** 4:1. Min **512×128**. Recommended **1200×300**.
- Typical Editor file types: PNG or JPG. Transparent PNG is the usual logo file.

This pack is **square logos only**. There is no 4:1 landscape file here.

## What to add in Editor

### US + AU — hopper marks (use as-is)

New marks from `xray/assets/media/hopper/`. **1024×1024 PNG, 1:1.** Above the 128 min. Below the 1200 recommendation. Usable — not recompressed.

| File | Pixels | Market |
| --- | --- | --- |
| `hopper-businesses-only.png` | 1024×1024 | US + AU |
| `hopper-you-interview.png` | 1024×1024 | US + AU |
| `hopper-dedicated-teammate.png` | 1024×1024 | US + AU |
| `hopper-14-years.png` | 1024×1024 | US + AU |

### US — trust badges

LP originals live in `source-lp/`. Three of four are **not 1:1** or sit well below 1200. **Do not invent a new badge.** Use the existing 1200×1200 white-pad PNGs already made 18 Aug (same marks) in `editor-ready/`.

| Add this in Editor | Pixels | Market | LP original | Original pixels | Note |
| --- | --- | --- | --- | --- | --- |
| `editor-ready/logo-forbes-navy.png` | 1200×1200 | US | `source-lp/badge-forbes-navy.webp` | 240×240 (1:1) | Original meets min square; small vs 1200. Use the pad. |
| `editor-ready/logo-google-5star-us.png` | 1200×1200 | US | `source-lp/badge-google-5star.webp` | 222×240 (not 1:1) | **Wrong ratio.** Needs a larger square export — pad already exists. |
| `editor-ready/logo-clutch-us.png` | 1200×1200 | US | `source-lp/clutch-us.webp` | 470×508 (not 1:1) | **Wrong ratio.** Needs a larger square export — pad already exists. |

### AU only — keep off US creatives

| Add this in Editor | Pixels | Market | LP original | Original pixels | Note |
| --- | --- | --- | --- | --- | --- |
| `editor-ready/logo-clutch-au.png` | 1200×1200 | **AU only** | `source-lp/badge-clutch-au.webp` | 222×240 (not 1:1) | **Wrong ratio.** Keep off US ads. |

## Do not

- Ads API upload / mutate
- Put Clutch AU (or any AU-only mark) on US ads
- Redesign or fake a badge
- Treat this folder as live — nothing is live until you Post in Editor
