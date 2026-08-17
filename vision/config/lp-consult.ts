/**
 * Consult-truth employer LP. Cheyenne Gichana (US) + Holly Wallace (APAC).
 * Sibling of /us and /au. Not the Ads control. Same conversion machine:
 * GuidedMatchGate role → hours → people → contact → /api/lead → thank-you.
 *
 * Claims from their call notes + existing TRUST_PROOF / PUBLIC_QUOTES.
 * Holly folded in here (no extra URL): security is the frequent objection;
 * part-time / 20h min lands; recruit the specific role, not a generic VA;
 * reframe off cheap labor. AU copy can name AU/NZ industry experience.
 * Refused: live $7 starting rate, invented timelines, fake review counts,
 * Fortune 500, candidate cards, a standalone security landing page.
 */

import type { MarketId } from "./markets";
import {
  COMPANY_IDENTITY,
  PUBLIC_QUOTES,
  SITE,
  TRUST_PROOF,
  googleBusinessForMarket,
} from "./site";
import { GUIDED_MATCH_HOURS_MINIMUM_NOTE } from "./guided-match";
import { CATEGORY_SLUGS } from "./categories";

export const CONSULT_VARIANT = "consult-truth" as const;

export const CONSULT_PATHS = {
  us: "/us/consult",
  au: "/au/consult",
} as const;

export function consultSlugCollidesWithCategory(): boolean {
  return (CATEGORY_SLUGS as readonly string[]).includes("consult");
}

export type ConsultCopy = {
  market: MarketId;
  variant: typeof CONSULT_VARIANT;
  path: string;
  h1: string;
  lead: string;
  primaryCta: string;
  painsTitle: string;
  pains: { t: string; d: string }[];
  enquireTitle: string;
  enquireLead: string;
  enquire: { t: string; d: string }[];
  howTitle: string;
  howLead: string;
  steps: { k: string; t: string; d: string }[];
  valueTitle: string;
  values: { t: string; d: string }[];
  mixTitle: string;
  mixLead: string;
  mixups: { t: string; d: string }[];
  storiesTitle: string;
  gateTitle: string;
  gateLead: string;
  finalTitle: string;
  finalLead: string;
  hoursMinimum: string;
  phoneDisplay: string;
  phoneHref: string;
  entity: string;
  nap: string;
  googleLine: string;
  clutchLine: string;
  heroSrc: string;
  heroAlt: string;
  closerSrc: string;
  closerAlt: string;
  sceneSrc: string;
  sceneAlt: string;
  sinceYear: number;
  linkedin: string;
};

function quotes() {
  return PUBLIC_QUOTES.map((q) => ({
    text: q.quote,
    by: `${q.name} · ${q.role} · ${q.company}`,
  }));
}

export function consultQuotes() {
  return quotes();
}

export function consultCopy(market: MarketId): ConsultCopy {
  const au = market === "au";
  const google = googleBusinessForMarket(market);
  const hours = au ? "Australian business hours" : "US business hours";
  const admin = au ? "employment admin" : "payroll and HR";

  return {
    market,
    variant: CONSULT_VARIANT,
    path: CONSULT_PATHS[market],
    h1: "Your team is maxed. Hire dedicated staff who can learn your systems.",
    lead: au
      ? "The team is maxed and you need someone to take the work, not another person to chase. Nervous about systems, passwords, and sensitive data? We recruit for Australian business hours and the actual role. You interview. 20 hours/week minimum. We stay."
      : "The team is maxed and you need someone to take the work, not another person to chase. Nervous about systems, passwords, and sensitive data? We recruit for your hours and the actual role. You interview. 20 hours/week minimum. We stay.",
    primaryCta: "Tell us the role",
    painsTitle: "What owners say on the call",
    pains: [
      {
        t: "The team is at capacity",
        d: "Repetitive admin is drowning the owner or the floor. Filing, scheduling, inbox, billing. Lead influx or order volume the internal team cannot absorb. You need a person who owns the work without constant oversight or chasing.",
      },
      {
        t: "Systems, passwords, and sensitive data",
        d: "Giving offshore staff access to email, passwords, banking, or client files is the objection we hear most. Healthcare and finance especially. You stay in control of access. We walk through how before anyone logs in.",
      },
      {
        t: "First time hiring offshore",
        d: "Never hired this way, or burned by a VA or freelancer who left. Nervous about quality, reliability, communication, and whether they will actually integrate into the team. Worried the next person will churn.",
      },
      au
        ? {
            t: "AU and NZ industry experience",
            d: "Real estate, construction, project administration, healthcare, and bookkeeping. Clients want people who already know how work is done here, not a generic admin hire.",
          }
        : {
            t: "Your tools are not generic",
            d: "ERP, CRM, Simple Practice, Klaviyo, or a custom workflow. You need someone who can learn the stack without months of hand-holding.",
          },
    ],
    enquireTitle: "Why people get in touch",
    enquireLead:
      "Most owners are not browsing. They already have a reason, then they want the mix-ups cleared.",
    enquire: [
      {
        t: "Someone they trust already did it",
        d: "A peer on Reddit, a contractor, or another owner with direct experience. They want the same kind of hire, not a guess.",
      },
      {
        t: "They want the role, not a generic VA",
        d: "They searched for an offshore assistant or Virtual Coworker. They need a targeted hire for the actual work, not one person expected to do admin, bookkeeping, social, and lead gen.",
      },
      {
        t: "A colleague already uses offshore staff",
        d: "Someone in their circle is already doing this. They want to see if the same model fits their hours and tools.",
      },
    ],
    howTitle: "How hiring works",
    howLead: `Tell us the role. We filter so you only review people who fit. We recruit after you are aligned. You interview. We handle ${admin}.`,
    steps: [
      {
        k: "1",
        t: "You tell us",
        d: "Role, hours, and how many people. We help write the job description from the call, or start from a sample JD.",
      },
      {
        k: "2",
        t: "We scope",
        d: "A staffing specialist reviews the actual role so you are not hiring one person for five jobs. Then we send a hiring brief.",
      },
      {
        k: "3",
        t: "We recruit",
        d: "Philippines team sources and vets after you are aligned. We filter the pile so you review suitable people. You conduct a video interview with your chosen candidate.",
      },
      {
        k: "4",
        t: "We stay",
        d: `You choose who starts. Dedicated account manager and check-ins in ramp-up. We handle onboarding, ${admin}, and the time tracker.`,
      },
    ],
    valueTitle: "What usually settles it",
    values: [
      {
        t: "Reliability and trust",
        d: "Price matters. Trust is why people hire. Dedicated staff, not a rotating freelancer. Payroll stability so people stay. 13-month performance reviews.",
      },
      {
        t: "Start part-time",
        d: `${GUIDED_MATCH_HOURS_MINIMUM_NOTE} Consistent support without jumping to a full-time hire. Scale hours up as the business grows.`,
      },
      {
        t: "Hire the role, not a generic VA",
        d: au
          ? "We recruit for the job you actually need. Rates are role-specific. Specialized experience and AU or NZ industry knowledge are priced in."
          : "We recruit for the job you actually need. Rates are role-specific. Admin, bookkeeping, customer service, social, and lead generation are different hires.",
      },
      {
        t: "Fast turnaround",
        d: "Profiles in 3-5 days. About 1.5-2 weeks from the need to the first day, once you are aligned.",
      },
      {
        t: "Buy back the week",
        d: `Get out of the day-to-day weeds. We staff for ${hours}. Dedicated people on your clock, not leftover overnight coverage.`,
      },
      {
        t: "You interview. We stay.",
        d: `You meet the shortlist and make the hiring choice. Help writing the job description. Dedicated account manager in ramp-up. Serving employers since ${TRUST_PROOF.sinceYear}.`,
      },
    ],
    mixTitle: "Mix-ups we clear on the call",
    mixLead:
      "These come up every week. Better to say them here than un-teach them later.",
    mixups: [
      {
        t: "I saw $7/hour on the website",
        d: au
          ? "That is not a rate we quote here. This is not cheap labor. Rates follow skill, responsibility, and the role. AU and NZ industry knowledge is priced in."
          : "That is not a rate we quote here. This is not cheap labor. Rates follow skill, responsibility, and the role. An appointment setter, a bookkeeper, and a medical biller are not the same price.",
      },
      {
        t: "A VA can do everything",
        d: "Generalists exist. Specialists land the work. Appointment setter, bookkeeper, social, medical billing, and inbox admin are different jobs. We help you pick a plan instead of hiring a blur.",
      },
      {
        t: "Who trains whom",
        d: "We source and onboard. Setup, systems verification, English fluency. You train on product, process, tools, and culture. Plan on 1-2 weeks of training load from your side. First-timers should expect that.",
      },
      {
        t: "How do they get into my systems safely?",
        d: "You do not share one login and hope. Individual logins, MFA, a password manager, restricted access, NDAs, and endpoint security. We talk through the practical steps on the call. You keep control of the accounts.",
      },
    ],
    storiesTitle: "What employers say",
    gateTitle: "Tell us the role",
    gateLead: au
      ? "A member of our team will follow up. Obligation free. Role, hours, then your details."
      : "A member of our team will follow up. Obligation free. Role, hours, then your details.",
    finalTitle: "Ready to hire?",
    finalLead:
      "Tell us the role. We will build the hiring brief and walk you through recruiting.",
    hoursMinimum: GUIDED_MATCH_HOURS_MINIMUM_NOTE,
    phoneDisplay: au ? SITE.auPhoneDisplay : SITE.usPhoneDisplay,
    phoneHref: au ? SITE.auPhoneHref : SITE.usPhoneHref,
    entity: au
      ? `${COMPANY_IDENTITY.entityAu} · ABN ${COMPANY_IDENTITY.abn}`
      : COMPANY_IDENTITY.entityUs,
    nap: au
      ? `AU office · ${SITE.addressAu} · ABN ${COMPANY_IDENTITY.abn}`
      : `US office · ${SITE.addressUs}`,
    googleLine: `${google.rating} Google · ${google.reviewCount} reviews`,
    clutchLine: `${TRUST_PROOF.clutch.rating} Clutch · ${TRUST_PROOF.clutch.reviewCount} reviews`,
    heroSrc: au ? "/brand/va-au.jpg" : "/brand/va-us.jpg",
    heroAlt: au
      ? "Filipino teammate at work for an Australian business"
      : "Filipino teammate at work for a US business",
    closerSrc: au ? "/brand/hero-au-2026.jpg" : "/brand/hero-us-2026.jpg",
    closerAlt: "Virtual Coworker office photograph",
    sceneSrc: "/guided-match/trust-consult.jpg",
    sceneAlt: "Virtual Coworker consult in the office",
    sinceYear: TRUST_PROOF.sinceYear,
    linkedin: "450K+",
  };
}
