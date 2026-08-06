/**
 * Data-driven category LP config for Stage 1 paid Search.
 * Nine employer service lines only — no medical/tech/job-seeker verticals.
 * Do not invent pricing, testimonials, or conversion values here.
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
      us: "US employers: tell us who you need for digital marketing — we recruit, vet, and support Philippines-based staff.",
      au: "Australian employers: tell us who you need for digital marketing — we recruit, vet, and support Philippines-based staff.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire Philippines digital marketing staff for your US business.",
          au: "Hire Philippines digital marketing staff for your Australian business.",
        },
        subhead: {
          us: "Tell us the marketing role you need filled. We shortlist vetted talent — you interview and decide who to hire.",
          au: "Tell us the marketing role you need filled. We shortlist vetted talent — you interview and decide who to hire.",
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
          us: "A staffing partner path for US employers — not a freelance marketplace or gig board.",
          au: "A staffing partner path for Australian employers — not a freelance marketplace or gig board.",
        },
        primaryCta: "Start your hiring request →",
        heroImage: { us: "/brand/talent-john.jpeg", au: "/brand/talent-john.jpeg" },
        heroAlt: "Dedicated Philippines hire — professional portrait",
      },
    },
    benefits: [
      "Role-specific shortlist for digital marketing support",
      "You interview before anyone joins your team",
      "Account management after placement — you stay the client",
    ],
    faq: [
      {
        q: "Is this for employers or job seekers?",
        a: "Employers only on this page. Job seekers use the careers destination — not this form.",
      },
      {
        q: "What happens after I submit?",
        a: "You submit an employer hiring inquiry. That is not a confirmed job order or placement. A teammate follows up using the details you provide.",
      },
      {
        q: "Do you invent pricing on this page?",
        a: "No. Pricing and placement terms are discussed after we understand the role — nothing here claims a $/hr rate or guaranteed savings.",
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
      us: "US employers hiring dedicated Philippines social media support through Virtual Coworker.",
      au: "Australian employers hiring dedicated Philippines social media support through Virtual Coworker.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire a Philippines social media teammate for your US brand.",
          au: "Hire a Philippines social media teammate for your Australian brand.",
        },
        subhead: {
          us: "Tell us the social role you need. We recruit and screen — you choose who to hire.",
          au: "Tell us the social role you need. We recruit and screen — you choose who to hire.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-ph.jpg", au: "/brand/va-ph.jpg" },
        heroAlt: "Philippines social media professional at work",
      },
      b: {
        h1: {
          us: "Dedicated social media capacity from the Philippines — employer path.",
          au: "Dedicated social media capacity from the Philippines — employer path.",
        },
        subhead: {
          us: "Built for US businesses that want a staffing partner, not a gig platform.",
          au: "Built for Australian businesses that want a staffing partner, not a gig platform.",
        },
        primaryCta: "Request a hiring shortlist →",
        heroImage: { us: "/brand/va-face-3.jpg", au: "/brand/va-face-3.jpg" },
        heroAlt: "Dedicated Philippines social media teammate",
      },
    },
    benefits: [
      "Social-media-focused hiring brief",
      "Screened shortlist before interviews",
      "Clear separation from job-seeker careers paths",
    ],
    faq: [
      {
        q: "Can I hire for content + community roles?",
        a: "Yes — describe the social media role you need in the form. We treat it as an employer staffing inquiry.",
      },
      {
        q: "Is a form submit a placement?",
        a: "No. A submit is a qualified inquiry attempt — not a job order and not a placement.",
      },
      {
        q: "Job seeker?",
        a: "Use the careers destination. This form does not accept applications.",
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
      us: "US employers: hire dedicated Philippines accounting support through Virtual Coworker.",
      au: "Australian employers: hire dedicated Philippines accounting support through Virtual Coworker.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire Philippines accounting staff for your US business.",
          au: "Hire Philippines accounting staff for your Australian business.",
        },
        subhead: {
          us: "Tell us the accounting seat you need filled. You interview the shortlist.",
          au: "Tell us the accounting seat you need filled. You interview the shortlist.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-face-2.jpg", au: "/brand/va-face-2.jpg" },
        heroAlt: "Philippines accounting professional",
      },
      b: {
        h1: {
          us: "Offshore accounting capacity with an employer staffing partner.",
          au: "Offshore accounting capacity with an employer staffing partner.",
        },
        subhead: {
          us: "For established US businesses — recruit, vet, interview, then hire with support.",
          au: "For established Australian businesses — recruit, vet, interview, then hire with support.",
        },
        primaryCta: "Start your hiring request →",
        heroImage: { us: "/brand/support.jpg", au: "/brand/support.jpg" },
        heroAlt: "Dedicated Philippines hire at a workstation",
      },
    },
    benefits: [
      "Accounting-role hiring path (not DIY coursework)",
      "You keep hiring authority",
      "Inquiry → discussion → possible job order — never assumed from a form click",
    ],
    faq: [
      {
        q: "Is this bookkeeping or accounting?",
        a: "This page is for accounting roles. Use the bookkeeping category if that is the seat you need.",
      },
      {
        q: "Do you guarantee credentials?",
        a: "We do not invent credentials or licenses on this page. Role fit is confirmed in the hiring conversation.",
      },
      {
        q: "Job seekers?",
        a: "Careers destination only — not this employer form.",
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
      us: "US employers hiring dedicated Philippines bookkeeping support.",
      au: "Australian employers hiring dedicated Philippines bookkeeping support.",
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
          us: "Dedicated bookkeeping capacity from the Philippines.",
          au: "Dedicated bookkeeping capacity from the Philippines.",
        },
        subhead: {
          us: "Employer staffing path for US teams that need reliable remote books support.",
          au: "Employer staffing path for Australian teams that need reliable remote books support.",
        },
        primaryCta: "Request a hiring shortlist →",
        heroImage: { us: "/brand/va-face-2.jpg", au: "/brand/va-face-2.jpg" },
        heroAlt: "Dedicated remote books support professional",
      },
    },
    benefits: [
      "Bookkeeping-focused employer brief",
      "Interview before hire",
      "No fake $/hr claims on this page",
    ],
    faq: [
      {
        q: "QuickBooks or Xero?",
        a: "Mention the tools you use in your inquiry. Tool fit is confirmed in follow-up — not invented here.",
      },
      {
        q: "Is submit a job order?",
        a: "No. Submit = employer inquiry. Job order and placement come later if you proceed.",
      },
      {
        q: "Looking for work?",
        a: "Use careers — this page is for employers only.",
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
      us: "US employers hiring dedicated Philippines administrative and VA support.",
      au: "Australian employers hiring dedicated Philippines administrative and VA support.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire Philippines administrative support for your US business.",
          au: "Hire Philippines administrative support for your Australian business.",
        },
        subhead: {
          us: "Virtual assistant and admin roles with a clear employer path — tell us who you need.",
          au: "Virtual assistant and admin roles with a clear employer path — tell us who you need.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-ph.jpg", au: "/brand/va-ph.jpg" },
        heroAlt: "Philippines administrative professional at desk",
      },
      b: {
        h1: {
          us: "Hire a dedicated Philippines virtual assistant — employer path.",
          au: "Hire a dedicated Philippines virtual assistant — employer path.",
        },
        subhead: {
          us: "Not a freelance marketplace. You interview. We recruit, vet, and support the hire.",
          au: "Not a freelance marketplace. You interview. We recruit, vet, and support the hire.",
        },
        primaryCta: "Start your hiring request →",
        heroImage: { us: "/brand/va-face-1.jpg", au: "/brand/va-face-1.jpg" },
        heroAlt: "Dedicated Philippines virtual assistant",
      },
    },
    benefits: [
      "Admin / VA hiring focused on employers",
      "You keep interview and hire decisions",
      "Separate from careers / job applications",
    ],
    faq: [
      {
        q: "VA vs executive assistant?",
        a: "Describe the seat in the form. Both sit under administrative support for Stage 1 routing.",
      },
      {
        q: "Phone click = qualified call?",
        a: "No. A phone click is a phone CTA click only — not a qualified call until CallRail + human qualification exist.",
      },
      {
        q: "Job seeker?",
        a: "Careers destination — not this form.",
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
      us: "US employers hiring dedicated Philippines customer service support.",
      au: "Australian employers hiring dedicated Philippines customer service support.",
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
          us: "Dedicated customer service capacity from the Philippines.",
          au: "Dedicated customer service capacity from the Philippines.",
        },
        subhead: {
          us: "Employer staffing for US teams that need reliable remote support seats.",
          au: "Employer staffing for Australian teams that need reliable remote support seats.",
        },
        primaryCta: "Request a hiring shortlist →",
        heroImage: { us: "/brand/va-face-2.jpg", au: "/brand/va-face-2.jpg" },
        heroAlt: "Dedicated Philippines support teammate",
      },
    },
    benefits: [
      "Customer-service role brief",
      "Screened candidates before interviews",
      "Honest funnel: inquiry ≠ placement",
    ],
    faq: [
      {
        q: "Chat, email, or phone support?",
        a: "Specify channels in your inquiry. We do not invent coverage promises on this page.",
      },
      {
        q: "Is this medical support?",
        a: "No. Medical roles are out of scope for this Stage 1 category set.",
      },
      {
        q: "Job seekers?",
        a: "Careers only — not employer conversion.",
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
      us: "US employers hiring dedicated Philippines HR support staff.",
      au: "Australian employers hiring dedicated Philippines HR support staff.",
    },
    variants: {
      a: {
        h1: {
          us: "Hire Philippines HR support for your US business.",
          au: "Hire Philippines HR support for your Australian business.",
        },
        subhead: {
          us: "Tell us the HR seat you need. Controlled lower-volume category — still employer-only.",
          au: "Tell us the HR seat you need. Controlled lower-volume category — still employer-only.",
        },
        primaryCta: "Tell us who you need →",
        heroImage: { us: "/brand/va-face-1.jpg", au: "/brand/va-face-1.jpg" },
        heroAlt: "Philippines HR support professional",
      },
      b: {
        h1: {
          us: "Offshore HR capacity with a clear employer staffing path.",
          au: "Offshore HR capacity with a clear employer staffing path.",
        },
        subhead: {
          us: "For US employers — inquire about the role; we recruit and you interview.",
          au: "For Australian employers — inquire about the role; we recruit and you interview.",
        },
        primaryCta: "Start your hiring request →",
        heroImage: { us: "/brand/va-face-3.jpg", au: "/brand/va-face-3.jpg" },
        heroAlt: "Dedicated Philippines HR teammate",
      },
    },
    benefits: [
      "HR support hiring inquiry path",
      "Lower historical search volume — still Exact/Phrase controlled in Ads",
      "No job-seeker conversion on this page",
    ],
    faq: [
      {
        q: "HR vs recruitment?",
        a: "Use recruitment if you need hiring/recruiting ops support. Use HR for broader people-ops support.",
      },
      {
        q: "Form submit meaning?",
        a: "Employer inquiry only — not a job order or placement.",
      },
      {
        q: "Looking for a job?",
        a: "Careers destination — blocked from employer conversion events.",
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
      us: "US employers hiring dedicated Philippines recruitment support.",
      au: "Australian employers hiring dedicated Philippines recruitment support.",
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
          us: "Dedicated recruitment capacity from the Philippines.",
          au: "Dedicated recruitment capacity from the Philippines.",
        },
        subhead: {
          us: "Controlled category for US employers — staffing partner, not a job board.",
          au: "Controlled category for Australian employers — staffing partner, not a job board.",
        },
        primaryCta: "Request a hiring shortlist →",
        heroImage: { us: "/brand/talent-john.jpeg", au: "/brand/talent-john.jpeg" },
        heroAlt: "Dedicated Philippines recruiting ops teammate",
      },
    },
    benefits: [
      "Recruitment-ops employer brief",
      "Thin historical ST volume acknowledged — curated keywords only",
      "Separate from applicants seeking jobs",
    ],
    faq: [
      {
        q: "Are you a job board?",
        a: "No. This page is for businesses hiring recruitment support staff.",
      },
      {
        q: "Submit = placement?",
        a: "No. Inquiry first; job order and placement only if you proceed.",
      },
      {
        q: "Job seeker?",
        a: "Careers destination only.",
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
      us: "US employers hiring dedicated Philippines sales support staff.",
      au: "Australian employers hiring dedicated Philippines sales support staff.",
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
          us: "Dedicated sales capacity from the Philippines — employer path.",
          au: "Dedicated sales capacity from the Philippines — employer path.",
        },
        subhead: {
          us: "For US businesses that want vetted remote sales support, not gig churn.",
          au: "For Australian businesses that want vetted remote sales support, not gig churn.",
        },
        primaryCta: "Start your hiring request →",
        heroImage: { us: "/brand/va-face-1.jpg", au: "/brand/va-face-1.jpg" },
        heroAlt: "Dedicated Philippines sales teammate",
      },
    },
    benefits: [
      "Sales-support hiring inquiry path",
      "You interview the shortlist",
      "No SaaS “book a demo” language — this is staffing",
    ],
    faq: [
      {
        q: "Is this a CRM product demo?",
        a: "No. Virtual Coworker is a staffing partner for offshore hires — not SaaS.",
      },
      {
        q: "What does submit mean?",
        a: "An employer hiring inquiry. Not a qualified opportunity until humans say so.",
      },
      {
        q: "Job seekers?",
        a: "Careers path — blocked from employer conversion.",
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
