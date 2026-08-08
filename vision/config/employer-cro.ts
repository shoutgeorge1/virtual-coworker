/**
 * Shared employer CRO copy — pain → relief → gain.
 * Used by market landings, category pages, services, and how-it-works.
 * Claims stay within verified site facts (see config/site.ts, hiring-process.ts).
 */

import type { MarketId } from "./markets";
import type { CategorySlug } from "./categories";

/** Primary employer CTA — keep consistent across employer surfaces. */
export const PRIMARY_HIRE_CTA = "Start Hiring";

export type PainGainCopy = {
  eyebrow: string;
  title: string;
  lead: string;
  beforeLabel: string;
  afterLabel: string;
  before: string[];
  after: string[];
};

export function painGainCopy(market: MarketId): PainGainCopy {
  const hours =
    market === "au" ? "Australian business hours" : "US business hours";
  return {
    eyebrow: "Before you dig into the process",
    title: "What’s consuming your time — and what changes with the right coworker.",
    lead:
      market === "au"
        ? "Australian businesses usually don’t need another tool. They need dependable capacity for work that keeps pulling leadership and specialists off higher-value work."
        : "US businesses usually don’t need another tool. They need dependable capacity for work that keeps pulling leadership and specialists off higher-value work.",
    beforeLabel: "What’s consuming your time",
    afterLabel: "What changes with the right coworker",
    before: [
      "Admin, follow-ups, and coordination eat leadership hours",
      "Important tasks slip while your team firefights the day-to-day",
      "Internal specialists get pulled into work below their pay grade",
      "Growth work waits because routine execution never clears",
    ],
    after: [
      "A dedicated Filipino teammate owns a clear seat on your hours",
      "Follow-through becomes consistent — not something you chase",
      "Your local team gets time back for customers and growth",
      `Reliable support during ${hours}, with payroll and employment support handled`,
    ],
  };
}

export type RoleOutcome = {
  /** Short business problem for this role page. */
  problem: string;
  /** Concrete tasks a dedicated coworker can take over. */
  tasks: string[];
  /** Operational gain — no invented metrics. */
  gain: string;
};

/** Role-specific outcomes — not identical generic copy across pages. */
export const ROLE_OUTCOMES: Record<CategorySlug, RoleOutcome> = {
  "administrative-support": {
    problem:
      "Inbox, scheduling, documents, and follow-ups keep pulling you or your managers away from real work.",
    tasks: [
      "Inbox triage and routine replies",
      "Calendar and meeting coordination",
      "Document prep and file organization",
      "Follow-ups that otherwise slip",
    ],
    gain:
      "A dedicated admin seat that learns your rhythms — so leadership time goes back to customers and decisions.",
  },
  bookkeeping: {
    problem:
      "Invoices, records, and reconciliations stack up while the rest of the business waits on clean numbers.",
    tasks: [
      "Invoice and bill support",
      "Day-to-day record keeping",
      "Bank and account reconciliations",
      "Routine reporting assistance",
    ],
    gain:
      "Steadier books support so your finance owner spends less time catching up and more time guiding the business.",
  },
  accounting: {
    problem:
      "Accounting support work piles up and slows month-end, reporting, and handoffs to your advisor or controller.",
    tasks: [
      "Transaction support and coding assistance",
      "Schedule and document preparation",
      "Routine reporting support",
      "Coordination with your accountant or finance lead",
    ],
    gain:
      "Extra accounting capacity for the recurring work — without implying licensed advice or guaranteed outcomes.",
  },
  "customer-service": {
    problem:
      "Customer questions sit too long, queues build, and your team loses time answering the same requests.",
    tasks: [
      "Customer inquiries across email or chat",
      "Queue and ticket follow-through",
      "Order or account status updates",
      "Clear handoffs when something needs a manager",
    ],
    gain:
      "Faster, more consistent customer communication — so your brand doesn’t sound busy or neglected.",
  },
  "digital-marketing": {
    problem:
      "Campaigns, reporting, and content ops stall because nobody owns the day-to-day marketing execution.",
    tasks: [
      "Campaign coordination and checklist work",
      "Reporting pulls and status updates",
      "Content operations and asset handoffs",
      "Research and competitive monitoring support",
    ],
    gain:
      "Marketing capacity that keeps the machine moving while your strategists stay on the work that needs judgment.",
  },
  "social-media": {
    problem:
      "Posting, community replies, and asset coordination fall behind — and the brand goes quiet when you’re busy.",
    tasks: [
      "Content scheduling and publishing support",
      "Community replies and comment triage",
      "Asset gathering and creative coordination",
      "Basic performance reporting",
    ],
    gain:
      "A dedicated social seat that keeps channels active and organized without turning your week into a content firefight.",
  },
  hr: {
    problem:
      "People admin, records, and onboarding tasks pile up while your managers try to hire and run the business.",
    tasks: [
      "HR records and documentation support",
      "Onboarding checklist administration",
      "Interview scheduling coordination",
      "Internal people-ops follow-ups",
    ],
    gain:
      "HR administration support that keeps people processes moving — so managers aren’t the default ops desk.",
  },
  recruitment: {
    problem:
      "Sourcing, screens, and interview scheduling slow your hiring pipeline when your team is already stretched.",
    tasks: [
      "Candidate sourcing support",
      "Screening coordination against your brief",
      "Interview scheduling and reminders",
      "Pipeline hygiene and status updates",
    ],
    gain:
      "Recruiting support capacity so your hiring managers spend time deciding — not chasing calendars and resumes.",
  },
  sales: {
    problem:
      "Prospect research, CRM cleanup, and follow-ups slip — and opportunities cool while your closers stay buried.",
    tasks: [
      "Prospect and account research",
      "CRM hygiene and data updates",
      "Follow-up sequences and reminders",
      "Appointment and meeting coordination",
    ],
    gain:
      "Sales support that protects pipeline hygiene so your sellers spend more time talking to buyers.",
  },
};

/**
 * Hero tick list for category pages — problem → handoff → gain (+ process).
 * Kept short for the first viewport; detail lives in RoleOutcomes.
 */
export const ROLE_HERO_BENEFITS: Record<CategorySlug, string[]> = {
  "administrative-support": [
    "Inbox, scheduling, and follow-ups stop eating leadership hours",
    "A dedicated admin seat owns triage, docs, and coordination",
    "Your managers get time back for customers and decisions",
    "You interview before anyone joins — we support after hire",
  ],
  bookkeeping: [
    "Invoices, records, and reconciliations stop stacking on your desk",
    "A dedicated bookkeeper owns day-to-day books support",
    "Your finance owner spends less time catching up",
    "You interview before anyone joins — rates discussed for the role",
  ],
  accounting: [
    "Recurring accounting support stops slowing month-end and handoffs",
    "A dedicated seat helps with transactions, schedules, and reporting prep",
    "Extra capacity for the work — not a claim of licensed advice",
    "You interview the shortlist before anyone starts",
  ],
  "customer-service": [
    "Customer questions stop sitting unanswered in the queue",
    "A dedicated support seat owns inquiries, tickets, and status updates",
    "More consistent customer communication for your brand",
    "You interview before anyone joins your team",
  ],
  "digital-marketing": [
    "Campaigns, reporting, and content ops stop stalling for lack of owners",
    "A dedicated marketing seat keeps day-to-day execution moving",
    "Strategists stay on judgment work — not checklist firefights",
    "Marketing-focused shortlist matched to your tools — you interview",
  ],
  "social-media": [
    "Posting and community replies stop falling behind when you’re busy",
    "A dedicated social seat owns scheduling, replies, and asset coordination",
    "Channels stay active without turning your week into a content firefight",
    "You interview before anyone joins — businesses only",
  ],
  hr: [
    "People admin and onboarding tasks stop defaulting to busy managers",
    "A dedicated HR support seat owns records, checklists, and scheduling",
    "People processes keep moving while leaders run the business",
    "You interview before anyone joins — businesses only",
  ],
  recruitment: [
    "Sourcing, screens, and interview scheduling stop slowing your pipeline",
    "A dedicated recruiting seat owns coordination and pipeline hygiene",
    "Hiring managers spend time deciding — not chasing calendars",
    "You interview the shortlist — businesses only",
  ],
  sales: [
    "Prospect research, CRM hygiene, and follow-ups stop slipping",
    "A dedicated sales support seat protects pipeline basics",
    "Sellers spend more time talking to buyers",
    "You interview before anyone joins — staffing, not software",
  ],
};

export function roleHeroBenefits(slug: CategorySlug): string[] {
  return ROLE_HERO_BENEFITS[slug];
}

export type EmployerFaqItem = { q: string; a: string };

/** Shared employer FAQ — verified operating details only. */
export function employerFaq(
  market: MarketId,
  roleLabel?: string | null,
  category?: CategorySlug | null,
): EmployerFaqItem[] {
  const isAu = market === "au";
  const hours = isAu ? "Australian business hours" : "US business hours";
  const marketNoun = isAu ? "Australian businesses" : "US businesses";
  const outcome = category ? ROLE_OUTCOMES[category] : null;

  return [
    {
      q: "Is this for businesses or job seekers?",
      a: "Businesses only. If you’re looking for work, choose “I’m looking for a job” — that opens our Philippines careers experience, not this employer form.",
    },
    {
      q: "Where are the coworkers located?",
      a: "We recruit dedicated Filipino professionals in the Philippines. You get a remote team member matched to your role — not a rotating freelance pool.",
    },
    {
      q: isAu
        ? "Can they work Australian business hours?"
        : "Can they work US business hours?",
      a: `Yes — we recruit for ${hours}. Hours and must-haves are confirmed in the hiring conversation before recruiting starts.`,
    },
    {
      q: "Full-time or part-time?",
      a: "Tell us the capacity you need when you send the role. Availability depends on the seat and candidates — we’ll confirm options in conversation.",
    },
    {
      q: roleLabel
        ? `What can a ${roleLabel} coworker take on?`
        : "What roles can you support?",
      a: outcome
        ? `${outcome.problem} Typical handoffs include ${outcome.tasks.join("; ")}. ${outcome.gain} Describe your tools and must-haves in the form — we shortlist for that seat.`
        : roleLabel
          ? `This page is for ${roleLabel}. Describe the day-to-day work and tools — we shortlist screened candidates for that seat. Browse Services for other roles.`
          : "Common seats include admin / VA support, bookkeeping, customer service, digital marketing, social media, HR, recruitment support, and sales support. Pick the closest role or tell us in the form.",
    },
    {
      q: "How does matching and interviewing work?",
      a: "You tell us the role. We recruit and screen against your brief, then you interview the shortlist on video and decide. There’s no pressure to hire if it isn’t the right fit.",
    },
    {
      q: "Do you handle payroll and employment admin?",
      a: isAu
        ? "Yes. Once you hire, we support onboarding, employment operations, and account support so you’re not building another local employment stack from scratch."
        : "Yes. Once you hire, we support onboarding, payroll, and account support so you’re not building another local employment stack from scratch.",
    },
    {
      q: "How is this different from hiring a freelancer?",
      a: `Virtual Coworker is employer-focused staffing for ${marketNoun}: dedicated seats, candidate matching, interviews you control, and ongoing employment support — not a gig marketplace.`,
    },
    {
      q: "Are rates transparent?",
      a: "We discuss rates once we understand the role, hours, and seniority. A form submission starts that conversation — it is not a quote, contract, or instant hire.",
    },
    {
      q: "What happens after I submit the form?",
      a: "Our team follows up for a short hiring conversation. From there we take your brief, shortlist screened candidates, and you interview before anyone starts. You can also book a time on the thank-you page if you want to move faster.",
    },
  ];
}
