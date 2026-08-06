/**
 * Data-driven category LP config for paid Search.
 * Nine employer service lines only — no medical/tech/job-seeker verticals.
 * Do not hard-code pricing, testimonials, or Ads goal values here.
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
      us: "Hire dedicated Philippines digital marketing staff for your US business.",
      au: "Hire dedicated Philippines digital marketing staff for your Australian business.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire Philippines digital marketing staff for your US business.",
          au: "Hire Philippines digital marketing staff for your Australian business.",
        },
        subhead: {
          us: "Need campaigns, content, or marketing ops covered? Tell us the seat — we shortlist vetted talent, you interview and decide.",
          au: "Need campaigns, content, or marketing ops covered? Tell us the seat — we shortlist vetted talent, you interview and decide.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-au.jpg", au: "/brand/va-au.jpg" },
        heroAlt: "Philippines digital marketing professional at a desk",
      },
      b: {
        h1: {
          us: "Staff your digital marketing seat with a dedicated Philippines hire.",
          au: "Staff your digital marketing seat with a dedicated Philippines hire.",
        },
        subhead: {
          us: "A staffing partner for US employers — not a freelance marketplace or gig board.",
          au: "A staffing partner for Australian businesses — not a freelance marketplace or gig board.",
        },
        primaryCta: "Start hiring →",
        heroImage: { us: "/brand/talent-john.jpeg", au: "/brand/talent-john.jpeg" },
        heroAlt: "Dedicated Philippines hire — professional portrait",
      },
    },
    benefits: [
      "Marketing-focused shortlist matched to your tools",
      "You interview before anyone joins your team",
      "Account support after you hire",
    ],
    faq: [
      {
        q: "Is this for businesses or job seekers?",
        a: "Businesses only. Looking for work? Use the careers link in the footer.",
      },
      {
        q: "What happens after I submit?",
        a: "Our team follows up for a short hiring conversation, then we take your brief and shortlist screened candidates for you to interview.",
      },
      {
        q: "Do you list pricing here?",
        a: "No. Rates depend on the role — we’ll talk through options once we understand what you need.",
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
      us: "Hire a dedicated Philippines social media teammate for your US brand.",
      au: "Hire a dedicated Philippines social media teammate for your Australian brand.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire a Philippines social media teammate for your US brand.",
          au: "Hire a Philippines social media teammate for your Australian brand.",
        },
        subhead: {
          us: "Content, scheduling, community — tell us the social role. We recruit and screen; you choose who to hire.",
          au: "Content, scheduling, community — tell us the social role. We recruit and screen; you choose who to hire.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-ph.jpg", au: "/brand/va-ph.jpg" },
        heroAlt: "Philippines social media professional at work",
      },
      b: {
        h1: {
          us: "Get dedicated social media capacity from the Philippines.",
          au: "Get dedicated social media capacity from the Philippines.",
        },
        subhead: {
          us: "For US businesses that want a staffing partner, not a gig platform.",
          au: "For Australian businesses that want a staffing partner, not a gig platform.",
        },
        primaryCta: "Get matched →",
        heroImage: { us: "/brand/va-face-3.jpg", au: "/brand/va-face-3.jpg" },
        heroAlt: "Dedicated Philippines social media teammate",
      },
    },
    benefits: [
      "Social media roles matched to your brand and channels",
      "Screened shortlist before you interview",
      "Clear path for businesses — not a job board",
    ],
    faq: [
      {
        q: "Can I hire for content and community roles?",
        a: "Yes — describe the social media seat you need. We’ll take it from there.",
      },
      {
        q: "Is submitting the form a hire?",
        a: "No. It starts a conversation with our team. You interview before anyone joins.",
      },
      {
        q: "Looking for a job?",
        a: "Use careers in the footer. This form is for businesses only.",
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
      us: "Hire dedicated Philippines accounting support for your US business.",
      au: "Hire dedicated Philippines accounting support for your Australian business.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire Philippines accounting staff for your US business.",
          au: "Hire Philippines accounting staff for your Australian business.",
        },
        subhead: {
          us: "Tell us the accounting seat you need filled. We shortlist — you interview.",
          au: "Tell us the accounting seat you need filled. We shortlist — you interview.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-face-2.jpg", au: "/brand/va-face-2.jpg" },
        heroAlt: "Philippines accounting professional",
      },
      b: {
        h1: {
          us: "Add offshore accounting capacity with a staffing partner.",
          au: "Add offshore accounting capacity with a staffing partner.",
        },
        subhead: {
          us: "For US businesses — we recruit and screen, you interview, then hire with support.",
          au: "For Australian businesses — we recruit and screen, you interview, then hire with support.",
        },
        primaryCta: "Start hiring →",
        heroImage: { us: "/brand/support.jpg", au: "/brand/support.jpg" },
        heroAlt: "Dedicated Philippines hire at a workstation",
      },
    },
    benefits: [
      "Accounting roles — not generic admin fill-ins",
      "You keep the final hire decision",
      "Conversation first, hire when you’re ready",
    ],
    faq: [
      {
        q: "Is this bookkeeping or accounting?",
        a: "This page is for accounting roles. Need books support instead? Use the bookkeeping page.",
      },
      {
        q: "How do you check skills?",
        a: "We screen candidates against your brief. Fit for tools and experience is confirmed when you interview.",
      },
      {
        q: "Looking for a job?",
        a: "Careers link in the footer — not this form.",
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
      us: "Hire dedicated Philippines bookkeeping support for your US business.",
      au: "Hire dedicated Philippines bookkeeping support for your Australian business.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire a Philippines bookkeeper for your US business.",
          au: "Hire a Philippines bookkeeper for your Australian business.",
        },
        subhead: {
          us: "Tell us the books role you need. We recruit and screen — you decide who to hire.",
          au: "Tell us the books role you need. We recruit and screen — you decide who to hire.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-face-1.jpg", au: "/brand/va-face-1.jpg" },
        heroAlt: "Philippines bookkeeping professional",
      },
      b: {
        h1: {
          us: "Get dedicated bookkeeping capacity from the Philippines.",
          au: "Get dedicated bookkeeping capacity from the Philippines.",
        },
        subhead: {
          us: "For US teams that need reliable remote books support — without marketplace churn.",
          au: "For Australian teams that need reliable remote books support — without marketplace churn.",
        },
        primaryCta: "Get matched →",
        heroImage: { us: "/brand/va-face-2.jpg", au: "/brand/va-face-2.jpg" },
        heroAlt: "Dedicated remote books support professional",
      },
    },
    benefits: [
      "Bookkeeping-focused hiring — not a general VA grab-bag",
      "Interview before anyone starts",
      "Rates discussed after we understand the role",
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
        a: "Use careers — this page is for businesses only.",
      },
    ],
  },
  "administrative-support": {
    slug: "administrative-support",
    label: "Administrative Support",
    formLabel: "Administrative / VA support",
    shortLabel: "Admin",
    title: {
      us: "Hire Philippines Administrative Support | Virtual Coworker US",
      au: "Hire Philippines Administrative Support | Virtual Coworker AU",
    },
    description: {
      us: "Hire a dedicated Philippines virtual assistant or admin teammate for your US business.",
      au: "Hire a dedicated Philippines virtual assistant or admin teammate for your Australian business.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire a Philippines virtual assistant for your US business.",
          au: "Hire a Philippines virtual assistant for your Australian business.",
        },
        subhead: {
          us: "Admin, EA, or day-to-day ops — tell us who you need. We recruit Filipino talent; you interview and choose.",
          au: "Admin, EA, or day-to-day ops — tell us who you need. We recruit Filipino talent for Australian business hours; you interview and choose.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-ph.jpg", au: "/brand/va-ph.jpg" },
        heroAlt: "Philippines administrative professional at desk",
      },
      b: {
        h1: {
          us: "Hire a dedicated Philippines virtual assistant.",
          au: "Hire a dedicated Philippines virtual assistant.",
        },
        subhead: {
          us: "Not a freelance marketplace. You interview. We recruit, screen, and support the hire.",
          au: "Not a freelance marketplace. You interview. We recruit, screen, and support the hire.",
        },
        primaryCta: "Start hiring →",
        heroImage: { us: "/brand/va-face-1.jpg", au: "/brand/va-face-1.jpg" },
        heroAlt: "Dedicated Philippines virtual assistant",
      },
    },
    benefits: [
      "Virtual assistant and admin roles for businesses",
      "You keep interview and hire decisions",
      "Separate from careers / job applications",
    ],
    faq: [
      {
        q: "Can I hire a VA or an executive assistant?",
        a: "Yes — tell us what the day-to-day looks like and we’ll recruit for that seat.",
      },
      {
        q: "What if I call instead?",
        a: "We’ll talk through the role the same way — fit and next steps get confirmed in conversation.",
      },
      {
        q: "Looking for a job?",
        a: "Careers in the footer — not this form.",
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
      us: "Hire dedicated Philippines customer service staff for your US business.",
      au: "Hire dedicated Philippines customer service staff for your Australian business.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire Philippines customer service staff for your US business.",
          au: "Hire Philippines customer service staff for your Australian business.",
        },
        subhead: {
          us: "Tell us the support role you need covered. We shortlist — you interview.",
          au: "Tell us the support role you need covered. We shortlist — you interview.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/support.jpg", au: "/brand/support.jpg" },
        heroAlt: "Philippines customer support professional",
      },
      b: {
        h1: {
          us: "Get dedicated customer service capacity from the Philippines.",
          au: "Get dedicated customer service capacity from the Philippines.",
        },
        subhead: {
          us: "For US teams that need reliable remote support seats.",
          au: "For Australian teams that need reliable remote support seats.",
        },
        primaryCta: "Get matched →",
        heroImage: { us: "/brand/va-face-2.jpg", au: "/brand/va-face-2.jpg" },
        heroAlt: "Dedicated Philippines support teammate",
      },
    },
    benefits: [
      "Customer service roles matched to your channels",
      "Screened candidates before interviews",
      "Conversation first — hire when you’re ready",
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
        a: "Careers in the footer — not this form.",
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
      us: "Hire dedicated Philippines HR support staff for your US business.",
      au: "Hire dedicated Philippines HR support staff for your Australian business.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire Philippines HR support for your US business.",
          au: "Hire Philippines HR support for your Australian business.",
        },
        subhead: {
          us: "Tell us the HR seat you need. Businesses only — not for job seekers.",
          au: "Tell us the HR seat you need. Businesses only — not for job seekers.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-face-1.jpg", au: "/brand/va-face-1.jpg" },
        heroAlt: "Philippines HR support professional",
      },
      b: {
        h1: {
          us: "Add offshore HR capacity with clear hiring support.",
          au: "Add offshore HR capacity with clear hiring support.",
        },
        subhead: {
          us: "For US employers — send the role, we recruit, you interview.",
          au: "For Australian businesses — send the role, we recruit, you interview.",
        },
        primaryCta: "Start hiring →",
        heroImage: { us: "/brand/va-face-3.jpg", au: "/brand/va-face-3.jpg" },
        heroAlt: "Dedicated Philippines HR teammate",
      },
    },
    benefits: [
      "HR support seats for growing teams",
      "Businesses only — not a job board",
      "You interview before anyone joins",
    ],
    faq: [
      {
        q: "HR or recruitment support?",
        a: "Need someone running hiring ops day to day? Try recruitment. Broader people-ops support sits here.",
      },
      {
        q: "What does submitting mean?",
        a: "You start a conversation with our team. Nothing is hired until you say yes.",
      },
      {
        q: "Looking for a job?",
        a: "Careers in the footer — not this form.",
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
      us: "Hire dedicated Philippines recruitment support for your US business.",
      au: "Hire dedicated Philippines recruitment support for your Australian business.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire Philippines recruitment support for your US business.",
          au: "Hire Philippines recruitment support for your Australian business.",
        },
        subhead: {
          us: "Tell us the recruiting ops role you need staffed. You keep final hire decisions.",
          au: "Tell us the recruiting ops role you need staffed. You keep final hire decisions.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-face-2.jpg", au: "/brand/va-face-2.jpg" },
        heroAlt: "Philippines recruitment support professional",
      },
      b: {
        h1: {
          us: "Get dedicated recruitment capacity from the Philippines.",
          au: "Get dedicated recruitment capacity from the Philippines.",
        },
        subhead: {
          us: "For US employers — a staffing partner, not a job board.",
          au: "For Australian businesses — a staffing partner, not a job board.",
        },
        primaryCta: "Get matched →",
        heroImage: { us: "/brand/talent-john.jpeg", au: "/brand/talent-john.jpeg" },
        heroAlt: "Dedicated Philippines recruiting ops teammate",
      },
    },
    benefits: [
      "Recruiting-ops support for your hiring pipeline",
      "Built for businesses staffing a seat — not applicants",
      "You interview the shortlist",
    ],
    faq: [
      {
        q: "Is this a job board?",
        a: "No. This page is for businesses hiring recruitment support staff.",
      },
      {
        q: "Is submitting a hire?",
        a: "No. Conversation first — you interview before anyone starts.",
      },
      {
        q: "Looking for a job?",
        a: "Careers in the footer only.",
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
      us: "Hire dedicated Philippines sales support for your US business.",
      au: "Hire dedicated Philippines sales support for your Australian business.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire Philippines sales support for your US business.",
          au: "Hire Philippines sales support for your Australian business.",
        },
        subhead: {
          us: "Appointment setting, CRM ops, or sales VA — tell us the seat you need.",
          au: "Appointment setting, CRM ops, or sales VA — tell us the seat you need.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-us.jpg", au: "/brand/va-us.jpg" },
        heroAlt: "Philippines sales support professional",
      },
      b: {
        h1: {
          us: "Get dedicated sales capacity from the Philippines.",
          au: "Get dedicated sales capacity from the Philippines.",
        },
        subhead: {
          us: "For US businesses that want vetted remote sales support — not gig churn.",
          au: "For Australian businesses that want vetted remote sales support — not gig churn.",
        },
        primaryCta: "Start hiring →",
        heroImage: { us: "/brand/va-face-1.jpg", au: "/brand/va-face-1.jpg" },
        heroAlt: "Dedicated Philippines sales teammate",
      },
    },
    benefits: [
      "Sales support seats — setters, CRM, pipeline help",
      "You interview the shortlist",
      "Staffing partner — not software or a marketplace",
    ],
    faq: [
      {
        q: "Is this a software product?",
        a: "No. Virtual Coworker helps you hire offshore staff — we don’t sell a CRM demo.",
      },
      {
        q: "What happens when I submit?",
        a: "Our team follows up to talk through the role and next steps.",
      },
      {
        q: "Looking for a job?",
        a: "Careers in the footer — not this form.",
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
