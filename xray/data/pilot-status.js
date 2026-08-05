/* Launch-blocker status model for the paid-search pilot.
   Edit this file when access or approvals change.
   Do not invent account IDs, emails, phones, budgets, or conversion IDs. */
window.PILOT_STATUS = {
  pilotName: "Google Search proof of concept",
  fee: "$3,000",
  markets: ["US", "Australia"],
  channel: "Google Search",
  primaryContact: "Braden",
  previousContact: "Caitlin",
  handoffNote:
    "Caitlin is preparing for maternity leave. Braden is the primary contact for the pilot.",
  commercialStatus: "stage1_built_payment_in_transit",
  commercialLabel: "STAGE 1 BUILT — PAYMENT IN TRANSIT · APPROVALS STILL NEEDED",
  objective:
    "Can Google Search → independent microsite generate qualified USA and Australia employer leads at an acceptable cost? WordPress stays as-is.",
  landingPages: {
    us: "https://vision-three-alpha.vercel.app/us",
    au: "https://vision-three-alpha.vercel.app/au"
  },
  keywordClustersPhase1: ["philippines_va_hire", "general_employer_va_hire"],
  keywordClustersLater: ["philippines_bookkeeping", "general_bookkeeping"],
  matchPolicy: "exact_first_no_broad",
  phases: {
    current: 1,
    labels: {
      1: "Paid Search Validation",
      2: "Conversion Improvement",
      3: "Expansion"
    }
  },
  confirmedComplete: [
    { id: "mcc_link", label: "Google Ads MCC connections accepted (US + AU)", status: "complete" },
    { id: "gusto", label: "Gusto setup", status: "complete" },
    { id: "nda", label: "NDA", status: "complete" },
    {
      id: "gtm_access",
      label: "Existing GTM access approved (audit only — no tag changes/publish yet)",
      status: "complete"
    }
  ],
  verifyNow: [
    {
      id: "ads_admin_verify",
      label: "Verify Google Ads Admin inside each US + AU account",
      status: "verify"
    },
    {
      id: "gtm_publish_verify",
      label: "Verify GTM publish permission (still audit-only)",
      status: "verify"
    }
  ],
  /* Reduced onboarding — still waiting on VC */
  waitingOnVc: [
    {
      id: "payment",
      label: "$3,000 pilot payment (on its way to George’s bank — in transit)",
      status: "in_transit"
    },
    { id: "ad_spend_payer", label: "Who pays Google Ads spend", status: "waiting" },
    { id: "lead_emails", label: "Lead-routing emails (US + AU)", status: "waiting" },
    { id: "phone_routing", label: "Call-tracking phones, if calls included", status: "waiting" },
    { id: "qualified_def", label: "Definition of a qualified lead", status: "waiting" },
    { id: "day_contact", label: "Day-to-day contact while Caitlin unavailable", status: "waiting" },
    { id: "brand_ok", label: "Brand and messaging approval", status: "waiting" }
  ],
  blocked: [
    {
      id: "zoho_login",
      label:
        "Zoho login — Raffie reset webmaster@virtualcoworker.com but sent no password/reset link; George emailed, waiting",
      status: "blocked"
    },
    {
      id: "zoho_api",
      label: "Zoho API integration — blocked until login/access exists",
      status: "blocked"
    }
  ],
  optionalNotBlockers: [
    "WordPress / hosting / Shopify — stays as-is; not paid destination",
    "WordPress rebuild / SEO / remarketing",
    "Zoho / CallRail / offline conversions (do not block Stage 1)",
    "Social media or SEO tool logins"
  ],
  georgeHandles: [
    "MCC + Google Ads Editor (verify Admin per US + AU account)",
    "Independent microsite Stage 1 LPs (vision) — not WordPress",
    "Paused Clean Search import (Brand + CORE hire)",
    "Temporary GTM map later — no production GTM publish required for LP QA",
    "Lead form → email/webhook; Zoho optional later"
  ],
  /* Injected into Overview + Project Status blocker lists */
  majorBlockers: [
    "Budget / Max CPC approval placeholders",
    "Business phones + lead-routing emails (US + AU)",
    "Confirm paid host Final URL (microsite, not WordPress)",
    "Pilot payment clearing (on its way — not yet confirmed received)"
  ],
  nextThree: [
    "Verify Admin inside each US + AU account (MCC Accept already done)",
    "Approve budgets/CPC + phones + lead inbox",
    "Import paused Stage 1 CSV → enable US Brand + CORE after LP validation"
  ],
  placeholders: {
    usLeadEmail: "[US_LEAD_EMAIL]",
    auLeadEmail: "[AU_LEAD_EMAIL]",
    usPhone: "[US_PHONE]",
    auPhone: "[AU_PHONE]",
    usBudget: "[US_MONTHLY_BUDGET]",
    auBudget: "[AU_MONTHLY_BUDGET]",
    gtmId: "[TEMP_GTM_ID]",
    ga4Id: "[TEMP_GA4_ID]",
    adsConversionId: "[ADS_CONVERSION_ID]",
    qualifiedLeadDefinition: "[TO BE CONFIRMED WITH VIRTUAL COWORKER]"
  }
};
