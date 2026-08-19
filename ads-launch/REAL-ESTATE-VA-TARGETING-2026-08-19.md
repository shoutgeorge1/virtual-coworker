# Real Estate VA targeting — proposed-change report

**Status:** Proposal only. No Ads API. No live enable. Editor CSVs are paused.

**Date:** 19 Aug 2026  
**Accounts reviewed:** USA `496-715-1855` (AU not in scope for this vertical)  
**Intel:** George 19 Aug (generic Real Estate VA often = outbound cold caller; VC stopped that work) + discovery notes (poor fit = cold calling, pay-per-lead / CPA, commission-only, lead-buying confusion; good fit = dedicated headcount, free up time for sales/strategy, operational ownership).

Successful US placements to keep access to: **Assistant Property Manager, Guest Relations Specialist, Lead Generation, Bookkeeper, Executive Assistant.**

---

## What the account actually has

There is **no live Real Estate ad group** in the Stage 1 package. Prior rec (`ads-launch/research/trust-first-us-2026-08-18/ad-group-recommendation.md`) said do not invent one yet.

Real-estate traffic can still arrive from:

- CORE `Hire_VA_PH` / `Offshore_VA_PH` if generic VA keywords are enabled (many heads are already paused)
- Sales groups (`Sales_Hire_PH`, `Sales_Outsource_PH`) whose RSAs still say appointment setter / outbound / prospecting
- Live LP `https://www.virtualcoworker.app/us/real-estate` (URL exists in production; this branch did not have the route)

Search-term evidence in-repo (`ads-launch/_evidence_search_terms.json`) has **no Real Estate term in keepers**. Closest paid waste: `virtual assistant appointment setter` ($301, 30 clicks, 0 conv) and `appointment setter philippines` ($61, 2 clicks, 0 conv). Historical Editor dumps list many “real estate virtual assistant …” strings as **entity/negative occurrences, not proof of converting employer volume**.

Zoho week snapshot (`xray/data/sales-ops-week-zoho.json`, 10–16 Aug) has **no industry or role field**. Gmail was not readable in this environment. No extra good-fit / bad-fit lead rows beyond the two emails.

---

## What should stay

| Keep | Why |
|------|-----|
| Real-estate / property-management as a vertical | Intel says do not kill the market |
| Existing Bookkeeping and EA ad groups | Successful placement types; no evidence they are misaligned |
| `lead generation virtual assistant` and other **hire / dedicated / VA** lead-gen terms in Sales | Lead Generation is a successful seat. Do not treat “lead gen” as lead-buying |
| CORE employer VA keywords that already convert | No ST proof they are mostly RE cold callers. Do not pause CORE to “fix RE” |
| Brand | Still deferred |
| Sales support for **non-RE** follow-up / CRM | Separate from RE cold calling. Do not account-negative `appointment setter` |

---

## What should change

| Change | Action now | Risk if skipped |
|--------|------------|-----------------|
| Live `/us/real-estate` H1 and role cards | In this PR: stop “Hire a Real Estate Virtual Assistant” and remove **Appointment setting** | Page still sells the role VC does not want |
| Trust-first `/preview/trust-first/real-estate` | Same supported seats; FAQ says no ISA / no lead-buying | Preview still reads as generic RE VA |
| CORE + ROLES campaign negatives for **RE cold-call / PPL / dialer** patterns | Editor CSV, Phrase, **not imported until you say so** | Generic VA queries can still pull ISA intent |
| Sales RSAs that lead with setters / outbound | Leave live package as-is; rewrite only if you want Sales to stop selling setters entirely | RE agents clicking Sales ads still hear “appointment setter” |
| Generic “real estate VA” as a positive | Do not add it. Optional Phrase negative is in the **review** file | Treating generic RE VA as automatically good |

**Not done automatically:** pausing converting CORE keywords, account-wide `isa` / `appointment setter` / `lead generation` negatives, enabling new ad groups.

---

## New keyword / ad-group opportunities

Volume does **not** support five live role groups. Propose one paused hub plus three paused satellites. Bookkeeper and EA stay in existing groups; hub RSA mentions them.

| Ad group | Status | Exact candidates (not a bid list) | Final URL |
|----------|--------|-----------------------------------|-----------|
| `RE_Ops_Hire_PH` | Proposed, **Paused** | hire assistant property manager; assistant property manager philippines; hire guest relations specialist; hire real estate bookkeeper; hire real estate executive assistant; property management bookkeeper; dedicated lead generation virtual assistant | `/us/real-estate` |
| `RE_Property_Manager_PH` | Satellite, **Paused** | assistant property manager; hire an assistant property manager; remote assistant property manager | `/us/real-estate` |
| `RE_Guest_Relations_PH` | Satellite, **Paused** | guest relations specialist; hire guest relations specialist; guest relations virtual assistant | `/us/real-estate` |
| `RE_Lead_Gen_PH` | Satellite, **Paused** | hire dedicated lead generation specialist; dedicated lead generation hire | `/us/real-estate` |

Do **not** add: `real estate virtual assistant`, `real estate va`, `real estate appointment setter`, `real estate cold calling`, `real estate isa`.

Enable later only if search terms show employer volume on the hub. No Broad. No Brand.

---

## Proposed negatives

### Safe to import after you review (`google-ads-editor-re-negatives-us.csv`)

Campaign-level on `VC_US_S_CORE` and `VC_US_S_ROLES`. Phrase unless noted.

**Cold call / ISA / setter (RE-qualified or unambiguous):**  
cold calling · cold caller · cold callers · cold call · real estate isa · realtor isa · real estate cold calling · real estate cold caller · real estate appointment setter · realtor appointment setter · appointment setting for real estate · real estate setter · realtor setter · inside sales agent real estate · expired listing caller · expired listings caller · fsbo caller · fsbo cold · telemarketing · telemarketer · dialer · power dialer · auto dialer

**Lead-buying / outcome pay (not bare “lead generation”):**  
pay per lead · pay per lead real estate · cost per lead · cost per acquisition · commission based · commission only · buy real estate leads · purchase real estate leads · real estate leads for sale · real estate lead company · real estate lead service · realtor lead service

### Human review (`google-ads-editor-re-negatives-review-us.csv`)

Do not import with the safe file.

| Term | Why it is ambiguous |
|------|---------------------|
| `real estate virtual assistant` (Phrase) | Can be EA / admin / property ops, or a cold caller. Intel says do not treat as automatically good — not the same as “block it” |
| `real estate va` / `realtor va` | Same mix |
| `outbound calling` / `outbound prospecting` | Can be research/follow-up language |
| `appointment setter` (bare, all campaigns) | Still used in paused Sales keywords for non-RE |
| `lead generation services philippines` (already a Sales_Outsource keyword) | Sounds like a lead-buying agency. Pause/negative that **keyword** later if Sales still wants dedicated-hire lead gen |
| Transaction coordinator | On the old LP; **not** in the successful-placement list. Do not bid or negative yet |

---

## Landing-page changes (this PR)

| URL | Change |
|-----|--------|
| `/us/real-estate` | Add the missing production route. H1: dedicated **property staff**, not generic Real Estate VA. Role cards = the five supported seats. CTA stays “Tell Us Who You Need” / staffing request. No appointment setting. No prices. |
| `/preview/trust-first/real-estate` | Same seat list. FAQ: not cold callers / ISAs; not a lead-buying service. |
| `/us/sales` | **Unchanged.** H1 still “Need a setter?” — flag for you. Changing it would hit non-RE sales. |

AU: no `/au/real-estate`. Not added to the nine paid categories.

---

## RSA language (proposed, paused)

Hub RSA points at `/us/real-estate`. Headlines name property staff, guest relations, bookkeeper, EA, dedicated lead-gen seat. No setter, ISA, cold call, pay-per-lead, or “buy leads”.

Sales RSAs in the existing package still say “Hire Appointment Setter” / “Interview-Ready Setters”. Leave them until you decide whether Sales should keep setters for non-RE.

---

## Ambiguous areas needing your call

1. **Phrase-negative generic “real estate VA” on CORE?** Filters the cold-caller meaning; can also drop a good property EA. Default here: leave in the review file.
2. **Keep Sales setter keywords paused, or negative them?** Evidence is waste + RE intel. Non-RE setter demand may still be real.
3. **Lead Generation ads:** keep on `/us/sales` (current) or split RE lead-gen to `/us/real-estate`? Recommend keep generic lead-gen on Sales; only RE-ops hub uses the industry URL.
4. **Transaction coordinator / listing admin / CRM follow-up** were on the old LP. Not in the placement list. Do not bid.
5. Need a current Ads search-term export + Zoho industry/role on RE leads before enabling the new groups.

---

## Files

- `ads-launch/google-ads-editor-re-negatives-us.csv` — safe negatives, not imported
- `ads-launch/google-ads-editor-re-negatives-review-us.csv` — review only
- `ads-launch/google-ads-editor-re-ops-keywords-us.csv` — paused ad groups, Exact keywords, RSA
- `vision/app/us/real-estate/page.tsx` + `vision/config/real-estate.ts`
- `vision/config/trust-first.ts` (preview copy)

**Editor:** import only after you approve. Everything in the keyword file is **Paused**.
