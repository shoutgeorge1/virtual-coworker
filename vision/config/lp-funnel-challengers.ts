/**
 * Two structurally different paid LPs for duplicate ad groups.
 * Hypothesis copy only - do not treat as a winner until form starts move.
 *
 * Paths are static siblings of /us and /au, not [category]:
 *   /us/offer  /au/offer   form-first (speed)
 *   /us/proof  /au/proof   story-first then form (trust)
 *
 * Live /us and /au stay control. Same conversion machine:
 * GuidedMatchGate contact fields → /api/lead → thank-you?market=&sid= → Calendly.
 * form_start still fires on first name/email/phone focus.
 *
 * Claims below are from virtualcoworker.com homepage / pricing-savings-guide,
 * PUBLIC_QUOTES (success stories), TRUST_PROOF, and Clutch as stored in site.ts.
 * Skipped: hire-in-7-days, 48-hour placement, live $7 starting rates, FBI-grade,
 * country literacy stats, competitor review counts, Glassdoor 4.1 on-page.
 */

import { CATEGORY_SLUGS } from "./categories";
import type { MarketId } from "./markets";
import {
  COMPANY_IDENTITY,
  PUBLIC_QUOTES,
  SITE,
  TRUST_PROOF,
  googleBusinessForMarket,
} from "./site";

export const OFFER_FUNNEL_VARIANT = "offer-direct" as const;
export const PROOF_FUNNEL_VARIANT = "proof-story" as const;

export const OFFER_FUNNEL_PATHS = {
  us: "/us/offer",
  au: "/au/offer",
} as const;

export const PROOF_FUNNEL_PATHS = {
  us: "/us/proof",
  au: "/au/proof",
} as const;

const RESERVED_FUNNEL_SLUGS = ["offer", "proof"] as const;

export function funnelSlugCollidesWithCategory(): boolean {
  return RESERVED_FUNNEL_SLUGS.some((slug) =>
    (CATEGORY_SLUGS as readonly string[]).includes(slug),
  );
}

export type OfferFunnelCopy = {
  market: MarketId;
  variant: typeof OFFER_FUNNEL_VARIANT;
  path: string;
  eyebrow: string;
  h1: string;
  lead: string;
  chips: string[];
  audienceLine: string;
  contactHeading: string;
  howTitle: string;
  howBeats: { k: string; t: string; d: string }[];
  quote: { text: string; by: string };
  hoursLine: string;
  phoneDisplay: string;
  phoneHref: string;
  entity: string;
  nap: string;
  googleLine: string;
  clutchLine: string;
  heroSrc: string;
  heroAlt: string;
  sinceYear: number;
};

export type ProofFunnelCopy = {
  market: MarketId;
  variant: typeof PROOF_FUNNEL_VARIANT;
  path: string;
  eyebrow: string;
  situationKicker: string;
  situation: string;
  booksLine: string;
  quote: { text: string; by: string; company: string };
  supportQuote: { text: string; by: string };
  beatsTitle: string;
  beats: { k: string; t: string; d: string }[];
  formEyebrow: string;
  formTitle: string;
  formLead: string;
  contactHeading: string;
  phoneDisplay: string;
  phoneHref: string;
  entity: string;
  nap: string;
  googleLine: string;
  clutchLine: string;
  heroSrc: string;
  heroAlt: string;
  teamSrc: string;
  teamAlt: string;
  sinceYear: number;
};

function davidQuote() {
  const hit = PUBLIC_QUOTES.find((q) => q.name === "David Boyd");
  return (
    hit ||
    PUBLIC_QUOTES[0]
  );
}

function kyrstinQuote() {
  const hit = PUBLIC_QUOTES.find((q) => q.name === "Kyrstin H.");
  return hit || PUBLIC_QUOTES[0];
}

function sharedMarket(market: MarketId) {
  const au = market === "au";
  const google = googleBusinessForMarket(market);
  return {
    au,
    phoneDisplay: au ? SITE.auPhoneDisplay : SITE.usPhoneDisplay,
    phoneHref: au ? SITE.auPhoneHref : SITE.usPhoneHref,
    googleLine: `${google.rating} Google · ${google.reviewCount} reviews`,
    clutchLine: `${TRUST_PROOF.clutch.rating} Clutch · ${TRUST_PROOF.clutch.reviewCount} reviews`,
    entity: au
      ? `${COMPANY_IDENTITY.entityAu} · ABN ${COMPANY_IDENTITY.abn}`
      : COMPANY_IDENTITY.entityUs,
    nap: au
      ? `AU office · ${SITE.addressAu} · ABN ${COMPANY_IDENTITY.abn}`
      : `US office · ${SITE.addressUs}`,
    sinceYear: TRUST_PROOF.sinceYear,
    admin: au ? "employment admin" : "payroll and HR",
    hours: au ? "Australian business hours" : "US business hours",
  };
}

export function offerFunnelCopy(market: MarketId): OfferFunnelCopy {
  const m = sharedMarket(market);
  const david = davidQuote();
  return {
    market,
    variant: OFFER_FUNNEL_VARIANT,
    path: OFFER_FUNNEL_PATHS[market],
    eyebrow: m.au
      ? "Employers hiring staff · Australian hours"
      : "Employers hiring staff · your hours",
    h1: m.au
      ? "A dedicated Filipino teammate on Australian hours. Start with your details."
      : "A dedicated Filipino VA on your hours. Start with your details.",
    lead: m.au
      ? `We recruit and vet. You interview. We handle ${m.admin}. No recruitment fee to start. Obligation free.`
      : `We recruit and vet. You interview. We handle ${m.admin}. No recruitment fee to start. Obligation free.`,
    chips: [
      `Since ${m.sinceYear}`,
      "20 hours/week minimum",
      "You interview and choose",
    ],
    audienceLine:
      "This page is for employers. Job seekers use the careers link in the footer.",
    contactHeading: "Send your name, company, email, and phone",
    howTitle: "What happens after you send details",
    howBeats: [
      {
        k: "1",
        t: "A specialist follows up",
        d: m.au
          ? "Short chat about the role, hours, and hiring path. Not a contract."
          : "Usually the same business day. Role, hours, and hiring path. Not a contract.",
      },
      {
        k: "2",
        t: "We recruit if you are aligned",
        d: "Philippines team sources and vets against the brief. You conduct a video interview with your chosen candidate.",
      },
      {
        k: "3",
        t: m.au ? "You pick. We handle employment admin." : "You pick. We handle payroll.",
        d: `Once you hire, onboarding, ${m.admin}, and the time tracker stay with us.`,
      },
    ],
    quote: {
      text: david.quote,
      by: `${david.name} · ${david.role}${david.company ? ` · ${david.company}` : ""}`,
    },
    hoursLine: m.au
      ? "We recruit for Australian business hours. Full-time or part-time. 20 hours/week minimum."
      : "We recruit for US business hours. Full-time or part-time. 20 hours/week minimum.",
    phoneDisplay: m.phoneDisplay,
    phoneHref: m.phoneHref,
    entity: m.entity,
    nap: m.nap,
    googleLine: m.googleLine,
    clutchLine: m.clutchLine,
    /* Saved from Google’s ad image CDN copy (simgad/138562541072164392).
       No competitor mark. Not US-office-specific, so AU can share it. */
    heroSrc: "/brand/offer-desk-staff.jpg",
    heroAlt: m.au
      ? "Filipino teammate at a desk with colleagues, for an Australian business"
      : "Filipino teammate at a desk with colleagues, for a US business",
    sinceYear: m.sinceYear,
  };
}

export function proofFunnelCopy(market: MarketId): ProofFunnelCopy {
  const m = sharedMarket(market);
  const david = davidQuote();
  const kyrstin = kyrstinQuote();
  return {
    market,
    variant: PROOF_FUNNEL_VARIANT,
    path: PROOF_FUNNEL_PATHS[market],
    eyebrow: m.au
      ? "Finance and books support · Australian hours"
      : "Finance and books support · US hours",
    situationKicker: "One employer's situation",
    situation:
      "David Boyd hired a VA with a lot of finance experience through Virtual Coworker. He said it was something he should have done a long time ago.",
    booksLine:
      "For teams drowning in books, invoices, and recurring admin - and careful about who sees the numbers.",
    quote: {
      text: david.quote,
      by: `${david.name} · ${david.role}`,
      company: david.company || "",
    },
    supportQuote: {
      text: kyrstin.quote,
      by: `${kyrstin.name} · ${kyrstin.role}${kyrstin.company ? ` · ${kyrstin.company}` : ""}`,
    },
    beatsTitle: "How hiring works",
    beats: [
      {
        k: "01",
        t: "Tell us the role",
        d: "Name, company, email, and phone start a hiring conversation. We turn the role and hours into a brief.",
      },
      {
        k: "02",
        t: "We recruit and vet",
        d: "After you are aligned, the Philippines team sources and screens. You are not left reading a pile of resumes.",
      },
      {
        k: "03",
        t: "You interview. We stay on.",
        d: m.au
          ? `You conduct a video interview with your chosen candidate. Once you hire, we handle onboarding, ${m.admin}, and the time tracker.`
          : `You conduct a video interview with your chosen candidate. Once you hire, we handle onboarding, ${m.admin}, and the time tracker.`,
      },
    ],
    formEyebrow: "Employers only · obligation free",
    formTitle: "When you are ready, send your details.",
    formLead: m.au
      ? "A staffing specialist follows up about the role, hours, and hiring path."
      : "A staffing specialist follows up - usually the same business day.",
    contactHeading: "Where should we send your hiring brief?",
    phoneDisplay: m.phoneDisplay,
    phoneHref: m.phoneHref,
    entity: m.entity,
    nap: m.nap,
    googleLine: m.googleLine,
    clutchLine: m.clutchLine,
    heroSrc: "/guided-match/trust-consult.jpg",
    heroAlt: "Employer and staffing specialist reviewing a Virtual Coworker role brief",
    teamSrc: "/guided-match/trust-team-office.jpg",
    teamAlt: "Recruitment team collaborating in the office",
    sinceYear: m.sinceYear,
  };
}
