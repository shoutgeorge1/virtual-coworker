/* Launch-blocker status model for the paid-search pilot.
   Edit this file when access or approvals change.
   Do not invent account IDs, emails, phones, budgets, or conversion IDs.
   Distinguish confirmed facts vs recommendations vs unresolved. */
window.PILOT_STATUS = {
  pilotName: "Google Search proof of concept",
  fee: "$3,000",
  markets: ["US", "Australia"],
  channel: "Google Search",
  primaryContact: "Braden",
  previousContact: "Caitlin",
  handoffNote:
    "Caitlin is ops contact + lead-quality stakeholder and may start maternity leave anytime. Braden is expected to take over day-to-day while she is out.",
  commercialStatus: "stage1_built_payment_in_transit",
  commercialLabel: "STAGE 1 BUILT — PAYMENT IN TRANSIT · APPROVALS STILL NEEDED",
  objective:
    "Can Google Search → independent US/AU employer microsites generate qualified leads at an acceptable cost? Three identities (US · AU · PH); WordPress stays as-is with zero paid egress.",
  landingPages: {
    rootRedirectsTo: "https://www.virtualcoworker.app/us",
    us: "https://www.virtualcoworker.app/us",
    au: "https://www.virtualcoworker.app/au",
    ph: "https://www.virtualcoworker.app/ph"
  },
  /** Domains + measurement — separate per employer market; PH can hang for Stage 1. */
  micrositeInfra: {
    model: "three_separate_microsites",
    domains: {
      us: { status: "buy_on_vercel", note: "~$10 Vercel — attach to vision for US employer site" },
      au: { status: "buy_on_vercel", note: "~$10 Vercel — separate AU domain; do not share with US" },
      ph: { status: "deferred", note: "No Stage 1 domain required — careers path can hang on preview host" }
    },
    measurement: {
      rule: "Do not share one GTM/GA4 across US+AU",
      us: ["GTM container", "GA4 property", "Search Console on US domain", "Ads conversions → US microsite only"],
      au: ["GTM container", "GA4 property", "Search Console on AU domain", "Ads conversions → AU microsite only"],
      ph: "optional_later",
      envPlaceholders: [
        "NEXT_PUBLIC_GTM_US",
        "NEXT_PUBLIC_GTM_AU",
        "NEXT_PUBLIC_GTM_PH",
        "NEXT_PUBLIC_GA4_US",
        "NEXT_PUBLIC_GA4_AU",
        "NEXT_PUBLIC_GA4_PH"
      ]
    }
  },
  keywordClustersPhase1: [
    "digital_marketing",
    "social_media",
    "accounting",
    "bookkeeping",
    "administration_incl_va_hire",
    "customer_service",
    "hr",
    "recruitment",
    "sales"
  ],
  keywordClustersLater: ["brand_deferred", "competitors_deferred", "tech_medical_spanish_excluded"],
  matchPolicy: "exact_and_phrase_no_broad",
  brandPolicy: "deferred_not_in_stage1_import",
  phases: {
    current: 1,
    labels: {
      1: "Paid Search Validation",
      2: "Conversion Improvement",
      3: "Expansion"
    }
  },

  /* Confirmed conversion strategy (Stage 1) */
  conversionStrategy: {
    stage1Primary: [
      "Employer form submissions (server-accepted)",
      "Qualified phone calls"
    ],
    stage1DoNotOptimize: [
      "Job orders / placements — need clean lead data first before Ads learns from them"
    ],
    futureOfflineRanges: {
      jobOrder: "$200–$400 (estimate only — not approved for Ads import)",
      jobPlacement: "$500–$800 (estimate only — not approved for Ads import)"
    },
    laterPath: "Zoho → Google Ads offline conversions so campaigns learn which leads produce business"
  },

  /* Confirmed phone routing */
  phones: {
    naDestination: {
      number: "310-426-8776",
      status: "confirmed",
      note: "Raffie/Raffy (PH) manages/answers. Do not replace or port. CallRail tracking later — forward to this destination."
    },
    auDestination: {
      number: null,
      status: "unresolved",
      note: "No new paid-media AU number confirmed. Use only the official approved number already on the AU website. Final AU number = open launch item."
    },
    callRail: "Later — not Stage 1 operational. Tracking numbers forward to existing destinations; AU local tracking eventually."
  },

  /* Target services (PH remote staffing priority) */
  targetServices: {
    prioritize: [
      "Digital marketing",
      "Social media",
      "Accounting",
      "Bookkeeping",
      "Administration",
      "Customer service",
      "HR",
      "Recruitment",
      "Sales"
    ],
    exclude: [
      "Medical staffing",
      "Technology staffing",
      "Spanish-language campaigns / claims (hard to fill; no Spanish offering)"
    ]
  },

  /* People — first names only; no guessed surnames/emails/titles */
  people: [
    { name: "Caitlin", role: "Ops contact + lead-quality stakeholder; may start maternity leave anytime" },
    { name: "Braden", role: "Expected takeover for day-to-day while Caitlin is out" },
    { name: "Raffie/Raffy", role: "PH contact — Zoho + NA phone destination" },
    { name: "Cheyenne", role: "Lead-quality (Los Angeles)" },
    { name: "Pauly", role: "Lead-quality" },
    { name: "Essa", role: "AI and internship initiatives" },
    { name: "Dev team", role: "Separate team — contact + hours still needed" }
  ],

  confirmedComplete: [
    { id: "mcc_link", label: "Google Ads MCC connections accepted (US + AU)", status: "complete" },
    {
      id: "ads_access_standard",
      label:
        "Ads access confirmed — Standard via MCC on USA 496-715-1855 + AU 573-539-1940 (enough for Stage 1; Admin optional later)",
      status: "complete"
    },
    { id: "gusto", label: "Gusto setup", status: "complete" },
    { id: "nda", label: "NDA", status: "complete" },
    {
      id: "gtm_access",
      label: "Existing GTM access approved (audit only — no tag changes/publish yet)",
      status: "complete"
    },
    {
      id: "na_phone_dest",
      label: "NA phone destination confirmed: 310-426-8776 (Raffie/Raffy PH; do not port)",
      status: "complete"
    }
  ],
  verifyNow: [
    {
      id: "gtm_publish_verify",
      label: "Verify GTM publish permission (still audit-only)",
      status: "verify"
    }
  ],
  waitingOnVc: [
    {
      id: "payment",
      label: "$3,000 pilot payment (on its way to George’s bank — in transit)",
      status: "in_transit"
    },
    { id: "ad_spend_payer", label: "Who pays Google Ads spend", status: "waiting" },
    { id: "lead_emails", label: "Lead-routing emails / webhook (US + AU) for Stage 1 fallback", status: "waiting" },
    {
      id: "au_phone",
      label: "AU business phone — confirm official approved AU-site number for paid LPs",
      status: "waiting"
    },
    { id: "qualified_def", label: "Exact definitions: qualified lead / job order / placement", status: "waiting" },
    { id: "lead_owner", label: "Who owns/routes employer leads + response-time expectations", status: "waiting" },
    { id: "lead_feedback", label: "How Caitlin / Cheyenne / Pauly return lead-quality feedback", status: "waiting" },
    { id: "day_contact", label: "Confirm Braden as day-to-day contact when Caitlin unavailable", status: "waiting" },
    { id: "chat_platform", label: "Official chat platform + invite George + notification settings", status: "waiting" },
    { id: "dev_contact", label: "Dev team email / phone / chat / hours", status: "waiting" },
    { id: "brand_ok", label: "Brand and messaging approval", status: "waiting" },
    {
      id: "qual_fields",
      label: "Approve recommended business-qualification form fields (see Launch Checklist)",
      status: "waiting"
    }
  ],
  blocked: [
    {
      id: "zoho_access",
      label:
        "Zoho access — modules, field mappings, ownership, and API not confirmed; do not build final Zoho push yet",
      status: "blocked"
    },
    {
      id: "zoho_api",
      label: "Zoho API integration — blocked until access/modules/fields/ownership confirmed",
      status: "blocked"
    },
    {
      id: "callrail",
      label: "CallRail — approval/ownership unresolved; later, not fake-operational",
      status: "blocked"
    },
    {
      id: "offline_values",
      label: "Final offline conversion values before Ads import (ranges only until approved)",
      status: "blocked"
    }
  ],
  optionalNotBlockers: [
    "Ads Admin — nice-to-have later (ask Braden when convenient; Standard is enough for Stage 1)",
    "WordPress / hosting / Shopify — stays as-is; not paid destination",
    "WordPress rebuild / SEO / remarketing",
    "Gravity Forms — existing WP process only; paid LPs must not depend on WP/GF",
    "Zoho / CallRail / offline conversions (do not block Stage 1 — email/webhook OK to launch)",
    "Social media or SEO tool logins"
  ],
  georgeHandles: [
    "MCC + Google Ads Editor (Standard access confirmed on US + AU — Stage 1 OK)",
    "Three microsites on vision (US · AU · PH) — not WordPress; / → /us",
    "Production host www.virtualcoworker.app + /us /au /ph paths (preview still exists — not TRAFFIC READY)",
    "Separate GTM_US + GTM_AU (+ GTM_PH if needed) / GA4 / GSC / Ads conversions — same host OK",
    "Paused Clean Search import (Core + Roles US+AU; brand deferred)",
    "Lead form → secure server-side → email/webhook Stage 1; Zoho when access confirmed",
    "Capture GCLID / GBRAID / WBRAID / UTMs / LP / timestamp + market site_surface"
  ],
  majorBlockers: [
    "Budget / Max CPC approval placeholders",
    "AU phone + lead-routing email/webhook (NA dest phone confirmed)",
    "Durable lead delivery (real inbox / webhook / sheet) — domains are not the gate",
    "Separate GTM_US + GTM_AU measurement stacks (same host + path markets OK)",
    "Pilot payment clearing (on its way — not yet confirmed received)"
  ],
  nextThree: [
    "Account hygiene in Ads: Brand review · conversion events end-to-end · goal baskets · Zapier/lead map (Zapier ≠ fixed) · Assets · shared negatives · Auto-apply off",
    "Then Editor download + paused CSV import; keep path Final URLs; wire GTM_US + GTM_AU; lead inbox/webhook",
    "Enable PH long-tail first only after gates green (Launch Control step 20; brand deferred)"
  ],
  openItemsUnresolved: [
    "Conversion events end-to-end audit (USA + AU Primary/Secondary / source / fire path)",
    "Zapier / lead integration map (WP/GF? Ads conversions? Zoho?) — Zapier ≠ fixed",
    "Zoho access",
    "Zoho modules / field mappings",
    "Who owns / routes employer leads",
    "Lead response-time expectations",
    "AU phone (official AU-site number)",
    "Dev team email / phone / chat / hours",
    "Approved business-qualification form fields",
    "Exact defs: qualified lead / job order / placement",
    "How Caitlin / Cheyenne / Pauly return lead-quality feedback",
    "CallRail approval / ownership",
    "Final offline conversion values before Ads import",
    "Official chat platform + George invite"
  ],
  placeholders: {
    usLeadEmail: "[US_LEAD_EMAIL]",
    auLeadEmail: "[AU_LEAD_EMAIL]",
    usPhone: "310-426-8776",
    auPhone: "[AU_BUSINESS_PHONE]",
    usBudget: "[US_MONTHLY_BUDGET]",
    auBudget: "[AU_MONTHLY_BUDGET]",
    gtmUs: "[NEXT_PUBLIC_GTM_US]",
    gtmAu: "[NEXT_PUBLIC_GTM_AU]",
    gtmPh: "[NEXT_PUBLIC_GTM_PH — optional later]",
    ga4Us: "[NEXT_PUBLIC_GA4_US]",
    ga4Au: "[NEXT_PUBLIC_GA4_AU]",
    adsConversionIdUs: "[ADS_CONVERSION_ID_US]",
    adsConversionIdAu: "[ADS_CONVERSION_ID_AU]",
    qualifiedLeadDefinition: "[TO BE CONFIRMED WITH VIRTUAL COWORKER]"
  }
};
