# Tonight handoff — Stage 1 activation priority flip

**Date:** 2026-08-05  
**Branch:** `vision-demo`  
**Package:** `stage1-v7` · `ads-launch/google-ads-editor-import.csv` (unchanged — still all Paused)

---

## 1. What changed this pass

George corrected phased activation. **No v8 CSV regen.** Docs + Launch Control + DECISIONS only.

**Wrong (old):** Enable Core first → Digital/Social/Admin; hold accounting/books/CS/HR/recruitment/sales.  
**Right (locked):** Phase by **intent quality** — PH/Filipino/offshore long-tail Exact first across Core **and** Roles (books/accounting OK when PH-shaped) → broader category → generic Core heads later.

Source of truth: `ads-launch/PHASED-ACTIVATION.md`

## 2. Files touched

- `ads-launch/PHASED-ACTIVATION.md` — **new** source of truth + real ST examples
- `ads-launch/07-phased-activation-recommendation.md` — flipped; points to PHASED-ACTIVATION
- `ads-launch/DECISIONS.md` — activation priority row
- `ads-launch/CHATGPT-DEBRIEF.md` — brief activation flip
- `ads-launch/LAUNCH-SHEET.md` · `README.md` · `06-stage1-campaign-architecture.md`
- `ads-launch/build_stage1_editor_package.py` — comments only (PRIMARY/CONTROLLED ≠ enable order)
- `ads-launch/TONIGHT-HANDOFF.md` — this file
- `xray/launch-control.html` — step 13 + sequence enable copy
- `xray/docs/ads-launch/*` — mirrored docs

## 3. Safety

- **ADS REMAIN OFF** — CSV entities still Paused; no live enable
- **NOT SAFE FOR PAID TRAFFIC** until durable lead delivery
- No keyword CSV rebuild

## 4. Launch Control

https://vc-xray.vercel.app/launch-control

## 5. Tomorrow’s first three operator actions

1. Verify legacy live campaign status (`PM_*` Brand).
2. Configure durable US + AU lead delivery.
3. When enable is approved: follow `PHASED-ACTIVATION.md` — PH long-tail Exact first, not bare Core heads.

---

**Verdict for tonight:** `SAFE TO REVIEW` · `NOT SAFE FOR PAID TRAFFIC` · activation docs corrected
