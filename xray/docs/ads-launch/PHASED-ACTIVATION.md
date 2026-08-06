# Phased activation — Stage 1 (source of truth)

**Locked by George 2026-08-05.**  
**CSV stays Paused. This is enable order only — not Ads enable approval.**  
Companion checklist: `07-phased-activation-recommendation.md` · Launch Control step 20.

---

## Priority lock (read this first)

1. **Priority = long-tail high intent**, especially queries with **Philippine / Philippines / Filipino** + role or hire language  
   (example shape: *Filipino virtual assistant for bookkeeping*).
2. **Generic intent launches later** — bare “virtual assistant”, broad Core head terms — **not** first.
3. Early goal is **impressions / clicks / CTR learning**. Lead plumbing may lag; they need leads and can scale fast — don’t be overly shy on volume once enable is approved.
4. Want volume without thin-spread chaos → phase by **intent quality**, not “only three role names.”
5. **Accounting / bookkeeping / etc. are not automatically held back** when they carry strong PH long-tail — those can be **Phase 1**.

### Flip the wrong story

| Wrong (old) | Right (locked) |
|-------------|----------------|
| Enable Core first, then Digital / Social / Admin | Enable **PH / Filipino / offshore long-tail** first |
| Hold accounting · books · CS · HR · recruitment · sales | Include any Roles AG whose **query shape** is PH+role/hire long-tail |
| Phase by “proven volume role names” | Phase by **intent quality** (geo + hire + role) |

---

## Phase order (plain English)

### Phase 0 — TRAFFIC READY (before any Enable)

**TRAFFIC READY** hard gates: durable lead delivery (email/webhook/sheet — not log-only), live-format test arrives, named responder, LP/gate QA, phones locked, Final URLs = Core→market home · Roles→category, budgets/CPC confirmed, campaigns still Paused, **explicit George Enable approval**.  
**URL stability (strongly prefer before Enable):** one custom domain + Final URLs on that host (or rewrite off preview before Enable). Domain ≠ durable-leads substitute; one host + `/us` `/au` `/ph` paths — not two country domains. Regen: `ADS_FINAL_URL_HOST`.  

See `DECISIONS.md` (sequencing lock), `12-blocker-decision-list.md`, Launch Control.

**Not required for Enable:** Zoho CRM record, Zoho OAuth, native Zoho↔Ads connector, offline conversions, working Google Ads conversion action, Ads API. Those are **CRM READY** / **OPTIMIZATION READY** parallel tracks.

**Editor reminder:** Import = local draft only; Post = live upload (still Paused until Enable). CSV stamps **Account** Customer IDs (USA `496-715-1855` · AU `573-539-1940`). New `VC_*` add alongside `PM_*` — do not wipe account settings or delete old campaigns.

**Zoho / offline (parallel):** Audit modules/fields/ownership when ready. Access ≠ CRM READY. Plan offline job-order / job-placement later (values TBD).

### Phase 1 — PH / Filipino / offshore long-tail (Exact + tight Phrase)

**Turn on first** (US recommended before AU):

- Keywords / ad groups that match **Philippines · Philippine · Filipino · offshore** + hire/role language — across **both** `VC_*_S_CORE` **and** `VC_*_S_ROLES`.
- Category long-tails with **hire + PH + role** (Digital, Social, Admin, **Bookkeeping, Accounting**, CS, etc. when the keyword is PH-shaped).
- Prefer **Exact**, plus **tight Phrase** only — no Broad.

**Inside Roles:** do **not** hold Bookkeeping/Accounting just because historical volume looked lower if PH long-tail exists. Prioritize by query shape.

**Practical operator move:** In Editor, filter keywords containing `philippin` / `filipino` / `offshore` (and close variants), enable those Exact (+ tight Phrase) rows and their parent AGs as needed — leave bare head terms paused.

### Phase 2 — Broader category Exact / Phrase (no PH geo)

- Role/category Exact + Phrase **without** PH/Filipino/offshore geo modifiers.
- Still not bare Core head terms.
- Expand AGs already warmed by Phase 1 PH traffic.

### Phase 3 / later — Generic Core head terms

- Bare / short Core heads: *virtual assistant*, *hire a VA*, thin generics without PH geo.
- Tighter CPC / budget once CTR and inquiry quality from Phases 1–2 are known.
- AU same pattern after US diagnostics look sane (AU remains form-primary).

### Never in Stage 1

- Broad positives · PMax · DSA · competitor farms · WP Final URLs · Brand until scoped · Max Conversions on unverified conversion defs · treating log-only as TRAFFIC READY · treating Zoho/CRM as a traffic gate.

---

## Real PH long-tail examples (from USA search terms)

Mined from `audit-data/performance/search_terms_usa_4967151855_2026-08-05.csv` (historical ST — Ads “Conversions” ≠ placements). These illustrate **Phase 1 shape**, including books/accounting:

| Search term (example) | Why Phase 1 |
|-----------------------|-------------|
| filipino virtual assistant | PH + hire/VA |
| hire filipino virtual assistants | hire + Filipino + VA |
| how to hire a virtual assistant philippines | hire + PH + VA |
| hire va philippines | hire + PH + VA |
| social media manager philippines | role + PH |
| hire philippines social media manager | hire + role + PH |
| bookkeeper philippines | books + PH |
| philippines bookkeeper | books + PH |
| bookkeeping philippines | books + PH |
| philippines bookkeeping outsourcing | books + PH + outsource |
| philippines accounting outsourcing | accounting + PH |
| outsource bookkeeping philippines | books + PH + outsource |

**Phase 3 contrast (later):** bare `virtual assistant` / short hire-VA heads without geo — historically high volume, but **not** first under this lock.

---

## Operator checklist (when George says enable)

1. Confirm Phase 0 gates green + explicit approval.  
2. **US first.** Keep AU paused until US ST/CTR look sane.  
3. Enable **Phase 1** PH long-tail Exact (+ tight Phrase) in Core **and** Roles (include Bookkeeping/Accounting PH terms).  
4. Watch 7–14 days: search terms, CTR, inquiry quality (human) — not fake job-order ROI.  
5. Then Phase 2 category non-PH Exact/Phrase.  
6. Then Phase 3 generic Core heads with tighter CPC/budget.  
7. Brand deferred. Everything outside this order stays Paused.

**Ads remain Off until you click Enable in Ads/Editor.** Launch Control does not enable spend.

---

## Where this is wired

| Surface | Points here |
|---------|-------------|
| Launch Control step 20 | Enable copy → this file |
| `07-phased-activation-recommendation.md` | Short checklist mirror |
| `DECISIONS.md` | Activation priority row |
| `CHATGPT-DEBRIEF.md` | Brief activation flip |
| Builder | Comment only — CSV still all Paused; no v8 regen for vibes |
