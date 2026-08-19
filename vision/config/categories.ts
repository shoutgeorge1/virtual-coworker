/**
 * Data-driven category LP config for paid Search.
 * Nine employer service lines only - no medical/tech/job-seeker verticals.
 * Do not hard-code pricing, testimonials, or Ads goal values here.
 *
 * Voice: US = punchy RSA. AU = same logic, understated B2B English -
 * not US copy with “Australian hours” swapped in. No USD ~$8 on AU.
 */

import type { MarketId } from "./markets";

export const CATEGORY_SLUGS = [
  "digital-marketing",
  "social-media",
  "accounting",
  "bookkeeping",
  "administrative-support",
  "customer-service",
  "hr",
  "recruitment",
  "sales",
] as const;

export type CategorySlug = (typeof CATEGORY_SLUGS)[number];

/** Legacy Ads / form role tokens → canonical category slug */
export const ROLE_TO_CATEGORY: Record<string, CategorySlug> = {
  digital_marketing: "digital-marketing",
  "digital-marketing": "digital-marketing",
  digitalmarketing: "digital-marketing",
  social_media: "social-media",
  "social-media": "social-media",
  socialmedia: "social-media",
  accounting: "accounting",
  bookkeeping: "bookkeeping",
  administration: "administrative-support",
  admin: "administrative-support",
  "administrative-support": "administrative-support",
  administrative_support: "administrative-support",
  customer_service: "customer-service",
  "customer-service": "customer-service",
  customerservice: "customer-service",
  hr: "hr",
  "human-resources": "hr",
  human_resources: "hr",
  recruitment: "recruitment",
  recruiting: "recruitment",
  sales: "sales",
};

/** Ads campaign role key → category slug */
export const ADS_ROLE_TO_CATEGORY: Record<string, CategorySlug> = {
  digital_marketing: "digital-marketing",
  social_media: "social-media",
  accounting: "accounting",
  bookkeeping: "bookkeeping",
  administration: "administrative-support",
  customer_service: "customer-service",
  hr: "hr",
  recruitment: "recruitment",
  sales: "sales",
};

export type AbVariant = "a" | "b";

export type CategoryCopy = {
  slug: CategorySlug;
  label: string;
  formLabel: string;
  /** Short noun for Path / UI */
  shortLabel: string;
  title: Record<MarketId, string>;
  description: Record<MarketId, string>;
  variants: Record<
    AbVariant,
    {
      h1: Record<MarketId, string>;
      subhead: Record<MarketId, string>;
      primaryCta: string;
      heroImage: Record<MarketId, string>;
      heroAlt: string;
    }
  >;
  benefits: string[];
  faq: { q: string; a: string }[];
};

export const CATEGORIES: Record<CategorySlug, CategoryCopy> = {
  "digital-marketing": {
    slug: "digital-marketing",
    label: "Digital Marketing",
    formLabel: "Digital marketing support",
    shortLabel: "Marketing",
    title: {
      us: "Hire Philippines Digital Marketing Staff | Virtual Coworker US",
      au: "Hire Philippines Digital Marketing Staff | Virtual Coworker AU",
    },
    description: {
      us: "Campaigns stalling? Hire a dedicated Filipino marketer for US hours - we shortlist, you interview, we handle payroll.",
      au: "Marketing still slipping? Hire a dedicated Filipino marketer for Australian hours - you interview, we handle employment admin.",
    },
    variants: {
      a: {
        h1: {
          us: "Your marketing is stalled. Hire a dedicated Filipino marketer.",
          au: "Marketing still slipping? Get dedicated Filipino marketing support.",
        },
        subhead: {
          us: "Campaigns, reporting, and content ops need an owner. We shortlist. You interview. We handle payroll.",
          au: "Campaigns, reporting and content ops need an owner. We shortlist. You interview. Australian hours - no lock-in from the first chat.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/marketing-v2.png", au: "/roles/marketing-v2.png" },
        heroAlt: "Filipino digital marketing professional at a desk",
      },
      b: {
        h1: {
          us: "Staff your marketing seat with a dedicated Filipino hire.",
          au: "A dedicated Filipino marketer - Australian hours, you choose who joins.",
        },
        subhead: {
          us: "Strategists stay on judgment work. We recruit the day-to-day owner - you interview before anyone joins.",
          au: "Your strategists stay on the work that needs judgment. We recruit the day-to-day owner. You interview before anyone starts.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/marketing-v2.png", au: "/roles/marketing-v2.png" },
        heroAlt: "Dedicated Philippines hire - professional portrait",
      },
    },
    benefits: [
      "Campaigns, reporting, and content ops stop stalling for lack of owners",
      "A dedicated marketing seat keeps day-to-day execution moving",
      "Strategists stay on judgment work - not checklist firefights",
      "Marketing-focused shortlist matched to your tools - you interview",
    ],
    faq: [
      {
        q: "What marketing work can they take on?",
        a: "Campaign coordination, reporting pulls, content ops, and research support matched to your tools - describe the seat and we’ll recruit against it.",
      },
      {
        q: "What happens after I submit?",
        a: "A member of our team will follow up for a short hiring consult - obligation free, at no cost. Then we take your brief and shortlist screened candidates for you to interview.",
      },
      {
        q: "Do you list pricing here?",
        a: "No. Rates depend on the role - we’ll talk through options once we understand what you need.",
      },
    ],
  },
  "social-media": {
    slug: "social-media",
    label: "Social Media",
    formLabel: "Social media support",
    shortLabel: "Social",
    title: {
      us: "Hire Philippines Social Media Staff | Virtual Coworker US",
      au: "Hire Philippines Social Media Staff | Virtual Coworker AU",
    },
    description: {
      us: "Channels going quiet? Hire a dedicated Filipino social teammate for US hours - you interview and choose.",
      au: "Social gone quiet? Hire a dedicated Filipino social teammate for Australian hours - you interview and choose.",
    },
    variants: {
      a: {
        h1: {
          us: "Brand going quiet? Hire a dedicated Filipino social teammate.",
          au: "Social gone quiet? A dedicated Filipino teammate can run the channels.",
        },
        subhead: {
          us: "Keep channels active without turning your week into a content firefight. You interview. We handle payroll.",
          au: "Keep channels active without the week becoming a content scramble. You interview. Australian hours. We handle employment admin.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/marketing-a.png", au: "/roles/marketing-a.png" },
        heroAlt: "Filipino social media professional at work",
      },
      b: {
        h1: {
          us: "Get dedicated social media capacity from a Filipino teammate.",
          au: "Dedicated social support from a Filipino teammate - Australian hours.",
        },
        subhead: {
          us: "Scheduling, community, and asset coordination - staffing for US brands, not a gig platform.",
          au: "Scheduling, community and asset coordination - staffing for Australian brands, not a gig platform.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/marketing-a.png", au: "/roles/marketing-a.png" },
        heroAlt: "Dedicated Philippines social media teammate",
      },
    },
    benefits: [
      "Posting and community replies stop falling behind when you’re busy",
      "A dedicated social seat owns scheduling, replies, and asset coordination",
      "Channels stay active without turning your week into a content firefight",
      "You interview before anyone joins - businesses only",
    ],
    faq: [
      {
        q: "Can I hire for content and community roles?",
        a: "Yes - scheduling, community replies, asset coordination, and basic reporting. Describe the channels and we’ll recruit for that seat.",
      },
      {
        q: "Is submitting the form a hire?",
        a: "No. It starts a conversation. You interview before anyone joins.",
      },
      {
        q: "Looking for a job?",
        a: "Choose the job-seeker option in the form - it opens our careers site.",
      },
    ],
  },
  accounting: {
    slug: "accounting",
    label: "Accounting",
    formLabel: "Accounting support",
    shortLabel: "Accounting",
    title: {
      us: "Hire Philippines Accounting Staff | Virtual Coworker US",
      au: "Hire Philippines Accounting Staff | Virtual Coworker AU",
    },
    description: {
      us: "Month-end piling up? Hire dedicated Filipino accounting support - we shortlist, you interview.",
      au: "Month-end still a scramble? Hire dedicated Filipino accounting support - you interview, we handle employment admin.",
    },
    variants: {
      a: {
        h1: {
          us: "Month-end piling up? Hire dedicated Filipino accounting support.",
          au: "Month-end still a scramble? Add dedicated Filipino accounting support.",
        },
        subhead: {
          us: "Recurring accounting work stacking up? We shortlist. You interview. Extra capacity - not licensed advice.",
          au: "Recurring accounting work stacking up? We shortlist. You interview. Extra capacity - not a substitute for your accountant.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/bookkeeper-a.png", au: "/roles/bookkeeper-a.png" },
        heroAlt: "Philippines accounting professional",
      },
      b: {
        h1: {
          us: "Add offshore accounting capacity with a staffing partner.",
          au: "Offshore accounting capacity - Australian hours, you choose who joins.",
        },
        subhead: {
          us: "For US businesses - we recruit and screen, you interview, then hire with payroll support.",
          au: "For Australian businesses - we recruit and screen, you interview, then hire with employment admin sorted.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/bookkeeper-a.png", au: "/roles/bookkeeper-a.png" },
        heroAlt: "Dedicated Philippines hire at a workstation",
      },
    },
    benefits: [
      "Recurring accounting support stops slowing month-end and handoffs",
      "A dedicated seat helps with transactions, schedules, and reporting prep",
      "Extra capacity for the work - not a claim of licensed advice",
      "You interview the shortlist before anyone starts",
    ],
    faq: [
      {
        q: "Is this bookkeeping or accounting?",
        a: "This page is for accounting support roles. Need day-to-day books instead? Use the bookkeeping page.",
      },
      {
        q: "How do you check skills?",
        a: "We screen candidates against your brief. Fit for tools and experience is confirmed when you interview.",
      },
      {
        q: "Looking for a job?",
        a: "Choose the job-seeker option in the form - it opens our careers site.",
      },
    ],
  },
  bookkeeping: {
    slug: "bookkeeping",
    label: "Bookkeeping",
    formLabel: "Bookkeeping support",
    shortLabel: "Books",
    title: {
      us: "Hire Philippines Bookkeeping Staff | Virtual Coworker US",
      au: "Hire Philippines Bookkeeping Staff | Virtual Coworker AU",
    },
    description: {
      us: "Invoices stacking up? Hire a dedicated Filipino bookkeeper - we recruit, you decide.",
      au: "Books falling behind? Hire a dedicated Filipino bookkeeper - you interview, we handle employment admin.",
    },
    variants: {
      a: {
        h1: {
          us: "Invoices stacking up? Hire a dedicated Filipino bookkeeper.",
          au: "Books falling behind? Hire a dedicated Filipino bookkeeper.",
        },
        subhead: {
          us: "Invoices, reconciliations, and routine reporting waiting on you? We recruit. You interview. We handle payroll.",
          au: "Invoices, reconciliations and routine reporting still on your desk? We recruit. You interview. Australian hours.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/bookkeeper-v2.png", au: "/roles/bookkeeper-v2.png" },
        heroAlt: "Filipino bookkeeping professional",
      },
      b: {
        h1: {
          us: "Get dedicated bookkeeping capacity from a Filipino teammate.",
          au: "Dedicated books support from a Filipino teammate - Australian hours.",
        },
        subhead: {
          us: "Reliable remote books support for US teams - without a freelance marketplace.",
          au: "Reliable remote books support for Australian teams - without a freelance marketplace.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/bookkeeper-v2.png", au: "/roles/bookkeeper-v2.png" },
        heroAlt: "Dedicated remote books support professional",
      },
    },
    benefits: [
      "Invoices, records, and reconciliations stop stacking on your desk",
      "A dedicated bookkeeper owns day-to-day books support",
      "Your finance owner spends less time catching up",
      "You interview before anyone joins - rates discussed for the role",
    ],
    faq: [
      {
        q: "QuickBooks or Xero?",
        a: "Mention the tools you use when you send your role. We’ll match against that in recruiting.",
      },
      {
        q: "Is submitting the form a hire?",
        a: "No. It starts a conversation. You interview before anyone joins.",
      },
      {
        q: "Looking for work?",
        a: "Use careers - this page is for businesses only.",
      },
    ],
  },
  "administrative-support": {
    slug: "administrative-support",
    label: "Administrative Support",
    formLabel: "Administrative / virtual assistant",
    shortLabel: "Admin",
    title: {
      us: "Hire Philippines Administrative Support | Virtual Coworker US",
      au: "Hire Philippines Administrative Support | Virtual Coworker AU",
    },
    description: {
      us: "Inbox eating your week? Hire a dedicated Filipino virtual assistant or EA for US hours - admin starting at $7/hour. You interview.",
      au: "Still doing the admin yourself? Hire a dedicated Filipino virtual assistant for Australian hours - you interview, we handle employment admin.",
    },
    variants: {
      a: {
        h1: {
          us: "Inbox eating your week? Hire a dedicated Filipino virtual assistant.",
          au: "Still doing the admin yourself? Hire a dedicated Filipino virtual assistant.",
        },
        subhead: {
          us: "Inbox, scheduling, and follow-ups eating leadership hours? We recruit and vet. You interview. Admin starting at $7/hour.",
          au: "Inbox, scheduling and follow-ups still landing back on you? We recruit. You interview. Australian hours - no lock-in from the first chat.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/admin-a.png", au: "/roles/admin-a.png" },
        heroAlt: "Filipino administrative professional at desk",
      },
      b: {
        h1: {
          us: "Hire a dedicated Filipino virtual assistant.",
          au: "A dedicated Filipino virtual assistant - Australian hours, you choose who joins.",
        },
        subhead: {
          us: "Dependable capacity for US businesses - not a freelance marketplace. We recruit and vet; you interview and decide.",
          au: "Dependable capacity for Australian businesses - not a freelance marketplace. You interview. We recruit, screen and support the hire.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/admin-a.png", au: "/roles/admin-a.png" },
        heroAlt: "Dedicated Philippines virtual assistant",
      },
    },
    benefits: [
      "Inbox, scheduling, and follow-ups stop eating leadership hours",
      "A dedicated admin seat owns triage, docs, and coordination",
      "Your managers get time back for customers and decisions",
      "You interview before anyone joins - we support after hire",
    ],
    faq: [
      {
        q: "Can I hire a virtual assistant or an executive assistant?",
        a: "Yes - inbox, calendar, documents, and follow-ups are common. Tell us the day-to-day and we’ll recruit for that seat.",
      },
      {
        q: "What if I call instead?",
        a: "We’ll talk through the role the same way - fit and next steps get confirmed in conversation.",
      },
      {
        q: "Looking for a job?",
        a: "Choose the job-seeker option in the form - it opens our careers site.",
      },
    ],
  },
  "customer-service": {
    slug: "customer-service",
    label: "Customer Service",
    formLabel: "Customer service support",
    shortLabel: "Support",
    title: {
      us: "Hire Philippines Customer Service Staff | Virtual Coworker US",
      au: "Hire Philippines Customer Service Staff | Virtual Coworker AU",
    },
    description: {
      us: "Customers waiting too long? Hire dedicated Filipino support for US hours - we shortlist, you interview.",
      au: "Customers waiting on replies? Hire dedicated Filipino support for Australian hours - you interview, we handle employment admin.",
    },
    variants: {
      a: {
        h1: {
          us: "Customers waiting too long? Hire dedicated Filipino support.",
          au: "Customers waiting on replies? Add dedicated Filipino support.",
        },
        subhead: {
          us: "Questions sitting in the queue? We shortlist. You interview. Dedicated support on your hours - we handle payroll.",
          au: "Questions sitting in the queue? We shortlist. You interview. Dedicated support on Australian hours - we handle employment admin.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/customer-service-v2.png", au: "/roles/customer-service-v2.png" },
        heroAlt: "Filipino customer support professional",
      },
      b: {
        h1: {
          us: "Get dedicated customer service capacity from a Filipino teammate.",
          au: "Dedicated customer support from a Filipino teammate - Australian hours.",
        },
        subhead: {
          us: "Reliable remote support seats for US businesses - not freelance gigs.",
          au: "Reliable remote support seats for Australian teams - not freelance gigs.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/customer-service-v2.png", au: "/roles/customer-service-v2.png" },
        heroAlt: "Dedicated Philippines support teammate",
      },
    },
    benefits: [
      "Customer questions stop sitting unanswered in the queue",
      "A dedicated support seat owns inquiries, tickets, and status updates",
      "More consistent customer communication for your brand",
      "You interview before anyone joins your team",
    ],
    faq: [
      {
        q: "Chat, email, or phone support?",
        a: "Tell us which channels matter when you send the role. We’ll recruit against that.",
      },
      {
        q: "Is this medical support?",
        a: "No. Medical roles are outside what we place on this page.",
      },
      {
        q: "Looking for a job?",
        a: "Choose the job-seeker option in the form - it opens our careers site.",
      },
    ],
  },
  hr: {
    slug: "hr",
    label: "Human Resources",
    formLabel: "HR support",
    shortLabel: "HR",
    title: {
      us: "Hire Philippines HR Support | Virtual Coworker US",
      au: "Hire Philippines HR Support | Virtual Coworker AU",
    },
    description: {
      us: "People admin stacking up? Hire dedicated Filipino HR support - businesses only, you interview first.",
      au: "People ops still on managers? Hire dedicated Filipino HR support - businesses only, you interview first.",
    },
    variants: {
      a: {
        h1: {
          us: "People admin stacking up? Hire dedicated Filipino HR support.",
          au: "People ops still on managers? Hire dedicated Filipino HR support.",
        },
        subhead: {
          us: "Records, onboarding, and scheduling defaulting to managers? We shortlist. You interview. Businesses only.",
          au: "Records, onboarding and scheduling still defaulting to managers? We shortlist. You interview. Businesses only.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/hr-v2.png", au: "/roles/hr-v2.png" },
        heroAlt: "Philippines HR support professional",
      },
      b: {
        h1: {
          us: "Add offshore HR capacity with clear hiring support.",
          au: "Offshore HR capacity - Australian hours, you choose who joins.",
        },
        subhead: {
          us: "For US employers - send the role, we recruit, you interview.",
          au: "For Australian businesses - tell us the role, we recruit, you interview.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/hr-v2.png", au: "/roles/hr-v2.png" },
        heroAlt: "Dedicated Philippines HR teammate",
      },
    },
    benefits: [
      "People admin and onboarding tasks stop defaulting to busy managers",
      "A dedicated HR support seat owns records, checklists, and scheduling",
      "People processes keep moving while leaders run the business",
      "You interview before anyone joins - businesses only",
    ],
    faq: [
      {
        q: "HR or recruitment support?",
        a: "Need someone running hiring day to day? Try recruitment. Broader people-ops admin sits here - records, onboarding checklists, and coordination.",
      },
      {
        q: "What does submitting mean?",
        a: "You start a conversation. Nothing is hired until you say yes.",
      },
      {
        q: "Looking for a job?",
        a: "Choose the job-seeker option in the form - it opens our careers site.",
      },
    ],
  },
  recruitment: {
    slug: "recruitment",
    label: "Recruitment",
    formLabel: "Recruitment support",
    shortLabel: "Recruiting",
    title: {
      us: "Hire Philippines Recruitment Support | Virtual Coworker US",
      au: "Hire Philippines Recruitment Support | Virtual Coworker AU",
    },
    description: {
      us: "Hiring pipeline slowing? Hire dedicated Filipino recruiting support - you keep final hire decisions.",
      au: "Hiring stuck in the admin? Hire dedicated Filipino recruiting support - you keep final hire decisions.",
    },
    variants: {
      a: {
        h1: {
          us: "Hiring pipeline slowing? Hire dedicated Filipino recruiting support.",
          au: "Hiring stalled in the admin? Add dedicated Filipino recruiting support.",
        },
        subhead: {
          us: "Sourcing and interview scheduling eating the week? We shortlist TA support. You interview. You keep final hire decisions.",
          au: "Sourcing and interview scheduling slowing things down? We shortlist TA support. You interview. You keep final hire decisions.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/sales-a.png", au: "/roles/sales-a.png" },
        heroAlt: "Filipino recruitment support professional",
      },
      b: {
        h1: {
          us: "Get dedicated recruitment capacity from a Filipino teammate.",
          au: "Dedicated recruiting support from a Filipino teammate - Australian hours.",
        },
        subhead: {
          us: "Hiring capacity for US employers - a staffing partner, not a job board. We shortlist; you decide.",
          au: "Hiring capacity for Australian businesses - a staffing partner, not a job board. We shortlist; you decide.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/sales-a.png", au: "/roles/sales-a.png" },
        heroAlt: "Dedicated Philippines recruiting support teammate",
      },
    },
    benefits: [
      "Sourcing, screens, and interview scheduling stop slowing your pipeline",
      "A dedicated recruiting seat owns coordination and pipeline hygiene",
      "Hiring managers spend time deciding - not chasing calendars",
      "You interview the shortlist - businesses only",
    ],
    faq: [
      {
        q: "Is this a job board?",
        a: "No. This page is for businesses hiring recruitment support staff - sourcing, screens, and interview coordination.",
      },
      {
        q: "Is submitting a hire?",
        a: "No. Conversation first - you interview before anyone starts.",
      },
      {
        q: "Looking for a job?",
        a: "Choose the job-seeker option in the form - it opens our careers site.",
      },
    ],
  },
  sales: {
    slug: "sales",
    label: "Sales",
    formLabel: "Sales support",
    shortLabel: "Sales",
    title: {
      us: "Hire Philippines Sales Support | Virtual Coworker US",
      au: "Hire Philippines Sales Support | Virtual Coworker AU",
    },
    description: {
      us: "Need a setter or sales support? Hire dedicated Filipino talent - you interview before anyone joins.",
      au: "Follow-ups falling through? Hire dedicated Filipino sales support - you interview, we handle employment admin.",
    },
    variants: {
      a: {
        h1: {
          us: "Need a setter? Hire dedicated Filipino sales support.",
          au: "Follow-ups falling through? Hire dedicated Filipino sales support.",
        },
        subhead: {
          us: "Appointment setting or sales support without another US full-time hire. We shortlist. You interview. We handle payroll.",
          au: "Research, CRM hygiene and follow-ups still sitting with closers? We shortlist. You interview. Australian hours.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/sales-v2.png", au: "/roles/sales-v2.png" },
        heroAlt: "Filipino sales support professional",
      },
      b: {
        h1: {
          us: "Fill your setter or sales-support seat with dedicated Filipino talent.",
          au: "Dedicated sales support from a Filipino teammate - Australian hours.",
        },
        subhead: {
          us: "Vetted remote appointment setting and sales support for US businesses - staffing partner, not a gig platform.",
          au: "Vetted remote sales support for Australian businesses - staffing partner, not a gig platform.",
        },
        primaryCta: "Book Your Free Consultation",
        heroImage: { us: "/roles/sales-v2.png", au: "/roles/sales-v2.png" },
        heroAlt: "Dedicated Philippines sales teammate",
      },
    },
    benefits: [
      "Appointment setting, research, CRM hygiene, and follow-ups stop slipping",
      "A dedicated sales support seat protects pipeline basics",
      "Sellers spend more time talking to buyers",
      "You interview before anyone joins - staffing, not a job board",
    ],
    faq: [
      {
        q: "Is this a software product?",
        a: "No. Virtual Coworker helps you hire offshore sales support staff - research, CRM hygiene, and follow-ups - we don’t sell a CRM demo.",
      },
      {
        q: "What happens when I submit?",
        a: "A member of our team will follow up to talk through the role and next steps - obligation free, at no cost.",
      },
      {
        q: "Looking for a job?",
        a: "Choose the job-seeker option in the form - it opens our careers site.",
      },
    ],
  },
};

export function isCategorySlug(value: string): value is CategorySlug {
  return (CATEGORY_SLUGS as readonly string[]).includes(value);
}

export function resolveCategoryParam(raw: string | null | undefined): CategorySlug | null {
  if (!raw) return null;
  const key = raw.trim().toLowerCase();
  return ROLE_TO_CATEGORY[key] || (isCategorySlug(key) ? key : null);
}

export function allFormRoleLabels(): string[] {
  return CATEGORY_SLUGS.map((s) => CATEGORIES[s].formLabel);
}

export function formLabelForSlug(slug: CategorySlug): string {
  return CATEGORIES[slug].formLabel;
}

export function slugForFormLabel(label: string): CategorySlug | null {
  const hit = CATEGORY_SLUGS.find((s) => CATEGORIES[s].formLabel === label);
  return hit || null;
}
