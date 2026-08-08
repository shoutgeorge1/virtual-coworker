/* Launch-blocker status model for the paid-search pilot.
   Edit this file when access or approvals change.
   Do not invent account IDs, emails, phones, budgets, or conversion IDs.
   Distinguish confirmed facts vs recommendations vs unresolved.
   Status as of Aug 8, 2026. */
window.PILOT_STATUS = {
  pilotName: "Google Search proof of concept",
  fee: "$3,000",
  markets: ["US", "Australia"],
  channel: "Google Search",
  primaryContact: "Braden",
  previousContact: "Caitlin",
  handoffNote:
    "Caitlin is ops contact + lead-quality stakeholder and may start maternity leave anytime. Braden is expected to take over day-to-day while she is out. Cheyenne owns US sales; Holly owns APAC.",
  commercialStatus: "au_priority_us_live",
  commercialLabel: "AU PRIORITY · VC_AU_* LIVE (WAITING ON TRAFFIC) · SITE PHONE 1300 LIVE · US LIVE · BRAND PAUSED · AU TRACKING GAPS",
  objective:
    "Can Google Search → independent US/AU employer microsites generate qualified leads at an acceptable cost? Three identities (US · AU · PH); WordPress stays as-is with zero paid egress.",
  landingPages: {
    rootRedirectsTo: "https://www.virtualcoworker.app/us",
    us: "https://www.virtualcoworker.app/us",
    au: "https://www.virtualcoworker.app/au",
    ph: "https://www.virtualcoworker.app/ph",
    copyNote:
      "Caitlin LP copy already live (demo removed, Filipino terms, US hero, master 4-step, transparent rates, AU footer, thank-you aligned) — not pending rewrite."
  },
  /** Domains + measurement — separate per employer market; PH can hang for Stage 1. */
  micrositeInfra: {
    model: "one_host_path_markets",
    domains: {
      production: {
        status: "live",
        note: "www.virtualcoworker.app on Vercel vision (apex → www). Paths /us · /au · /ph — not two country domains."
      },
      preview: {
        status: "qa_only",
        note: "vision-three-alpha.vercel.app still exists — not for Ads Final URLs / Import"
      },
      ph: { status: "path_on_same_host", note: "Careers at /ph on www — no separate Stage 1 domain" }
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
  matchPolicy: "exact_only_live_phrase_paused",
  brandPolicy: "left_up_contained_~40_day_paused_weak_kws_secondary_to_vc_search",
  phases: {
    current: 1,
    labels: {
      1: "Paid Search Validation",
      2: "Conversion Improvement",
      3: "Expansion"
    }
  },

  adsLive: {
    us: {
      status: "live_spending",
      campaigns: [
        { id: "VC_US_S_CORE", dailyBudget: 75, maxCpc: 12 },
        { id: "VC_US_S_ROLES", dailyBudget: 50, maxCpc: null }
      ],
      combinedDaily: 125,
      bidding: "Maximize Clicks",
      match: "Exact-only (Phrase paused; junk Exact paused)",
      network: "Search-only",
      finalUrls: "www.virtualcoworker.app"
    },
    au: {
      status: "live_waiting_on_traffic",
      note: "AU campaigns live (George 2026-08-08) — not paused/broken; waiting on traffic/spend. Site phone 1300 live. Ops risk: Unkown AGs with Broad positives — cleanup landmine. Tracking (GTM/GA4/phone conversions) still thin vs US."
    },
    brand: "paused_deferred_2026_08_07"
  },

  /* Confirmed conversion strategy (Stage 1) — phone-first; not form Primary */
  conversionStrategy: {
    stage1Primary: [
      "Phone call conversions (website + ad call extensions) after US routing works — early steering signal"
    ],
    stage1Secondary: [
      "Employer form delivery (Resend and/or GitHub) — observe only; not bidding Primary",
      "Click-to-call observation",
      "Calendly booking (secondary/separate — not second Primary)"
    ],
    stage1DoNotOptimize: [
      "Thank-you page / raw form fills as Primary (spam risk)",
      "Job orders / placements — need clean lead data first before Ads learns from them",
      "Old Zoho/Zapier conversion actions — do not attach to VC_US_*",
      "Triple-count form + Calendly + Zoho for one enquiry"
    ],
    futureOfflineRanges: {
      jobOrder: "$200–$400 (estimate only — not approved for Ads import)",
      jobPlacement: "$500–$800 (estimate only — not approved for Ads import)"
    },
    laterPath:
      "After AU phone + website tags: human marks qualified in Zoho → light signal into Ads. Later (enough deals/money): value-based conversions when deals actually pay.",
    biddingUntilClean: "Maximize Clicks"
  },

  calendly: {
    us: "https://calendly.com/cheyenne-virtualcoworker/30min",
    apac: "https://calendly.com/apac-virtualcoworker/30min",
    role: "secondary_separate_not_second_primary"
  },

  /* Confirmed phone routing */
  phones: {
    naDestination: {
      number: "310-730-9126",
      status: "rings_to_google_voice_vm",
      note: "Rings ~5–6 → Google Voice VM. Ash (intern) got test VM — not durable. Cheyenne owns US sales. Raffie = phone systems/IT, not US salesperson. Route into Cheyenne/US sales workflow + missed-call owner + E2E."
    },
    auDestination: {
      number: "1300 886 740",
      status: "site_live_2026_08_08",
      note: "George-approved AU site phone — live on /au. Keep answering. Next: AU tracking parity (GTM/GA4/Ads conversions) + Unkown AG cleanup."
    },
    callRail: "Later — not Stage 1 operational. Tracking numbers forward to sales destinations; AU local tracking eventually."
  },

  leadDelivery: {
    resend: {
      status: "active",
      us: "us@virtualcoworker.com",
      au: "apac@virtualcoworker.com",
      cc: "George via LEAD_EMAIL_CC only"
    },
    githubIssues: {
      status: "internal_backup_only",
      repo: "shoutgeorge1/vc-employer-leads",
      verified: ["Caitlin test #5", "probe #6", "Resend to us@"],
      note: "Internal durability only — do not lead with this in UI. Leads go to email today (not CRM yet)."
    },
    wordpress: {
      status: "still_emails_group_inboxes",
      note: "WP + microsite + organic mix into us@/apac@. Monday must distinguish paid microsite/Ads from total inbound."
    },
    attributionFields: [
      "utm_*",
      "gclid",
      "gbraid",
      "wbraid",
      "landing URL",
      "referrer",
      "market",
      "category",
      "variant"
    ]
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

  /* People — confirmed names where known */
  people: [
    { name: "Caitlin", role: "Ops contact + lead-quality stakeholder; may start maternity leave anytime; LP copy already live" },
    { name: "Braden", role: "Expected takeover for day-to-day while Caitlin is out" },
    { name: "Raffie/Raffy", role: "PH — phone systems / IT / Zoho help; not US salesperson" },
    { name: "Cheyenne Gichana", role: "US sales owner" },
    { name: "Holly Wallace", role: "APAC sales owner" },
    { name: "Ash", role: "Intern — test VM only; not permanent call owner" },
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
      id: "us_search_live",
      label: "USA Search live: VC_US_S_CORE ($75/day) + VC_US_S_ROLES ($50/day) = $125/day · Max Clicks · Exact · Search-only",
      status: "complete"
    },
    {
      id: "lead_resend_github",
      label: "Microsite lead delivery ACTIVE — email first: Resend → us@/apac@ (+ George CC). Not CRM yet.",
      status: "complete"
    },
    {
      id: "calendly_confirmed",
      label: "Calendly confirmed (US Cheyenne + APAC) — secondary/separate, not second Primary",
      status: "complete"
    },
    {
      id: "lp_copy_live",
      label: "Caitlin LP copy live on www — not pending rewrite",
      status: "complete"
    },
    {
      id: "na_phone_dest",
      label: "US phone number confirmed: 310-730-9126 (routing to Cheyenne/sales workflow still open; Raffie ≠ salesperson)",
      status: "complete"
    },
    {
      id: "auto_apply_off",
      label: "Unsafe auto-apply disabled (done — keep off)",
      status: "complete"
    },
    {
      id: "apac_inbox_monitor",
      label: "APAC microsite monitoring confirmed — Holly Wallace (Zoho + Outlook; calendar for cold/follow-up; existing workflow enough for Monday; no new tracker/routing)",
      status: "complete"
    },
    {
      id: "au_phone_site",
      label: "AU site phone live — 1300 886 740 (deployed 2026-08-08)",
      status: "complete"
    },
    {
      id: "au_campaigns_enabled",
      label: "VC_AU_* live — waiting on traffic/spend (not paused). Tracking parity + Unkown AG cleanup still open",
      status: "complete"
    },
    {
      id: "ads_package_archived",
      label: "Editor Ads package DONE → archived from active checklist (nav Archive)",
      status: "complete"
    },
    {
      id: "cro_baseline",
      label: "CRO baseline shipped on employer microsite (pain→gain / conversion pass)",
      status: "complete"
    }
  ],
  verifyNow: [
    {
      id: "conversion_tracking",
      label: "After routing: VC_US_Phone_Call_From_Ads/_From_Website (60–90s) Primary; form Secondary; Zoho Qualified offline later — no legacy Zoho/Zapier",
      status: "verify"
    },
    {
      id: "search_terms_daily",
      label: "Daily: search terms · ad copy combos · budget spend · keywords + negatives",
      status: "verify"
    },
    {
      id: "monday_paid_scoreboard",
      label: "Verify Monday separates paid microsite/Ads from total inbound (attribution visible)",
      status: "verify"
    },
    {
      id: "exec_snapshot",
      label: "Keep Braden/CEO executive snapshot current (no fake Ads/Zoho widgets yet)",
      status: "verify"
    },
    {
      id: "gtm_publish_verify",
      label: "Verify GTM publish permission (still audit-only)",
      status: "verify"
    }
  ],
  waitingOnVc: [
    {
      id: "phone_routing_us",
      label: "Route 310-730-9126 into Cheyenne/US sales workflow + missed-call owner + E2E (not Google Voice dump)",
      status: "waiting"
    },
    {
      id: "sales_counting",
      label: "Cheyenne/US: confirm microsite monitoring in us@ + day-to-day counting source (APAC/Holly confirmed — Zoho+Outlook)",
      status: "waiting"
    },
    {
      id: "au_tracking_parity",
      label: "AU tracking parity (phone wins in Ads + GTM/GA4) — campaigns already live",
      status: "waiting"
    },
    {
      id: "au_unkown_ag_cleanup",
      label: "AU ops: delete blank/Unkown ad groups packed with Broad positives (Editor landmine)",
      status: "waiting"
    },
    { id: "qualified_def", label: "Exact definitions: qualified lead / job order / placement", status: "waiting" },
    { id: "lead_feedback", label: "How Caitlin / Cheyenne / Pauly return lead-quality feedback", status: "waiting" },
    { id: "day_contact", label: "Confirm Braden as day-to-day contact when Caitlin unavailable", status: "waiting" },
    { id: "chat_platform", label: "Official chat platform + invite George + notification settings", status: "waiting" },
    { id: "dev_contact", label: "Dev team email / phone / chat / hours", status: "waiting" }
  ],
  blocked: [
    {
      id: "callrail",
      label: "CallRail — approval/ownership unresolved; later, not Stage 1 operational",
      status: "blocked"
    },
    {
      id: "offline_values",
      label: "Final offline conversion values before Ads import (ranges only until approved)",
      status: "blocked"
    }
  ],
  optionalNotBlockers: [
    "Deep Zoho mapping / admin / direct write / offline / Job Order — shallow path first; not a traffic gate",
    "RSA image assets — useful polish; not required for RSAs to serve",
    "Ads Admin — nice-to-have later (Standard is enough for Stage 1)",
    "WordPress / hosting / Shopify — stays as-is; not paid destination",
    "WordPress rebuild / SEO / remarketing",
    "Gravity Forms — existing WP process only; paid LPs must not depend on WP/GF",
    "Brand campaigns — paused by George 2026-08-07; deferred; don’t re-enable",
    "Social media or SEO tool logins",
    "New lead tracker this week — Zoho + Monday email enough",
    "Unsafe Google auto-apply — already disabled"
  ],
  georgeHandles: [
    "AU top of queue: phone call conversions → GTM/GA4 → then Zoho qualified → Ads; Unkown AG cleanup",
    "Daily search terms / budget spend / keywords + negatives on live VC_US_* (and AU while Enabled)",
    "Phone-led conversions + shallow Zoho (Max Clicks until clean; form not preferred Primary)",
    "Wire site tests experiment events → dashboard (bottom of list until working)",
    "After AU tracking: Zoho qualified → Ads; value-based later",
    "Keep Braden/CEO executive snapshot calm (spend, clicks, themes — not raw typed queries)",
    "MCC + Google Ads Editor (Standard access on US + AU)",
    "Separate GTM_US + GTM_AU (+ GTM_PH if needed) / GA4 / GSC / Ads conversions"
  ],
  majorBlockers: [
    "AU top of queue: phone call conversions + GTM/GA4 (VC_AU_* already Enabled)",
    "AU ops risk: Unkown AGs with Broad positives — cleanup",
    "Site tests experiment / variant wiring (GTM or GA4 → dashboard) — bottom until working",
    "After AU tracking: Zoho qualified → Ads; later value when deals make money",
    "US inbox monitoring awaiting Cheyenne (APAC/Holly watches apac@)"
  ],
  nextThree: [
    "Australia — phone call conversions in Ads",
    "Australia — website tags (GTM + GA4)",
    "Then Zoho qualified mark → Ads; site tests stay at the bottom until working"
  ],
  openItemsUnresolved: [
    "AU phone call conversions in Ads (before Zoho → Ads)",
    "AU GTM/GA4 website tags (before Zoho → Ads)",
    "AU Unkown AG / Broad-positive cleanup",
    "Site tests GTM/GA4 experiment wiring (bottom until working)",
    "Zoho qualified → Ads path (after AU phone + website tags)",
    "Cheyenne/US microsite inbox monitoring + counting source (APAC/Holly watches)",
    "Monday paid microsite vs total inbound scoreboard verified",
    "Exact defs: qualified lead / job order / placement",
    "How Caitlin / Cheyenne / Pauly return lead-quality feedback",
    "CallRail approval / ownership",
    "Final offline conversion values before Ads import (later / money stage)",
    "Official chat platform + George invite"
  ],
  placeholders: {
    usLeadEmail: "us@virtualcoworker.com (Resend ACTIVE; WP also emails here)",
    auLeadEmail: "apac@virtualcoworker.com (Resend ACTIVE; WP also emails here)",
    usPhone: "888-954-8644",
    auPhone: "1300 886 740",
    usBudget: "$125/day combined (CORE $75 + ROLES $50)",
    auBudget: "Live · waiting on traffic — no invented AU spend figure",
    gtmUs: "GTM-M92DX9BJ (live on /us)",
    gtmAu: "[AU GTM — gap]",
    gtmPh: "[NEXT_PUBLIC_GTM_PH — optional later]",
    ga4Us: "G-2V3V0BS6JW (live on /us)",
    ga4Au: "[AU GA4 — gap]",
    adsConversionIdUs: "[existing US phone actions — do not invent new IDs here]",
    adsConversionIdAu: "[AU Ads conversion — do not invent; close gap carefully]",
    qualifiedLeadDefinition: "[open with VC — not blocking AU tracking work]"
  }
};
