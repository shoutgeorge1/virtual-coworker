/**
 * Trust-first US paid-search challenger.
 * Preview-only. Not a live Ads destination. Do not import from /us pages.
 *
 * Copy is original Virtual Coworker employer language.
 * Do not paste MyOutDesk sentences, stats, or claims.
 */

import {
  COMPANY_IDENTITY,
  PUBLIC_QUOTES,
  SITE,
  TRUST_PROOF,
  yearsTrading,
} from "./site";

export const TRUST_FIRST_NAMESPACE = "/preview/trust-first" as const;
export const TRUST_FIRST_LP_VERSION = "trust_first_preview_2026_08_18" as const;
export const TRUST_FIRST_EXPERIMENT_ID = "us_trust_first_lp" as const;
export const TRUST_FIRST_LANDING_PAGE_TYPE = "trust_first_preview" as const;

/** Preview toolbar + query override only. Production assignment stays off. */
export const TRUST_FIRST_SPLIT_LIVE = false;

export type TrustFirstVariant = "simple" | "proof_heavy";
export const TRUST_FIRST_VARIANTS = ["simple", "proof_heavy"] as const;
export const DEFAULT_TRUST_FIRST_VARIANT: TrustFirstVariant = "simple";

export type TrustFirstPageKey =
  | "us"
  | "philippines-virtual-assistants"
  | "virtual-assistant-agency"
  | "staffing"
  | "real-estate"
  | "bookkeeping"
  | "customer-service"
  | "sales"
  | "administrative-support"
  | "digital-marketing";

export type TrustFirstJobSeekerRisk = "low" | "medium" | "high";
export type TrustFirstPageKind = "new" | "replacement" | "existing-challenger";
export type TrustFirstConfidence = "high" | "medium" | "observed";

export type TrustFirstCard = { title: string; body: string };
export type TrustFirstFaq = { q: string; a: string };
export type TrustFirstStep = { k: string; t: string; d: string };
export type TrustFirstCompareRow = { label: string; vc: string; other: string };

export type TrustFirstPageConfig = {
  key: TrustFirstPageKey;
  name: string;
  previewPath: string;
  proposedProductionPath: string;
  currentProductionEquivalent: string;
  keywordCluster: string;
  intendedCampaign: string;
  intendedAdGroup: string;
  title: string;
  description: string;
  eyebrow: string;
  h1: string;
  supporting: string;
  heroBullets: readonly string[];
  cta: string;
  formHeading: string;
  trustStrip: readonly string[];
  roles: readonly TrustFirstCard[];
  process: readonly TrustFirstStep[];
  whyItems: readonly TrustFirstCard[];
  comparison: readonly TrustFirstCompareRow[];
  proofModules: readonly TrustFirstCard[];
  objections: readonly TrustFirstFaq[];
  faqs: readonly TrustFirstFaq[];
  formRoleDefault: string;
  jobSeekerRisk: TrustFirstJobSeekerRisk;
  pageKind: TrustFirstPageKind;
  recommendedStatus: string;
  notes: string;
  confidence: TrustFirstConfidence;
};

export const TRUST_FIRST_PAGE_KEYS: readonly TrustFirstPageKey[] = [
  "us",
  "philippines-virtual-assistants",
  "virtual-assistant-agency",
  "staffing",
  "real-estate",
  "bookkeeping",
  "customer-service",
  "sales",
  "administrative-support",
  "digital-marketing",
] as const;

export const COMPANY_SIZE_OPTIONS = [
  "Just me",
  "2-10 people",
  "11-50 people",
  "51-200 people",
  "200+ people",
] as const;

export const HIRING_TIMELINE_OPTIONS = [
  "As soon as we find the right person",
  "This month",
  "In the next 1-3 months",
  "Just researching",
] as const;

export const EMPLOYER_ROLE_OPTIONS = [
  "Virtual assistant / admin",
  "Bookkeeping support",
  "Customer service",
  "Sales support",
  "Digital marketing support",
  "Real estate support",
  "Several roles / a small team",
  "Something else",
] as const;

const YEARS = yearsTrading();

export const VERIFIED_PROOF = {
  foundedYear: TRUST_PROOF.sinceYear,
  yearsTrading: YEARS,
  usOffice: SITE.addressUs,
  auOffice: SITE.addressAu,
  phPresence: SITE.addressPhLabel,
  entityUs: COMPANY_IDENTITY.entityUs,
  entityAu: COMPANY_IDENTITY.entityAu,
  founder: `${COMPANY_IDENTITY.founderName}, ${COMPANY_IDENTITY.founderTitle}`,
  linkedinDisplay: TRUST_PROOF.socialReach.linkedinDisplay,
  facebookDisplay: TRUST_PROOF.socialReach.facebookDisplay,
  phoneDisplay: SITE.usPhoneDisplay,
  phoneHref: SITE.usPhoneHref,
  careersUrl: "https://virtualcoworker.com.ph",
} as const;

export const PROOF_NEEDING_CONFIRMATION = [
  {
    claim: "Exact current LinkedIn follower count above the 450K+ floor",
    why: "Last live check was 11 Aug 2026 (452,500). Floor is approved; do not print a fresher exact without a new look.",
  },
  {
    claim: "Exact current Facebook follower count above the 290K+ floor",
    why: "Live scrape was blocked. Floor came from the 11 Aug 2026 CEO meeting.",
  },
  {
    claim: "Published Philippines street address",
    why: "US and AU offices are published. PH is recruitment presence only on the contact page.",
  },
  {
    claim: "Client counts, savings percentages, or placement volume",
    why: "Not used. No verified public figure in this repo for those claims.",
  },
  {
    claim: "SOC 2, HIPAA, PCI, or similar certifications",
    why: "Not documented for Virtual Coworker. Do not display.",
  },
  {
    claim: "No recruitment fees as a headline promise",
    why: "Appears on some live pages. Confirm with George before leading with it here.",
  },
] as const;

const SHARED_PROCESS: TrustFirstStep[] = [
  {
    k: "1",
    t: "Tell us the seat",
    d: "A short call on your company, the role, and how many people you need. We write the job description with you. No fee to talk.",
  },
  {
    k: "2",
    t: "We recruit and vet",
    d: "Our Philippines team sources and screens. You review people who fit the seat, not a pile of random resumes.",
  },
  {
    k: "3",
    t: "You interview and decide",
    d: "You meet finalists on video. Nobody starts until you say yes. After you hire, we handle payroll and stay on support.",
  },
];

const SHARED_WHY: TrustFirstCard[] = [
  {
    title: `Staffing since ${TRUST_PROOF.sinceYear}`,
    body: "Virtual Coworker has recruited dedicated Filipino staff for businesses for more than a decade. This is a staffing company, not a freelance app.",
  },
  {
    title: "You keep the hire decision",
    body: "We shortlist. You interview. If it is not the right person, they do not join your team.",
  },
  {
    title: "Your hours, our employment admin",
    body: "Staff work your US business hours. Full-time or eligible part-time. After you hire, we employ them and handle payroll.",
  },
];

const SHARED_COMPARE: TrustFirstCompareRow[] = [
  {
    label: "Who you work with",
    vc: "A staffing company that recruits, vets, and stays after the hire",
    other: "A marketplace of freelancers, or a resume dump",
  },
  {
    label: "Who decides",
    vc: "You interview the shortlist and choose",
    other: "Someone assigns you a person you have not met",
  },
  {
    label: "After they start",
    vc: "Payroll, HR support, and a named team if you need help",
    other: "You are on your own once the contract is signed",
  },
];

const SHARED_PROOF: TrustFirstCard[] = [
  {
    title: `Founded ${TRUST_PROOF.sinceYear}`,
    body: `${YEARS}+ years recruiting dedicated Filipino staff for employers.`,
  },
  {
    title: "US and Australia employers",
    body: "West Hollywood and Sydney offices. Philippines recruitment and screening.",
  },
  {
    title: "Full-time or part-time seats",
    body: "Dedicated people on your hours. Eligible part-time starts at 20 hours a week.",
  },
  {
    title: "Role-specific recruiting",
    body: "We hire against the seat you described, not a generic talent pool.",
  },
];

const SHARED_OBJECTIONS: TrustFirstFaq[] = [
  {
    q: "Will they work my US hours?",
    a: "Yes. Dedicated staff are matched to your business hours, not the other way around.",
  },
  {
    q: "Do I have to hire the first person you send?",
    a: "No. You interview. If it is not a fit, we keep recruiting.",
  },
  {
    q: "Is this a freelance marketplace?",
    a: "No. Virtual Coworker is a staffing company. We recruit and vet. You choose. We employ the person after you hire.",
  },
  {
    q: "What does submitting this form do?",
    a: "It starts a hiring conversation. It is not a contract and not an instant hire.",
  },
];

const SHARED_FAQS: TrustFirstFaq[] = [
  {
    q: "Who is this page for?",
    a: "US businesses that want to hire dedicated Filipino staff. If you are looking for a job, use the careers link.",
  },
  {
    q: "How fast is a shortlist?",
    a: "It depends on the role. We talk through timing on the first call once we understand the seat.",
  },
  {
    q: "Do you publish rates here?",
    a: "No. Rates depend on the role. We talk through them after we understand what you need.",
  },
];

function page(
  partial: Omit<
    TrustFirstPageConfig,
    | "process"
    | "whyItems"
    | "comparison"
    | "proofModules"
    | "objections"
    | "cta"
    | "formHeading"
  > &
    Partial<
      Pick<
        TrustFirstPageConfig,
        | "process"
        | "whyItems"
        | "comparison"
        | "proofModules"
        | "objections"
        | "cta"
        | "formHeading"
      >
    >,
): TrustFirstPageConfig {
  return {
    process: SHARED_PROCESS,
    whyItems: SHARED_WHY,
    comparison: SHARED_COMPARE,
    proofModules: SHARED_PROOF,
    objections: SHARED_OBJECTIONS,
    cta: "Book a strategy call",
    formHeading: "Tell us about the role",
    ...partial,
  };
}

export const TRUST_FIRST_PAGES: Record<TrustFirstPageKey, TrustFirstPageConfig> = {
  us: page({
    key: "us",
    name: "US master challenger",
    previewPath: `${TRUST_FIRST_NAMESPACE}/us`,
    proposedProductionPath: "/us (challenger only; not a live swap)",
    currentProductionEquivalent: "/us",
    keywordCluster: "Employer PH staffing / dedicated Filipino staff (not generic virtual assistants)",
    intendedCampaign: "VC_US_S_CORE",
    intendedAdGroup: "Offshore_VA_PH / Hire_VA_PH employer phrases only",
    title: "Hire Dedicated Filipino Staff | Virtual Coworker",
    description:
      "Virtual Coworker recruits and vets dedicated Filipino staff for US businesses. You interview the shortlist. We handle payroll.",
    eyebrow: "Philippines staffing for US businesses",
    h1: "Hire dedicated Filipino staff who work your hours",
    supporting:
      "Virtual Coworker recruits and vets. You interview the shortlist and choose who joins. After you hire, we employ them and handle payroll. This is a staffing company, not a gig marketplace.",
    heroBullets: [
      "Dedicated people on your US hours",
      "You interview before anyone starts",
      "Full-time or eligible part-time seats",
    ],
    trustStrip: [
      `Staffing since ${TRUST_PROOF.sinceYear}`,
      "US hours",
      "You interview and decide",
    ],
    roles: [
      { title: "Admin and virtual assistant", body: "Inbox, calendar, follow-ups, and coordination." },
      { title: "Customer service", body: "Email, chat, and ticket work owned by one person." },
      { title: "Bookkeeping support", body: "Invoices, records, and routine reconciliations." },
      { title: "Sales support", body: "CRM hygiene, research, and follow-up. Not a cold-call farm." },
    ],
    faqs: SHARED_FAQS,
    formRoleDefault: "Virtual assistant / admin",
    jobSeekerRisk: "medium",
    pageKind: "replacement",
    recommendedStatus: "Preview only. Do not replace live /us.",
    notes:
      "Master format for US paid Search. Not a bid on the head term virtual assistants. Keep job-seeker diversion visible.",
    confidence: "high",
  }),

  "philippines-virtual-assistants": page({
    key: "philippines-virtual-assistants",
    name: "Philippines virtual assistants",
    previewPath: `${TRUST_FIRST_NAMESPACE}/philippines-virtual-assistants`,
    proposedProductionPath: "/us/philippines-virtual-assistants",
    currentProductionEquivalent: "/us",
    keywordCluster: "virtual assistant in the philippines / philippines virtual assistant / filipino VA hire",
    intendedCampaign: "VC_US_S_CORE",
    intendedAdGroup: "Offshore_VA_PH (keep; tighten). Hire_VA_PH only on 3+ word employer phrases.",
    title: "Hire a Virtual Assistant in the Philippines | Virtual Coworker",
    description:
      "Hire a dedicated virtual assistant in the Philippines for US hours. Virtual Coworker recruits and vets. You interview. We handle payroll.",
    eyebrow: "Philippines virtual assistants for US teams",
    h1: "Hire a virtual assistant in the Philippines",
    supporting:
      "A dedicated Filipino teammate for inbox, scheduling, and follow-ups on your US hours. We recruit and vet. You interview. Nobody starts until you say yes.",
    heroBullets: [
      "Dedicated seat, not a shared freelancer",
      "Matched to your US business hours",
      "You meet them before they join",
    ],
    trustStrip: [
      `Recruiting in the Philippines since ${TRUST_PROOF.sinceYear}`,
      "Your US hours",
      "You interview the shortlist",
    ],
    roles: [
      { title: "Inbox and calendar", body: "Triage, scheduling, and the follow-ups that slip." },
      { title: "Documents and research", body: "Files, trackers, and the prep work before a meeting." },
      { title: "Customer follow-up", body: "Replies and status updates in your voice." },
      { title: "Ops coordination", body: "A named person who owns the recurring work." },
    ],
    faqs: [
      {
        q: "Is this a person in the Philippines?",
        a: "Yes. We recruit dedicated Filipino staff. They work your US hours.",
      },
      ...SHARED_FAQS.slice(1),
    ],
    formRoleDefault: "Virtual assistant / admin",
    jobSeekerRisk: "medium",
    pageKind: "new",
    recommendedStatus: "Highest-leverage new page. Preview only.",
    notes:
      "Message match for the observed competitor keyword virtual assistant in the philippines (exact). Do not copy competitor claims.",
    confidence: "observed",
  }),

  "virtual-assistant-agency": page({
    key: "virtual-assistant-agency",
    name: "Virtual assistant agency",
    previewPath: `${TRUST_FIRST_NAMESPACE}/virtual-assistant-agency`,
    proposedProductionPath: "/us/virtual-assistant-agency",
    currentProductionEquivalent: "/us",
    keywordCluster: "virtual assistant agency / VA firm / VA company / Filipino VA agency",
    intendedCampaign: "VC_US_S_CORE",
    intendedAdGroup: "VA_Agency_Firm_PH",
    title: "Virtual Assistant Agency | Virtual Coworker",
    description:
      "A virtual assistant agency that recruits and vets dedicated Filipino staff. You interview. Virtual Coworker handles payroll.",
    eyebrow: "A staffing agency, not a gig listing",
    h1: "A virtual assistant agency that lets you interview first",
    supporting:
      "Virtual Coworker is the agency. We recruit and screen dedicated Filipino staff. You meet the shortlist. After you hire, we employ them. This is not a job board and not a freelance marketplace.",
    heroBullets: [
      "Agency recruiting against your brief",
      "You keep the hire decision",
      "Payroll and HR stay with us after you hire",
    ],
    trustStrip: [
      "Agency model since 2011",
      "You interview",
      "Not a job board",
    ],
    roles: [
      { title: "One dedicated assistant", body: "A named person for a defined seat." },
      { title: "A small pod", body: "Admin plus support or books, recruited as seats, not gigs." },
      { title: "Specialist seats", body: "Bookkeeping, customer service, or sales support when that is the brief." },
    ],
    faqs: [
      {
        q: "Are you hiring virtual assistants?",
        a: "This page is for businesses hiring staff. If you want a job with Virtual Coworker, use the careers link.",
      },
      ...SHARED_FAQS,
    ],
    formRoleDefault: "Virtual assistant / admin",
    jobSeekerRisk: "medium",
    pageKind: "new",
    recommendedStatus: "Preview. Strong match to existing agency search terms.",
    notes: "Competitor has no dedicated agency paid URL. Ours should read as a firm, not VA jobs.",
    confidence: "observed",
  }),

  staffing: page({
    key: "staffing",
    name: "Remote staffing",
    previewPath: `${TRUST_FIRST_NAMESPACE}/staffing`,
    proposedProductionPath: "/us/staffing",
    currentProductionEquivalent: "/us/staffing (candidate, noindex, not Ads)",
    keywordCluster: "remote staffing agency / philippines staffing / PH outsourcing agency",
    intendedCampaign: "VC_US_S_CORE",
    intendedAdGroup: "Staffing_Agency_PH",
    title: "Philippines Remote Staffing | Virtual Coworker",
    description:
      "A Philippines remote staffing partner for US businesses. We recruit and vet. You interview. We employ the person and handle payroll.",
    eyebrow: "Philippines remote staffing",
    h1: "A staffing partner for dedicated Filipino teammates",
    supporting:
      "Use Virtual Coworker when you want a staffing company, not a personal concierge and not a temp board. We recruit and vet. You interview. We employ them after you hire.",
    heroBullets: [
      "Staffing company for US employers",
      "Dedicated seats on your hours",
      "We stay on payroll after you hire",
    ],
    trustStrip: [
      `Since ${TRUST_PROOF.sinceYear}`,
      "US employers",
      "Philippines recruitment",
    ],
    roles: [
      { title: "Operations seats", body: "Admin, coordination, and the work that keeps a team moving." },
      { title: "Customer-facing seats", body: "Support and follow-up with a person you have met." },
      { title: "Finance support seats", body: "Books and records support, not licensed advice." },
      { title: "Growth support seats", body: "Marketing execution and sales admin, not a strategy retainers shop." },
    ],
    faqs: [
      {
        q: "Is this a staffing agency or a VA marketplace?",
        a: "A staffing agency. We recruit dedicated people. You interview. We employ them after you hire.",
      },
      {
        q: "Do you place US jobs?",
        a: "This page is for US businesses hiring Philippines staff. Job seekers use our Philippines careers site.",
      },
      ...SHARED_FAQS.slice(1),
    ],
    formRoleDefault: "Several roles / a small team",
    jobSeekerRisk: "medium",
    pageKind: "existing-challenger",
    recommendedStatus: "Challenger for the unused /us/staffing candidate. Still not an Ads URL.",
    notes: "Must read as a staffing company. Watch temp-job bleed on remote staffing agency.",
    confidence: "observed",
  }),

  "real-estate": page({
    key: "real-estate",
    name: "Real estate support",
    previewPath: `${TRUST_FIRST_NAMESPACE}/real-estate`,
    proposedProductionPath: "/us/real-estate",
    currentProductionEquivalent: "/us/real-estate",
    keywordCluster: "real estate virtual assistant / real estate admin / transaction coordinator support",
    intendedCampaign: "Not live. Do not create a Brand group. Test later under roles or a dedicated RE campaign.",
    intendedAdGroup: "None live. Do not add a duplicate if one is created later.",
    title: "Hire a Real Estate Virtual Assistant | Virtual Coworker",
    description:
      "Hire dedicated Philippines staff for US brokerages, teams, investors, and property managers. Admin, lead follow-up, transaction support, and database work.",
    eyebrow: "For brokerages, teams, and property managers",
    h1: "Hire a real estate virtual assistant for the work behind the deals",
    supporting:
      "Lead follow-up, listing admin, transaction files, and database hygiene. We recruit dedicated Philippines staff for US hours. You interview. This is not an ISA-only pitch and not a cold-call machine.",
    heroBullets: [
      "Admin, follow-up, and transaction support",
      "Database and CRM kept current",
      "You interview before anyone joins",
    ],
    trustStrip: [
      "US real-estate teams",
      "Your hours",
      "You choose the person",
    ],
    roles: [
      { title: "Lead follow-up", body: "Call and email follow-up so new inquiries do not sit." },
      { title: "Database and CRM", body: "Contacts, statuses, and next steps in the system you already use." },
      { title: "Listing and file admin", body: "Inbox, calendar, documents, and paperwork for one dedicated person." },
      { title: "Transaction coordination support", body: "Checklists and file prep. You keep the licensed work." },
      { title: "Property management admin", body: "Tenant messages, lease files, and day-to-day admin." },
    ],
    faqs: [
      {
        q: "Is this only for appointment setting?",
        a: "No. The common seats are admin, lead follow-up, files, and database work. Appointment support is available when that is the brief.",
      },
      {
        q: "Do they replace a licensed agent?",
        a: "No. They take the remote work so licensed people can stay on clients and closings.",
      },
      ...SHARED_FAQS.slice(1),
    ],
    formRoleDefault: "Real estate support",
    jobSeekerRisk: "low",
    pageKind: "existing-challenger",
    recommendedStatus: "Page exists live. This is a visual challenger only. Do not point ads yet.",
    notes: "Keep ISA and cold-call out of the H1. Competitor has a dedicated RE paid LP; we already have the URL.",
    confidence: "medium",
  }),

  bookkeeping: page({
    key: "bookkeeping",
    name: "Bookkeeping",
    previewPath: `${TRUST_FIRST_NAMESPACE}/bookkeeping`,
    proposedProductionPath: "/us/bookkeeping",
    currentProductionEquivalent: "/us/bookkeeping",
    keywordCluster: "bookkeeping VA / philippines bookkeeper / hire bookkeeper PH",
    intendedCampaign: "VC_US_S_ROLES",
    intendedAdGroup: "Bookkeeping_Hire_PH",
    title: "Hire a Philippines Bookkeeper | Virtual Coworker",
    description:
      "Hire dedicated Filipino bookkeeping support for US hours. Invoices, records, and reconciliations. You interview. We handle payroll.",
    eyebrow: "Books support for US businesses",
    h1: "Hire a dedicated Filipino bookkeeper",
    supporting:
      "Invoices, records, and routine reconciliations owned by one person on your hours. We recruit against your tools. You interview. Extra capacity for the work, not a claim of licensed advice.",
    heroBullets: [
      "Day-to-day books support, not a dump of contractors",
      "Tell us QuickBooks, Xero, or what you use",
      "You interview before anyone starts",
    ],
    trustStrip: [
      "Role-specific recruiting",
      "Your hours",
      "You interview",
    ],
    roles: [
      { title: "Invoices and bills", body: "Enter, track, and chase the routine paper." },
      { title: "Reconciliations", body: "Keep accounts current so month-end is not a scramble." },
      { title: "Records and reports", body: "The recurring reports your finance owner should not rebuild." },
    ],
    faqs: [
      {
        q: "QuickBooks or Xero?",
        a: "Tell us the tools when you send the role. We recruit against that.",
      },
      {
        q: "Is this a CPA service?",
        a: "No. This is bookkeeping support capacity. Licensed advice stays with your accountant.",
      },
      ...SHARED_FAQS.slice(1),
    ],
    formRoleDefault: "Bookkeeping support",
    jobSeekerRisk: "low",
    pageKind: "replacement",
    recommendedStatus: "Challenger for the strongest role URL (GA4 ~40 sessions / 47.5% engaged).",
    notes: "Keep this URL. Do not merge onto /us. Competitor has no dedicated paid bookkeeping LP.",
    confidence: "observed",
  }),

  "customer-service": page({
    key: "customer-service",
    name: "Customer service",
    previewPath: `${TRUST_FIRST_NAMESPACE}/customer-service`,
    proposedProductionPath: "/us/customer-service",
    currentProductionEquivalent: "/us/customer-service",
    keywordCluster: "customer service VA / philippines customer support / hire support PH",
    intendedCampaign: "VC_US_S_ROLES",
    intendedAdGroup: "Customer_Service_Hire_PH",
    title: "Hire Philippines Customer Service Staff | Virtual Coworker",
    description:
      "Hire dedicated Filipino customer service staff for US hours. We shortlist. You interview. We handle payroll.",
    eyebrow: "Dedicated support seats",
    h1: "Hire dedicated Filipino customer service staff",
    supporting:
      "A named person for the queue: email, chat, or tickets. We shortlist. You interview. More consistent replies without turning support into a freelance roster.",
    heroBullets: [
      "One dedicated support seat",
      "Channels you already use",
      "You meet them first",
    ],
    trustStrip: [
      "Your hours",
      "You interview",
      "Not a call-center dump",
    ],
    roles: [
      { title: "Email and tickets", body: "Inbox and help-desk work with a person who knows your product." },
      { title: "Chat support", body: "Live replies during the hours you cover." },
      { title: "Order and status updates", body: "The follow-ups customers wait on." },
    ],
    faqs: [
      {
        q: "Chat, email, or phone?",
        a: "Tell us the channels when you send the role. We recruit against that.",
      },
      {
        q: "Is this medical support?",
        a: "No. Medical roles are outside what we place on this page.",
      },
      ...SHARED_FAQS.slice(1),
    ],
    formRoleDefault: "Customer service",
    jobSeekerRisk: "medium",
    pageKind: "replacement",
    recommendedStatus: "Challenger for the best role engagement (GA4 ~22 / 68.2%).",
    notes: "CSR job titles bleed. Keep employer language. Do not merge onto /us.",
    confidence: "observed",
  }),

  sales: page({
    key: "sales",
    name: "Sales support",
    previewPath: `${TRUST_FIRST_NAMESPACE}/sales`,
    proposedProductionPath: "/us/sales",
    currentProductionEquivalent: "/us/sales",
    keywordCluster: "sales support VA / CRM follow-up / sales admin PH",
    intendedCampaign: "VC_US_S_ROLES",
    intendedAdGroup: "Sales_Hire_PH",
    title: "Hire Philippines Sales Support | Virtual Coworker",
    description:
      "Hire dedicated Filipino sales support for research, CRM, and follow-up. You interview. Not a cold-call machine.",
    eyebrow: "Sales support, not a dialer farm",
    h1: "Hire sales support for follow-up and CRM, not cold calling",
    supporting:
      "Research, CRM hygiene, and follow-ups so closers spend time with buyers. We shortlist dedicated Filipino staff. You interview. This is not a promise of a cold-call machine.",
    heroBullets: [
      "Pipeline admin and follow-up",
      "Research and list hygiene",
      "You interview before anyone joins",
    ],
    trustStrip: [
      "Support seat, not a closer",
      "Your CRM",
      "You decide",
    ],
    roles: [
      { title: "CRM hygiene", body: "Statuses, notes, and next steps stay current." },
      { title: "Follow-up", body: "The emails and reminders that drop when closers are busy." },
      { title: "Research", body: "Lists and prep so sellers walk into better conversations." },
    ],
    faqs: [
      {
        q: "Do you sell a CRM?",
        a: "No. We help you hire sales support staff. We do not sell software.",
      },
      {
        q: "Is this appointment setting only?",
        a: "Appointment support is available when that is the brief. The default seat is follow-up, research, and CRM.",
      },
      ...SHARED_FAQS.slice(1),
    ],
    formRoleDefault: "Sales support",
    jobSeekerRisk: "medium",
    pageKind: "replacement",
    recommendedStatus: "Challenger for /us/sales. Do not expand setter groups.",
    notes: "Account evidence already said pause setters. Keep this page on support language.",
    confidence: "observed",
  }),

  "administrative-support": page({
    key: "administrative-support",
    name: "Administrative support",
    previewPath: `${TRUST_FIRST_NAMESPACE}/administrative-support`,
    proposedProductionPath: "/us/administrative-support",
    currentProductionEquivalent: "/us/administrative-support",
    keywordCluster: "administrative support / executive assistant / virtual assistant admin",
    intendedCampaign: "VC_US_S_ROLES",
    intendedAdGroup: "Administration_EA_PH",
    title: "Hire Philippines Administrative Support | Virtual Coworker",
    description:
      "Hire a dedicated Filipino virtual assistant or admin for US hours. Inbox, calendar, and follow-ups. You interview.",
    eyebrow: "Admin and executive support",
    h1: "Hire a dedicated Filipino assistant for inbox and calendar",
    supporting:
      "Inbox, scheduling, and follow-ups owned by one person so leadership hours go back to customers and decisions. We recruit and vet. You interview. Clear admin work, not a vague VA promise.",
    heroBullets: [
      "Inbox, calendar, and documents",
      "A dedicated admin seat",
      "You interview before they start",
    ],
    trustStrip: [
      "Dedicated admin seat",
      "Your hours",
      "You interview",
    ],
    roles: [
      { title: "Inbox", body: "Triage and draft replies in your voice." },
      { title: "Calendar", body: "Scheduling that does not bounce back to you." },
      { title: "Follow-ups", body: "The reminders and check-ins that keep work moving." },
      { title: "Documents", body: "Files, trackers, and the prep before a meeting." },
    ],
    faqs: [
      {
        q: "Virtual assistant or executive assistant?",
        a: "Either. Tell us the day-to-day. We recruit for that seat.",
      },
      ...SHARED_FAQS,
    ],
    formRoleDefault: "Virtual assistant / admin",
    jobSeekerRisk: "medium",
    pageKind: "replacement",
    recommendedStatus: "Priority redesign. Live page engagement is weak (GA4 ~21.4%).",
    notes: "Fix the page before adding keywords. Keep employer language. Job-seeker risk on VA titles.",
    confidence: "observed",
  }),

  "digital-marketing": page({
    key: "digital-marketing",
    name: "Digital marketing",
    previewPath: `${TRUST_FIRST_NAMESPACE}/digital-marketing`,
    proposedProductionPath: "/us/digital-marketing",
    currentProductionEquivalent: "/us/digital-marketing",
    keywordCluster: "digital marketing VA / marketing support PH / campaign ops",
    intendedCampaign: "VC_US_S_ROLES",
    intendedAdGroup: "Digital_Marketing_Hire_PH",
    title: "Hire Philippines Digital Marketing Staff | Virtual Coworker",
    description:
      "Hire dedicated Filipino marketing support for campaigns, reporting, and content ops. You interview. Execution, not a strategy retainers shop.",
    eyebrow: "Marketing execution support",
    h1: "Hire marketing support for campaigns, reporting, and content ops",
    supporting:
      "Day-to-day marketing work needs an owner. We recruit dedicated Filipino staff for campaign coordination, reporting pulls, and content ops. You interview. Strategists stay on judgment work.",
    heroBullets: [
      "Execution tasks, not a strategy pitch",
      "Matched to the tools you already use",
      "You interview the shortlist",
    ],
    trustStrip: [
      "Execution seat",
      "Your tools",
      "You decide",
    ],
    roles: [
      { title: "Campaign coordination", body: "The checklists and handoffs that stall without an owner." },
      { title: "Reporting", body: "Pulls and recaps so someone is not rebuilding the same sheet." },
      { title: "Content ops", body: "Scheduling, asset coordination, and publishing support." },
    ],
    faqs: [
      {
        q: "Do you run ads for us?",
        a: "We help you hire the person who owns the day-to-day work. We are not selling a managed ads retainers package on this page.",
      },
      ...SHARED_FAQS.slice(1),
    ],
    formRoleDefault: "Digital marketing support",
    jobSeekerRisk: "low",
    pageKind: "replacement",
    recommendedStatus: "Challenger for a soft role URL (GA4 ~17 / 29.4% engaged).",
    notes: "Keep execution language. Do not promise agency-of-record outcomes.",
    confidence: "observed",
  }),
};

export function isTrustFirstPageKey(value: string): value is TrustFirstPageKey {
  return (TRUST_FIRST_PAGE_KEYS as readonly string[]).includes(value);
}

export function trustFirstPage(key: TrustFirstPageKey): TrustFirstPageConfig {
  return TRUST_FIRST_PAGES[key];
}

export function allTrustFirstPages(): TrustFirstPageConfig[] {
  return TRUST_FIRST_PAGE_KEYS.map((key) => TRUST_FIRST_PAGES[key]);
}

export const APPROVED_TESTIMONIALS = PUBLIC_QUOTES.map((q) => ({
  quote: q.quote,
  name: q.name,
  role: q.role,
  company: q.company || "",
}));

export const JOB_SEEKER_DIVERSION = {
  label: "Looking for a job with Virtual Coworker?",
  body: "This page is for businesses hiring staff. Applications go to our Philippines careers site.",
  cta: "View Philippines careers",
} as const;

export const DOCUMENTED_ADS_NEGATIVES = [
  "job",
  "jobs",
  "salary",
  "career",
  "careers",
  "apply",
  "application",
  "resume",
  "work from home",
] as const;

export const DOCUMENTED_DO_NOT_NEGATIVE = ["hire", "hiring"] as const;
