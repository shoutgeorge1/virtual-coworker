/**
 * Shared employer CRO copy - pain → relief → gain.
 * Used by market landings, category pages, services, and how-it-works.
 * Claims stay within verified site facts (see config/site.ts, hiring-process.ts).
 *
 * Voice: US = punchy RSA / human sales. AU = same logic, understated B2B English
 * (have a chat, no lock-in, sorted) - not US copy with “Australian hours” swapped in.
 */

import type { MarketId } from "./markets";
import type { CategorySlug } from "./categories";

/** US default CTA. Prefer primaryHireCta(market) on employer surfaces.
 * Competitors push book/strategy call (MyOutDesk) — not “demo”, not phone-as-hero. */
export const PRIMARY_HIRE_CTA = "Book a Free Strategy Call";

export function primaryHireCta(market: MarketId): string {
  return market === "au" ? "Book a free strategy call" : PRIMARY_HIRE_CTA;
}

export type PainGainCopy = {
  eyebrow: string;
  title: string;
  lead: string;
  beforeLabel: string;
  afterLabel: string;
  before: string[];
  after: string[];
};

export type PainGainBoom = { title: string; body: string };

export function painGainCopy(market: MarketId): PainGainCopy {
  if (market === "au") {
    return {
      eyebrow: "Why this works",
      title: "Your week is full. A virtual coworker takes the load.",
      lead:
        "You don’t need another tool. You need a dedicated Filipino teammate - strong value, works hard, learns fast, and stays on Australian hours.",
      beforeLabel: "What’s chewing up the week",
      afterLabel: "What changes once they’re in",
      before: [
        "Email, calendars and follow-ups chew up the day",
        "You worry about handing over email, passwords and client data",
        "Your best people get stuck on work below their pay",
        "The work that grows the business keeps waiting",
      ],
      after: [
        "A dedicated Filipino teammate on Australian hours - brief them once, then they’re on it",
        "You keep control of access. MFA, individual logins, a password manager - we talk through it before anyone logs in.",
        "Your local team gets time back for customers and growth",
        "Australian business hours. We handle employment admin so you don’t.",
      ],
    };
  }
  return {
    eyebrow: "Why this works",
    title: "Your week is full. A virtual coworker clears it.",
    lead:
      "You don’t need another tool. You need a dedicated Filipino teammate - strong value, works hard, learns fast, and stays on your hours.",
    beforeLabel: "What’s eating your week",
    afterLabel: "What changes with a virtual coworker",
    before: [
      "Email, calendars, and follow-ups eat your day",
      "You worry about handing over email, passwords, and client data",
      "Your best people get stuck doing work below their pay",
      "The work that grows the business keeps waiting",
    ],
    after: [
      "A dedicated Filipino teammate on your hours - train them once, then they’re on it",
      "You keep control of access. MFA, individual logins, a password manager - we talk through it before anyone logs in.",
      "Your local team gets time back for customers and growth",
      "US business hours. We handle payroll so you don’t.",
    ],
  };
}

export function painGainBooms(market: MarketId): PainGainBoom[] {
  if (market === "au") {
    return [
      {
        title: "Dedicated Filipino pros",
        body: "On Australian hours. They want this work. No drama.",
      },
      {
        title: "You interview. You pick.",
        body: "Good candidates. Your call. Nobody starts until you say yes.",
      },
      {
        title: "Access stays yours.",
        body: "MFA, individual logins, a password manager. We walk through the controls before anyone starts.",
      },
      {
        title: "They hit the ground running.",
        body: "Onboarded, on Australian hours, ready to work.",
      },
    ];
  }
  return [
    {
      title: "Dedicated Filipino pros",
      body: "Watching your back. On your hours. They want this work.",
    },
    {
      title: "You interview. You pick.",
      body: "Great candidates. Your choice. Nobody starts until you say yes.",
    },
    {
      title: "Access stays yours.",
      body: "MFA, individual logins, a password manager. We walk through the controls before anyone starts.",
    },
    {
      title: "They hit the ground running.",
      body: "Onboarded, on your clock, taking you to the next level.",
    },
  ];
}

export type RoleOutcome = {
  /** Short business problem for this role page. */
  problem: string;
  /** Concrete tasks a dedicated coworker can take over. */
  tasks: string[];
  /** Operational gain - no invented metrics. */
  gain: string;
};

const ROLE_TASKS: Record<CategorySlug, string[]> = {
  "administrative-support": [
    "Inbox triage and routine replies",
    "Calendar and meeting coordination",
    "Document prep and file organisation",
    "Follow-ups that otherwise slip",
  ],
  bookkeeping: [
    "Invoice and bill support",
    "Day-to-day record keeping",
    "Bank and account reconciliations",
    "Routine reporting assistance",
  ],
  accounting: [
    "Transaction support and coding assistance",
    "Schedule and document preparation",
    "Routine reporting support",
    "Coordination with your accountant or finance lead",
  ],
  "customer-service": [
    "Customer inquiries across email or chat",
    "Queue and ticket follow-through",
    "Order or account status updates",
    "Clear handoffs when something needs a manager",
  ],
  "digital-marketing": [
    "Campaign coordination and checklist work",
    "Reporting pulls and status updates",
    "Content operations and asset handoffs",
    "Research and competitive monitoring support",
  ],
  "social-media": [
    "Content scheduling and publishing support",
    "Community replies and comment triage",
    "Asset gathering and creative coordination",
    "Basic performance reporting",
  ],
  hr: [
    "HR records and documentation support",
    "Onboarding checklist administration",
    "Interview scheduling coordination",
    "Internal people-ops follow-ups",
  ],
  recruitment: [
    "Candidate sourcing support",
    "Screening coordination against your brief",
    "Interview scheduling and reminders",
    "Pipeline hygiene and status updates",
  ],
  sales: [
    "Prospect and account research",
    "CRM hygiene and data updates",
    "Follow-up sequences and reminders",
    "Appointment and meeting coordination",
  ],
};

const ROLE_OUTCOMES_US: Record<CategorySlug, Omit<RoleOutcome, "tasks">> = {
  "administrative-support": {
    problem:
      "Inbox, scheduling, and follow-ups keep stealing the week from you or your managers.",
    gain:
      "A dedicated admin who learns your rhythm - so leadership time goes back to customers and decisions.",
  },
  bookkeeping: {
    problem:
      "Invoices, records, and reconciliations stack up while the business waits on clean numbers.",
    gain:
      "Steadier books so your finance owner spends less time catching up and more time running the business.",
  },
  accounting: {
    problem:
      "Recurring accounting support piles up and slows month-end, reporting, and handoffs.",
    gain:
      "Extra capacity for the recurring work - not licensed advice, just the seat that keeps close moving.",
  },
  "customer-service": {
    problem:
      "Customer questions sit too long, queues build, and your team loses time on the same requests.",
    gain:
      "Faster, more consistent customer communication - so the brand doesn’t sound neglected.",
  },
  "digital-marketing": {
    problem:
      "Campaigns, reporting, and content ops stall because nobody owns day-to-day marketing.",
    gain:
      "A marketing seat that keeps the machine moving while your strategists stay on judgment work.",
  },
  "social-media": {
    problem:
      "Posting and community replies fall behind - and the brand goes quiet when you’re busy.",
    gain:
      "A dedicated social seat that keeps channels active without turning your week into a content firefight.",
  },
  hr: {
    problem:
      "People admin, records, and onboarding pile up while managers try to hire and run the business.",
    gain:
      "HR admin that keeps people processes moving - so managers aren’t the default ops desk.",
  },
  recruitment: {
    problem:
      "Sourcing, screens, and interview scheduling slow the pipeline when your team is already stretched.",
    gain:
      "Recruiting support so hiring managers spend time deciding - not chasing calendars and resumes.",
  },
  sales: {
    problem:
      "Appointment setting, research, CRM cleanup, and follow-ups slip while closers stay buried.",
    gain:
      "Sales support that protects the pipeline so sellers spend more time talking to buyers.",
  },
};

const ROLE_OUTCOMES_AU: Record<CategorySlug, Omit<RoleOutcome, "tasks">> = {
  "administrative-support": {
    problem:
      "Inbox, scheduling and follow-ups still land back on you or your managers.",
    gain:
      "A dedicated virtual assistant or EA who learns how you work - so leadership time goes back to customers and decisions.",
  },
  bookkeeping: {
    problem:
      "Invoices, records and reconciliations stack up while the rest of the business waits on clean numbers.",
    gain:
      "Steadier books so your finance lead spends less time catching up and more time on the actual business.",
  },
  accounting: {
    problem:
      "Recurring accounting support piles up and slows month-end, reporting and handoffs to your accountant.",
    gain:
      "Extra capacity for the recurring work - not a substitute for your accountant, just the seat that keeps close moving.",
  },
  "customer-service": {
    problem:
      "Customer questions sit too long, queues build, and the same requests keep bouncing back to your team.",
    gain:
      "More consistent customer communication - so the brand doesn’t sound like nobody’s home.",
  },
  "digital-marketing": {
    problem:
      "Campaigns, reporting and content ops stall because nobody owns the day-to-day marketing.",
    gain:
      "A marketing seat that keeps things moving while your strategists stay on the work that needs judgment.",
  },
  "social-media": {
    problem:
      "Posting and community replies slip when you’re busy - and the channels go quiet.",
    gain:
      "A dedicated social seat that keeps channels active without turning the week into a content scramble.",
  },
  hr: {
    problem:
      "People admin, records and onboarding pile up while managers try to hire and run the business.",
    gain:
      "HR admin that keeps people processes moving - so managers aren’t the default ops desk.",
  },
  recruitment: {
    problem:
      "Sourcing, screens and interview scheduling slow hiring when the team is already stretched.",
    gain:
      "Recruiting support so hiring managers spend time deciding - not chasing calendars and CVs.",
  },
  sales: {
    problem:
      "Research, CRM cleanup and follow-ups slip - and opportunities cool while closers stay buried.",
    gain:
      "Sales support that keeps the pipeline tidy so your sellers spend more time talking to buyers.",
  },
};

/** US default - prefer roleOutcomes(slug, market) on employer surfaces. */
export const ROLE_OUTCOMES: Record<CategorySlug, RoleOutcome> = Object.fromEntries(
  (Object.keys(ROLE_OUTCOMES_US) as CategorySlug[]).map((slug) => [
    slug,
    { ...ROLE_OUTCOMES_US[slug], tasks: usTasks(slug) },
  ]),
) as Record<CategorySlug, RoleOutcome>;

function usTasks(slug: CategorySlug): string[] {
  if (slug === "administrative-support") {
    return [
      "Inbox triage and routine replies",
      "Calendar and meeting coordination",
      "Document prep and file organization",
      "Follow-ups that otherwise slip",
    ];
  }
  return ROLE_TASKS[slug];
}

export function roleOutcomes(
  slug: CategorySlug,
  market: MarketId = "us",
): RoleOutcome {
  const base = market === "au" ? ROLE_OUTCOMES_AU[slug] : ROLE_OUTCOMES_US[slug];
  const tasks =
    market === "au" ? ROLE_TASKS[slug] : usTasks(slug);
  return { ...base, tasks };
}

const ROLE_HERO_BENEFITS_US: Record<CategorySlug, string[]> = {
  "administrative-support": [
    "Inbox, scheduling, and follow-ups stop eating leadership hours",
    "A dedicated admin seat owns triage, docs, and coordination",
    "Your managers get time back for customers and decisions",
    "You interview before anyone joins - we handle payroll after",
  ],
  bookkeeping: [
    "Invoices, records, and reconciliations stop stacking on your desk",
    "A dedicated bookkeeper owns day-to-day books support",
    "Your finance owner spends less time catching up",
    "You interview before anyone joins - rates discussed for the role",
  ],
  accounting: [
    "Recurring accounting support stops slowing month-end and handoffs",
    "A dedicated seat helps with transactions, schedules, and reporting prep",
    "Extra capacity for the work - not a claim of licensed advice",
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
    "Strategists stay on judgment work - not checklist firefights",
    "Marketing-focused shortlist matched to your tools - you interview",
  ],
  "social-media": [
    "Posting and community replies stop falling behind when you’re busy",
    "A dedicated social seat owns scheduling, replies, and asset coordination",
    "Channels stay active without turning your week into a content firefight",
    "You interview before anyone joins - businesses only",
  ],
  hr: [
    "People admin and onboarding stop defaulting to busy managers",
    "A dedicated HR support seat owns records, checklists, and scheduling",
    "People processes keep moving while leaders run the business",
    "You interview before anyone joins - businesses only",
  ],
  recruitment: [
    "Sourcing, screens, and interview scheduling stop slowing your pipeline",
    "A dedicated recruiting seat owns coordination and pipeline hygiene",
    "Hiring managers spend time deciding - not chasing calendars",
    "You interview the shortlist - businesses only",
  ],
  sales: [
    "Appointment setting, research, CRM hygiene, and follow-ups stop slipping",
    "A dedicated sales support seat protects pipeline basics",
    "Sellers spend more time talking to buyers",
    "You interview before anyone joins - staffing, not a job board",
  ],
};

const ROLE_HERO_BENEFITS_AU: Record<CategorySlug, string[]> = {
  "administrative-support": [
    "Inbox, scheduling and follow-ups stop landing back on you",
    "A dedicated virtual assistant or EA owns the day-to-day admin",
    "Your managers get time back for customers and decisions",
    "You interview before anyone joins - we handle employment admin after",
  ],
  bookkeeping: [
    "Invoices, records and reconciliations stop stacking on your desk",
    "A dedicated bookkeeper owns the day-to-day books",
    "Your finance lead spends less time catching up",
    "You interview before anyone joins - rates discussed for the role",
  ],
  accounting: [
    "Recurring accounting support stops slowing month-end and handoffs",
    "A dedicated seat helps with transactions, schedules and reporting prep",
    "Extra capacity for the work - not a substitute for your accountant",
    "You interview the shortlist before anyone starts",
  ],
  "customer-service": [
    "Customer questions stop sitting unanswered in the queue",
    "A dedicated support seat owns inquiries, tickets and status updates",
    "More consistent customer communication for your brand",
    "You interview before anyone joins your team",
  ],
  "digital-marketing": [
    "Campaigns, reporting and content ops stop stalling for lack of an owner",
    "A dedicated marketing seat keeps the day-to-day moving",
    "Strategists stay on judgment work - not checklist firefights",
    "Marketing-focused shortlist matched to your tools - you interview",
  ],
  "social-media": [
    "Posting and community replies stop slipping when you’re busy",
    "A dedicated social seat owns scheduling, replies and asset coordination",
    "Channels stay active without turning the week into a content scramble",
    "You interview before anyone joins - businesses only",
  ],
  hr: [
    "People admin and onboarding stop defaulting to busy managers",
    "A dedicated HR support seat owns records, checklists and scheduling",
    "People processes keep moving while leaders run the business",
    "You interview before anyone joins - businesses only",
  ],
  recruitment: [
    "Sourcing, screens and interview scheduling stop slowing hiring",
    "A dedicated recruiting seat owns coordination and pipeline hygiene",
    "Hiring managers spend time deciding - not chasing calendars",
    "You interview the shortlist - businesses only",
  ],
  sales: [
    "Research, CRM hygiene and follow-ups stop falling through",
    "A dedicated sales support seat keeps the pipeline tidy",
    "Sellers spend more time talking to buyers",
    "You interview before anyone joins - staffing, not a job board",
  ],
};

export const ROLE_HERO_BENEFITS = ROLE_HERO_BENEFITS_US;

export function roleHeroBenefits(
  slug: CategorySlug,
  market: MarketId = "us",
): string[] {
  return market === "au" ? ROLE_HERO_BENEFITS_AU[slug] : ROLE_HERO_BENEFITS_US[slug];
}

export type EmployerFaqItem = { q: string; a: string };

/** Shared employer FAQ - verified operating details only. */
export function employerFaq(
  market: MarketId,
  roleLabel?: string | null,
  category?: CategorySlug | null,
): EmployerFaqItem[] {
  const isAu = market === "au";
  const hours = isAu ? "Australian business hours" : "US business hours";
  const marketNoun = isAu ? "Australian businesses" : "US businesses";
  const outcome = category ? roleOutcomes(category, market) : null;

  return [
    {
      q: "Is Virtual Coworker a real staffing company?",
      a: isAu
        ? "Yes. We’ve placed Filipino staff for businesses since 2011, with offices in the US and Australia. A staffing partner - not a freelance marketplace or job board."
        : "Yes. We’ve placed Filipino staff for businesses since 2011, with offices supporting the US and Australia. You’re talking to a staffing partner - not a freelance marketplace or job board.",
    },
    {
      q: "Where are the coworkers located?",
      a: isAu
        ? "Dedicated Filipino professionals in the Philippines. You get a dedicated virtual assistant matched to your role - not a rotating freelance pool."
        : "We recruit dedicated Filipino professionals in the Philippines. You get a remote team member matched to your role - not a rotating freelance pool.",
    },
    {
      q: isAu
        ? "Can they work Australian business hours?"
        : "Can they work US business hours?",
      a: isAu
        ? `Yes - we recruit for ${hours}. Hours and must-haves get confirmed on the chat before recruiting starts.`
        : `Yes - we recruit for ${hours}. Hours and must-haves are confirmed in the hiring conversation before recruiting starts.`,
    },
    {
      q: "Full-time or part-time?",
      a: isAu
        ? "Both. 20 hours/week minimum. Start part-time without committing to a full-time hire - obligation free, at no cost."
        : "Both. 20 hours/week minimum. Start part-time, then scale hours as you need them - obligation free, at no cost.",
    },
    {
      q: roleLabel
        ? `What can a ${roleLabel} coworker take on?`
        : "What roles can you support?",
      a: outcome
        ? isAu
          ? `${outcome.problem} Typical handoffs include ${outcome.tasks.join("; ")}. ${outcome.gain} Tell us the tools and must-haves - we shortlist for that role.`
          : `${outcome.problem} Typical handoffs include ${outcome.tasks.join("; ")}. ${outcome.gain} Describe your tools and must-haves in the form - we shortlist for that seat.`
        : roleLabel
          ? isAu
            ? `This page is for ${roleLabel}. Tell us the day-to-day work and tools - we shortlist screened candidates for that role. Browse Services for other roles.`
            : `This page is for ${roleLabel}. Describe the day-to-day work and tools - we shortlist screened candidates for that seat. Browse Services for other roles.`
          : isAu
            ? "Common roles include admin / virtual assistant support, bookkeeping, customer service, digital marketing, social media, HR, recruitment support and sales support. Australian and New Zealand industry seats (real estate, construction, project administration, healthcare) are a targeted hire, not a generic VA. Pick the closest fit or tell us in the form."
            : "Common seats include admin / virtual assistant support, bookkeeping, customer service, digital marketing, social media, HR, recruitment support, and sales support. Pick the closest role or tell us in the form.",
    },
    {
      q: "How does matching and interviewing work?",
      a: isAu
        ? "Tell us the role. We recruit and screen for that job, not a generic VA. You interview the shortlist on video and decide. No pressure to hire if it isn’t a fit."
        : "You tell us the role. We recruit and screen for that job, not a generic VA. You interview the shortlist on video and decide. No pressure to hire if it isn’t the right fit.",
    },
    {
      q: "How do I keep systems and data safe?",
      a: "You stay in control of access. Individual logins, MFA, a password manager, restricted permissions, NDAs, and endpoint security. We walk through the practical steps on the call rather than asserting that offshore is automatically safe.",
    },
    {
      q: isAu
        ? "Do you handle employment admin?"
        : "Do you handle payroll and employment admin?",
      a: isAu
        ? "Yes. Once you hire, we handle onboarding, employment admin and account support. You forget the paperwork."
        : "Yes. Once you hire, we handle onboarding, payroll, and account support. You forget the paperwork.",
    },
    {
      q: "How is this different from hiring a freelancer?",
      a: isAu
        ? `Dedicated seats for ${marketNoun}. You interview. You pick. We handle employment admin after you hire. Not a gig marketplace.`
        : `Dedicated seats for ${marketNoun}. You interview. You pick. We handle payroll after you hire. Not a gig marketplace.`,
    },
    {
      q: "Are rates transparent?",
      a: isAu
        ? "We talk through rates once we understand the role, hours, seniority and any Australian or New Zealand industry experience. A form starts a conversation - not a quote, contract or instant hire. No lock-in from the first chat."
        : "We discuss rates once we understand the role, hours, and seniority. Skill and responsibility set the number - not a cheap-labor headline. A form starts a conversation - not a quote, contract, or instant hire.",
    },
    {
      q: "What happens after I submit the form?",
      a: isAu
        ? "A member of our team will follow up for a short hiring chat - obligation free, at no cost. Then we take your brief, shortlist people, and you interview before anyone starts. You can book a time on the thank-you page if you’d rather talk sooner."
        : "A member of our team will follow up for a short hiring consult - obligation free, at no cost. Then we take your brief, shortlist people, and you interview before anyone starts. You can book a time on the thank-you page if you want to move faster.",
    },
  ];
}

export type StopCloserSurface = "home" | "services" | "how" | CategorySlug;

export type StopCloserCopy = {
  eyebrow: string;
  title: string;
  lead: string;
};

const CLOSER_EYEBROW_US = "Next step";
const CLOSER_EYEBROW_AU = "Next step";
const CLOSER_TITLE_US = "Talk with a staffing specialist.";
const CLOSER_TITLE_AU = "Talk with a staffing specialist.";

const CLOSER_US: Record<StopCloserSurface, StopCloserCopy> = {
  home: {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "Tell us the role. We’ll follow up for a short hiring consult - obligation free, at no cost. You interview before anyone starts.",
  },
  services: {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "Pick the seat that fits, then start a short hiring consult - obligation free, at no cost. We match a dedicated Filipino teammate to the role.",
  },
  how: {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "The process is simple. Start with a short hiring consult - obligation free, at no cost. We recruit and screen; you interview and decide.",
  },
  "administrative-support": {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "If admin is eating the week, start a short hiring consult - obligation free, at no cost. We match a dedicated Filipino virtual assistant or EA.",
  },
  bookkeeping: {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "If invoices are stacking up, start a short hiring consult - obligation free, at no cost. We match a dedicated Filipino bookkeeper.",
  },
  accounting: {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "If month-end is piling up, start a short hiring consult - obligation free, at no cost. We match a dedicated Filipino accounting seat.",
  },
  "customer-service": {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "If customers are waiting on replies, start a short hiring consult - obligation free, at no cost. We match a dedicated Filipino support teammate.",
  },
  "digital-marketing": {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "If campaigns are stalling, start a short hiring consult - obligation free, at no cost. We match a dedicated Filipino marketer.",
  },
  "social-media": {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "If channels are going quiet, start a short hiring consult - obligation free, at no cost. We match a dedicated Filipino social teammate.",
  },
  hr: {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "If people admin is still on managers, start a short hiring consult - obligation free, at no cost. We match dedicated Filipino HR support.",
  },
  recruitment: {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "If the hiring pipeline is slowing, start a short hiring consult - obligation free, at no cost. We match dedicated Filipino recruiting support.",
  },
  sales: {
    eyebrow: CLOSER_EYEBROW_US,
    title: CLOSER_TITLE_US,
    lead: "If follow-ups are slipping, start a short hiring consult - obligation free, at no cost. We match a dedicated Filipino setter or sales support seat.",
  },
};

const CLOSER_AU: Record<StopCloserSurface, StopCloserCopy> = {
  home: {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "Tell us the role. We’ll follow up for a short hiring chat - obligation free, at no cost. You interview before anyone starts.",
  },
  services: {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "Pick the role that fits, then start a short hiring chat - obligation free, at no cost. We match a dedicated Filipino teammate for Australian hours.",
  },
  how: {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "The process is straightforward. Start with a short hiring chat - obligation free, at no cost. We recruit and screen; you interview and decide.",
  },
  "administrative-support": {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "If admin is running the week, start a short hiring chat - obligation free, at no cost. We match a dedicated Filipino virtual assistant or EA for Australian hours.",
  },
  bookkeeping: {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "If the books are falling behind, start a short hiring chat - obligation free, at no cost. We match a dedicated Filipino bookkeeper.",
  },
  accounting: {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "If month-end is a scramble, start a short hiring chat - obligation free, at no cost. We match dedicated Filipino accounting support.",
  },
  "customer-service": {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "If customers are waiting on replies, start a short hiring chat - obligation free, at no cost. We match a dedicated Filipino support teammate for Australian hours.",
  },
  "digital-marketing": {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "If marketing is slipping, start a short hiring chat - obligation free, at no cost. We match a dedicated Filipino marketer.",
  },
  "social-media": {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "If the channels have gone quiet, start a short hiring chat - obligation free, at no cost. We match a dedicated Filipino social teammate.",
  },
  hr: {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "If people ops is still on managers, start a short hiring chat - obligation free, at no cost. We match dedicated Filipino HR support.",
  },
  recruitment: {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "If hiring is stuck in the admin, start a short hiring chat - obligation free, at no cost. We match dedicated Filipino recruiting support.",
  },
  sales: {
    eyebrow: CLOSER_EYEBROW_AU,
    title: CLOSER_TITLE_AU,
    lead: "If follow-ups are falling through, start a short hiring chat - obligation free, at no cost. We match dedicated Filipino sales support.",
  },
};

export function stopCloserCopy(
  market: MarketId,
  surface: StopCloserSurface = "home",
): StopCloserCopy {
  const table = market === "au" ? CLOSER_AU : CLOSER_US;
  return table[surface] || table.home;
}
