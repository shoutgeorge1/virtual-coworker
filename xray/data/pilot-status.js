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
  commercialStatus: "ready_upon_payment_and_access",
  commercialLabel: "READY TO BEGIN UPON PAYMENT AND ACCESS",
  objective:
    "Can Google Search generate qualified US and Australian employer leads at an acceptable cost?",
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
  /* Reduced onboarding — launch blockers only */
  waitingOnVc: [
    { id: "payment", label: "Pay $3,000 pilot invoice", status: "waiting" },
    { id: "ads_admin", label: "Google Ads Admin access (George MCC)", status: "waiting" },
    { id: "ad_spend_payer", label: "Who pays ad spend", status: "waiting" },
    { id: "lead_emails", label: "Lead recipient emails (US + AU)", status: "waiting" },
    { id: "phone_routing", label: "Phones if calls tracked", status: "waiting" },
    { id: "qualified_def", label: "What counts as a good lead", status: "waiting" },
    { id: "day_contact", label: "Day-to-day contact during Caitlin leave", status: "waiting" },
    { id: "zoho_api", label: "Zoho API / write access for lead push", status: "waiting" },
    { id: "brand_ok", label: "OK to use brand on pilot pages", status: "waiting" }
  ],
  optionalNotBlockers: [
    "WordPress / hosting / Shopify",
    "Their existing GTM, GA4, or Search Console",
    "Social media or SEO tool logins",
    "Permission to rebuild the corporate website"
  ],
  georgeHandles: [
    "MCC + Google Ads Editor",
    "Independent microsite + domain purchase",
    "Temporary GTM, GA4, Search Console",
    "Exact-match employer Search US + AU",
    "Lead form → email + Zoho",
    "Weekly cleanup and follow-up emails"
  ],
  majorBlockers: [
    "Pilot invoice payment",
    "Google Ads Admin access",
    "Lead emails",
    "Zoho API write path"
  ],
  nextThree: [
    "Pay the $3,000 pilot invoice",
    "Grant Google Ads Admin so George can link his MCC",
    "Send lead emails + Zoho API write access"
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
