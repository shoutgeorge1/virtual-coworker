/**
 * Isolated message challenger (Concept A: capacity and cost relief).
 *
 * Hypothesis only. Not live /us or /au. Preview routes:
 *   /prototype/capacity/us
 *   /prototype/capacity/au
 *
 * Form/gate stays GuidedMatchGate. Copy around it is the test.
 * Claims below are from virtualcoworker.com, TRUST_PROOF, and PUBLIC_QUOTES.
 */

import type { MarketId } from "./markets";
import {
  COMPANY_IDENTITY,
  PUBLIC_QUOTES,
  SITE,
  TRUST_PROOF,
  googleBusinessForMarket,
} from "./site";

export const CAPACITY_CHALLENGER_ID = "capacity-a" as const;
export const CAPACITY_CHALLENGER_PATHS = {
  us: "/us/capacity",
  au: "/au/capacity",
} as const;

export type CapacitySituation = { title: string; body: string };
export type CapacityOutcome = { title: string; body: string };
export type CapacityProof = { title: string; body: string };
export type CapacityCompareRow = {
  option: string;
  screening: string;
  chooses: string;
  employment: string;
  support: string;
  dedicated: string;
  highlight?: boolean;
};
export type CapacityFaq = { q: string; a: string };
export type CapacityStep = { k: string; t: string; d: string };

export type CapacityChallengerCopy = {
  market: MarketId;
  eyebrow: string;
  h1: string;
  lead: string;
  primaryCta: string;
  secondaryCta: string;
  formIntro: string;
  proofStrip: string[];
  situationsEyebrow: string;
  situationsTitle: string;
  situations: CapacitySituation[];
  outcomesEyebrow: string;
  outcomesTitle: string;
  outcomes: CapacityOutcome[];
  compareEyebrow: string;
  compareTitle: string;
  compareLead: string;
  compareRows: CapacityCompareRow[];
  proofEyebrow: string;
  proofTitle: string;
  proofs: CapacityProof[];
  featuredQuoteIndex: number;
  processEyebrow: string;
  processTitle: string;
  processLead: string;
  steps: CapacityStep[];
  gateEyebrow: string;
  finalTitle: string;
  finalLead: string;
  faqs: CapacityFaq[];
  phoneDisplay: string;
  phoneHref: string;
  adminLabel: string;
  hoursLabel: string;
  entity: string;
  nap: string;
  heroSrc: string;
  heroAlt: string;
  closerSrc: string;
  closerAlt: string;
  teamSrc: string;
  teamAlt: string;
  sceneSrc: string;
  sceneAlt: string;
  googleLine: string;
  clutchLine: string;
  sinceYear: number;
  previewNote: string;
};

const KYRSTIN_INDEX = PUBLIC_QUOTES.findIndex((q) => q.name === "Kyrstin H.");
const FEATURED_QUOTE_INDEX = KYRSTIN_INDEX >= 0 ? KYRSTIN_INDEX : 0;

function compareRows(adminLabel: string): CapacityCompareRow[] {
  return [
    {
      option: "Freelancer marketplace",
      screening: "Mostly you",
      chooses: "Yes",
      employment: "You",
      support: "No",
      dedicated: "Not guaranteed",
    },
    {
      option: "Job board or local hire",
      screening: "You",
      chooses: "Yes",
      employment: "You",
      support: "You",
      dedicated: "Yes",
    },
    {
      option: "Virtual Coworker",
      screening: "We source and vet",
      chooses: "Yes - you interview",
      employment: adminLabel,
      support: "Yes, after they start",
      dedicated: "Yes, to your business",
      highlight: true,
    },
  ];
}

export function capacityChallengerCopy(market: MarketId): CapacityChallengerCopy {
  const au = market === "au";
  const google = googleBusinessForMarket(market);
  const adminLabel = au ? "Employment admin handled by us" : "Payroll and HR handled by us";
  const hours = au ? "Australian business hours" : "US business hours";
  const localHire = au ? "local headcount" : "local hire";

  const faqs: CapacityFaq[] = [
    {
      q: au ? "Can they work Australian hours?" : "Can they work US hours?",
      a: au
        ? "Yes. We recruit for Australian business hours. Hours are confirmed before recruiting starts."
        : "Yes. We recruit for US business hours. Hours are confirmed before recruiting starts.",
    },
    {
      q: "Do I choose the candidate?",
      a: "Yes. We source and vet. You interview on video and decide. Nobody starts until you say yes. No pressure to hire if it is not a fit.",
    },
    {
      q: "Is this full-time or part-time?",
      a: "Both. 20 hours/week minimum. Start part-time, then scale hours as you need them. Dedicated staff, not a rotating freelancer for the afternoon.",
    },
    {
      q: au ? "Who handles employment administration?" : "Who handles payroll and HR?",
      a: au
        ? "Once you hire, we handle onboarding, employment admin, and the time tracker."
        : "Once you hire, we handle onboarding, payroll and HR, and the time tracker.",
    },
    {
      q: "How are candidates screened?",
      a: "Our Philippines recruitment specialists source and vet candidates against your brief. The company identifies the top 1% of Filipino virtual assistants with proven skills and strong English. You then interview the people we present.",
    },
    {
      q: "What if the match is not right?",
      a: "You interview before anyone starts. There is no pressure to hire if the shortlist is not a fit. After placement, ongoing account support stays with you. Specific replacement terms are confirmed when you hire - we do not publish a live guarantee here.",
    },
    {
      q: "How long does recruiting normally take?",
      a: "A staffing specialist reviews the role, schedule, and requirements, then sends a hiring brief with the recruiting path, timeline, and hourly-rate structure. We recruit after you are aligned. We do not publish a live day-count on this page.",
    },
    {
      q: "How are rates determined?",
      a: au
        ? "Hourly rates depend on the role, hours, seniority, and specialized or Australian/New Zealand industry experience. The hiring brief explains the structure. Live prices are not listed here."
        : "Hourly rates depend on the role, hours, and seniority. Skill and responsibility set the number - not a cheap-labor headline. The hiring brief explains the structure. Live prices are not listed here.",
    },
    {
      q: "How do I keep systems and data safe?",
      a: "You stay in control of access. Individual logins, MFA, a password manager, restricted permissions, NDAs, and endpoint security. We walk through the practical steps on the call rather than asserting that offshore is automatically safe.",
    },
    {
      q: "Is this a freelancer marketplace?",
      a: au
        ? "No. Dedicated Filipino professionals for your business. You interview. You pick. We handle employment admin after you hire. Not a gig marketplace."
        : "No. Dedicated Filipino professionals for your business. You interview. You pick. We handle payroll after you hire. Not a gig marketplace.",
    },
  ];

  return {
    market,
    eyebrow: au
      ? "For growing Australian companies hiring staff"
      : "For growing companies hiring staff",
    h1: au
      ? "Get the work off your team's plate - without another expensive local hire."
      : "Get the work off your team's plate - without another expensive local hire.",
    lead: au
      ? `Choose a vetted Filipino specialist who works ${hours}. Virtual Coworker recruits and vets. You interview and choose. We handle employment administration and ongoing support.`
      : `Choose a vetted Filipino specialist who works ${hours}. Virtual Coworker recruits and vets. You interview and choose. We handle payroll, HR, and ongoing support.`,
    primaryCta: "Tell us the role",
    secondaryCta: au ? "Or call" : "Or call",
    formIntro: au
      ? "This page is for employers, not job seekers. Tell us the role. A staffing specialist follows up for a short chat about capacity, hours, and the hiring path. Obligation free. Not an instant hire."
      : "This page is for employers, not job seekers. Tell us the role. A staffing specialist follows up about capacity, hours, and the hiring path - usually the same business day. Obligation free. Not an instant hire.",
    proofStrip: [
      `Since ${TRUST_PROOF.sinceYear}`,
      "Save up to 80% of staffing costs",
      "No recruitment fees",
      "You interview and choose",
    ],
    situationsEyebrow: "If this sounds familiar",
    situationsTitle: "Your existing team is carrying work that should already have a home.",
    situations: [
      {
        title: "Mornings disappear into recurring admin",
        body: "Inbox, calendar, documents, and follow-up keep crowding out the work that actually grows the business.",
      },
      {
        title: "Important follow-up keeps slipping",
        body: "Customers, invoices, and leads wait because nobody dedicated owns the recurring work.",
      },
      {
        title: `Another ${localHire} feels slow and expensive`,
        body: au
          ? "Local headcount adds cost, delay, and employment admin before the work even has an owner."
          : "Local hiring adds payroll cost, delay, and recruitment burden before the work even has an owner.",
      },
      {
        title: "Freelancers still need managing",
        body: "Screening, continuity, and follow-through stay on you. You wanted capacity, not another person to chase.",
      },
    ],
    outcomesEyebrow: "What changes",
    outcomesTitle: "Give the existing team time back - and add a person they can rely on.",
    outcomes: [
      {
        title: "Time back for growth work",
        body: "A dedicated teammate owns the recurring work so managers and specialists can get back to customers and growth.",
      },
      {
        title: "Role-specific capacity",
        body: "Admin, bookkeeping, marketing, customer support, sales, or recruiting support - matched to the seat, not a generic task pile.",
      },
      {
        title: "You stay in control",
        body: "You interview on video and choose who starts. Nobody is assigned to you as a leftover profile.",
      },
      {
        title: au ? "Employment admin handled" : "Payroll and HR handled",
        body: au
          ? "Once you hire, we handle onboarding, employment admin, and the time tracker."
          : "Once you hire, we handle onboarding, payroll and HR, and the time tracker.",
      },
    ],
    compareEyebrow: "Why Virtual Coworker",
    compareTitle: `Add a matched teammate without carrying another ${localHire}.`,
    compareLead: au
      ? "You still choose the person and direct the work. We take on sourcing, employment administration, and ongoing support."
      : "You still choose the person and direct the work. We take on sourcing, payroll and HR, and ongoing support.",
    compareRows: compareRows(adminLabel),
    proofEyebrow: "Proof we can stand behind",
    proofTitle: "A staffing company since 2011 - not a gig app.",
    proofs: [
      {
        title: `Since ${TRUST_PROOF.sinceYear}`,
        body: "US and Australian offices. Philippines recruitment hub. Placing dedicated Filipino staff for businesses.",
      },
      {
        title: "Save up to 80% of staffing costs",
        body: "Company-published comparison with traditional local hiring. Hourly rates still depend on role, hours, and seniority.",
      },
      {
        title: "No recruitment fees",
        body: "Sourcing, vetting, and introductions have no upfront recruitment fee. Your investment goes into the staff member.",
      },
      {
        title: "You interview. You choose.",
        body: "We present vetted people. You meet them on video. Dedicated to your business, full-time or part-time, on your hours.",
      },
    ],
    featuredQuoteIndex: FEATURED_QUOTE_INDEX,
    processEyebrow: "How hiring works",
    processTitle: "A short path from the role to a person you chose.",
    processLead:
      "The hiring brief is how we work. The point of the conversation is capacity, reliability, and a teammate you can keep.",
    steps: [
      {
        k: "1",
        t: "Tell us the role",
        d: "Role, hours, and how many people. That starts a hiring conversation - not a contract.",
      },
      {
        k: "2",
        t: "Confirm the brief",
        d: "A staffing specialist reviews the role, schedule, and requirements: recruiting path, timeline, and hourly-rate structure.",
      },
      {
        k: "3",
        t: "Meet vetted candidates",
        d: "After you are aligned, the Philippines team sources and vets. You meet people on video.",
      },
      {
        k: "4",
        t: "Choose your teammate",
        d: "You decide who starts. Nobody is placed without your yes.",
      },
      {
        k: "5",
        t: au ? "We handle employment support" : "We handle onboarding and payroll",
        d: au
          ? "Onboarding, employment admin, the time tracker, and ongoing account support."
          : "Onboarding, payroll and HR, the time tracker, and ongoing account support.",
      },
    ],
    gateEyebrow: au
      ? "About a minute · obligation free"
      : "About a minute · obligation free",
    finalTitle: au
      ? "Give your team the capacity they have been missing."
      : "Give your team the capacity they've been missing.",
    finalLead: au
      ? "Tell us the role. A specialist will follow up for a short chat - then we recruit if you are aligned."
      : "Tell us the role. A specialist will follow up - then we recruit if you are aligned.",
    faqs,
    phoneDisplay: au ? SITE.auPhoneDisplay : SITE.usPhoneDisplay,
    phoneHref: au ? SITE.auPhoneHref : SITE.usPhoneHref,
    adminLabel: au ? "employment admin" : "payroll and HR",
    hoursLabel: hours,
    entity: au
      ? `${COMPANY_IDENTITY.entityAu} · ABN ${COMPANY_IDENTITY.abn}`
      : COMPANY_IDENTITY.entityUs,
    nap: au
      ? `AU office · ${SITE.addressAu} · ABN ${COMPANY_IDENTITY.abn}`
      : `US office · ${SITE.addressUs}`,
    heroSrc: au ? "/brand/va-au.jpg" : "/brand/va-us.jpg",
    heroAlt: au
      ? "Filipino teammate at work for an Australian business"
      : "Filipino teammate at work for a US business",
    closerSrc: au ? "/brand/hero-au-2026.jpg" : "/brand/hero-us-2026.jpg",
    closerAlt: "Virtual Coworker office photograph",
    teamSrc: "/guided-match/trust-team-office.jpg",
    teamAlt: "Virtual Coworker recruitment team at work",
    sceneSrc: "/guided-match/trust-consult.jpg",
    sceneAlt: "Virtual Coworker consult in the office",
    googleLine: `${google.rating} Google · ${google.reviewCount} reviews`,
    clutchLine: `${TRUST_PROOF.clutch.rating} Clutch · ${TRUST_PROOF.clutch.reviewCount} reviews`,
    sinceYear: TRUST_PROOF.sinceYear,
    previewNote: "",
  };
}

export function capacityQuotes() {
  return PUBLIC_QUOTES.map((q) => ({
    text: q.quote,
    by: `${q.name} · ${q.role}${q.company ? ` · ${q.company}` : ""}`,
    company: q.company || "",
    name: q.name,
  }));
}

export type ChallengerConcept = "capacity" | "time" | "teammate";

export const CHALLENGER_VARIANT: Record<ChallengerConcept, string> = {
  capacity: CAPACITY_CHALLENGER_ID,
  time: "time-b",
  teammate: "teammate-c",
};

export const TIME_CHALLENGER_PATHS = {
  us: "/us/time",
  au: "/au/time",
} as const;

export const TEAMMATE_CHALLENGER_PATHS = {
  us: "/us/teammate",
  au: "/au/teammate",
} as const;

const DAVID_INDEX = PUBLIC_QUOTES.findIndex((q) => q.name === "David Boyd");
const LAURA_INDEX = PUBLIC_QUOTES.findIndex((q) => q.name === "Laura W.");

/** Concept B: time and operational pain. Same claims; different hero. */
export function timeChallengerCopy(market: MarketId): CapacityChallengerCopy {
  const base = capacityChallengerCopy(market);
  const au = market === "au";
  const hours = base.hoursLabel;
  return {
    ...base,
    eyebrow: au
      ? "For owners whose week is already full"
      : "For owners whose week is already full",
    h1: "Stop losing your mornings to work a skilled teammate could own.",
    lead: au
      ? `Add reliable support for the recurring work consuming your team. A vetted Filipino specialist works ${hours}. You interview and choose. We handle employment administration.`
      : `Add reliable support for the recurring work consuming your team. A vetted Filipino specialist works ${hours}. You interview and choose. We handle payroll and HR.`,
    formIntro: au
      ? "This page is for employers, not job seekers. Tell us the role squeezing your week. A staffing specialist follows up for a short chat. Obligation free. Not an instant hire."
      : "This page is for employers, not job seekers. Tell us the role squeezing your week. A staffing specialist follows up - usually the same business day. Obligation free. Not an instant hire.",
    situationsEyebrow: "The week as it is",
    situationsTitle: "Recurring work is eating the hours that should grow the business.",
    situations: [
      {
        title: "Mornings go to the same admin pile",
        body: "Inbox, calendar, documents, and follow-up swallow the start of the day before growth work starts.",
      },
      {
        title: "Follow-up waits on whoever is free",
        body: "Customers, invoices, and leads slip because nobody dedicated owns the recurring work.",
      },
      {
        title: "Growth work keeps getting postponed",
        body: "The team knows what matters. The week fills with execution that a reliable teammate could take.",
      },
      {
        title: "Hiring locally would take months of attention",
        body: au
          ? "Local headcount adds delay and employment admin. You need time back sooner than that."
          : "A local hire adds delay, payroll, and recruiting. You need time back sooner than that.",
      },
    ],
    outcomesEyebrow: "What you get back",
    outcomesTitle: "A teammate who owns the recurring work so you can spend the morning on the business.",
    outcomes: [
      {
        title: "Mornings for growth",
        body: "A dedicated person on your hours takes the repeating work so your team can stay on customers and growth.",
      },
      {
        title: "Consistent execution",
        body: "Full-time or part-time. Dedicated staff - not a rotating freelancer for the afternoon.",
      },
      {
        title: "You still choose the person",
        body: "We source and vet. You interview on video. Nobody starts until you say yes.",
      },
      {
        title: au ? "Employment admin off your plate" : "Payroll and HR off your plate",
        body: au
          ? "Once you hire, we handle onboarding, employment admin, and the time tracker."
          : "Once you hire, we handle onboarding, payroll and HR, and the time tracker.",
      },
    ],
    compareTitle: "Time back without another long local hire.",
    featuredQuoteIndex: DAVID_INDEX >= 0 ? DAVID_INDEX : base.featuredQuoteIndex,
    processLead:
      "The hiring brief is the mechanism. The point is getting your mornings back with a person you chose.",
    finalTitle: "Get the mornings back for the work only you can do.",
    finalLead: au
      ? "Tell us the role stealing the week. A specialist will follow up for a short chat - then we recruit if you are aligned."
      : "Tell us the role stealing the week. A specialist will follow up - then we recruit if you are aligned.",
  };
}

/** Concept C: dedicated teammate, not a freelancer to manage. */
export function teammateChallengerCopy(market: MarketId): CapacityChallengerCopy {
  const base = capacityChallengerCopy(market);
  const au = market === "au";
  const hours = base.hoursLabel;
  return {
    ...base,
    eyebrow: au
      ? "Staffing since 2011 - not a gig marketplace"
      : "Staffing since 2011 - not a gig marketplace",
    h1: "Add a reliable teammate - not another freelancer to manage.",
    lead: au
      ? `Interview and choose a vetted Filipino professional matched to your role, working ${hours}. Virtual Coworker handles recruitment, employment administration, and ongoing support.`
      : `Interview and choose a vetted Filipino professional matched to your role, working ${hours}. Virtual Coworker handles recruitment, payroll and HR, and ongoing support.`,
    formIntro: au
      ? "This page is for employers hiring a dedicated teammate - not job seekers, and not a freelancer directory. Tell us the role. A staffing specialist follows up for a short chat. Obligation free."
      : "This page is for employers hiring a dedicated teammate - not job seekers, and not a freelancer directory. Tell us the role. A staffing specialist follows up. Obligation free.",
    situationsEyebrow: "If freelance hiring has been the workaround",
    situationsTitle: "You need someone in the business - not another profile to chase.",
    situations: [
      {
        title: "Too much time screening people who are not a fit",
        body: "Job boards and marketplaces leave you reading resumes instead of running the work.",
      },
      {
        title: "Freelancers still need managing",
        body: "Continuity, hours, and follow-through stay on you. You wanted a teammate, not another person to supervise.",
      },
      {
        title: "A local hire feels expensive and slow",
        body: au
          ? "You need dedicated capacity without the delay and employment admin of another local headcount."
          : "You need dedicated capacity without the delay and payroll of another local hire.",
      },
      {
        title: "You still want to choose who joins",
        body: "You do not want an assigned leftover profile. You want to interview and decide.",
      },
    ],
    outcomesEyebrow: "How this is different",
    outcomesTitle: "A dedicated Filipino professional you chose. We handle the employment side.",
    outcomes: [
      {
        title: "Dedicated to your business",
        body: "Full-time or part-time staff who work your hours - not a rotating freelancer pool.",
      },
      {
        title: "You interview. You pick.",
        body: "We source and vet. You meet people on video. Nobody starts until you say yes.",
      },
      {
        title: au ? "Employment admin handled" : "Payroll and HR handled",
        body: au
          ? "Once you hire, we handle onboarding, employment admin, and the time tracker."
          : "Once you hire, we handle onboarding, payroll and HR, and the time tracker.",
      },
      {
        title: "Ongoing account support",
        body: `Serving employers since ${base.sinceYear}. US and Australian offices. Philippines recruitment hub.`,
      },
    ],
    compareTitle: "A staffing company. Not a freelancer directory.",
    compareLead: au
      ? "You still choose the person and direct the work. We take on sourcing, employment administration, and support after they start."
      : "You still choose the person and direct the work. We take on sourcing, payroll and HR, and support after they start.",
    featuredQuoteIndex: LAURA_INDEX >= 0 ? LAURA_INDEX : base.featuredQuoteIndex,
    processLead:
      "The hiring brief is how we match the role. The point is a teammate you keep - not another freelancer to manage.",
    finalTitle: "Hire a teammate you can keep.",
    finalLead: au
      ? "Tell us the role. A specialist will follow up for a short chat - then we recruit if you are aligned."
      : "Tell us the role. A specialist will follow up - then we recruit if you are aligned.",
  };
}

export function challengerCopy(
  concept: ChallengerConcept,
  market: MarketId,
): CapacityChallengerCopy {
  if (concept === "time") return timeChallengerCopy(market);
  if (concept === "teammate") return teammateChallengerCopy(market);
  return capacityChallengerCopy(market);
}
