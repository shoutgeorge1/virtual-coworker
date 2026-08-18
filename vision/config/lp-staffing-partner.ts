/**
 * US staffing-partner challenger. Preview only.
 *
 * Path: /prototype/staffing-partner/us
 * lp_variant: price_staffing_v1
 *
 * Not live /us. Not an Ads Final URL. Do not invent /us/staffing.
 * Same conversion machine: GuidedMatchGate role → hours → people → size → contact.
 */

import { JOB_SEEKER_LINE, marketLandingCopy } from "./guided-match";
import {
  COMPANY_IDENTITY,
  PUBLIC_QUOTES,
  SITE,
  TRUST_PROOF,
  googleBusinessForMarket,
} from "./site";

export const STAFFING_PARTNER_VARIANT = "price_staffing_v1" as const;
export const STAFFING_PARTNER_PATH = "/prototype/staffing-partner/us" as const;

export type StaffingPartnerRole = { title: string; body: string };
export type StaffingPartnerStep = { k: string; t: string; d: string };
export type StaffingPartnerContrast = {
  option: string;
  body: string;
  highlight?: boolean;
};

export function staffingPartnerCopy() {
  const base = marketLandingCopy("us");
  const google = googleBusinessForMarket("us");
  return {
    market: "us" as const,
    variant: STAFFING_PARTNER_VARIANT,
    path: STAFFING_PARTNER_PATH,
    eyebrow: "Dedicated Filipino Remote Staff",
    // Soft wrap after "/" so mobile does not clip "$7/Hour"
    h1: "Hire Dedicated Filipino Remote Staff From $7/\u200bHour",
    lead: "Virtual Coworker recruits and vets experienced candidates for your role. You interview the shortlist and choose your new team member. Full-time or part-time, working in your time zone.",
    primaryCta: "Tell Us Who You Need",
    proofStrip: [
      `Since ${TRUST_PROOF.sinceYear}`,
      "No Recruitment Fees",
      "20–40 Hours Per Week",
    ] as const,
    howEyebrow: "How it works",
    howTitle: "Tell us the role. Review a vetted shortlist. Interview and select.",
    howLead:
      "A staffing partner model. We recruit. You choose the dedicated Filipino professional who joins your team.",
    steps: [
      {
        k: "1",
        t: "Tell us the role",
        d: "Share the work, hours, and how this team member will support your business.",
      },
      {
        k: "2",
        t: "Review a vetted shortlist",
        d: "We recruit and vet experienced candidates based on the role you need.",
      },
      {
        k: "3",
        t: "Interview and select",
        d: "You interview on video and choose the person who fits. Nobody is assigned without your yes.",
      },
    ] satisfies StaffingPartnerStep[],
    rolesEyebrow: "Common roles",
    rolesTitle: "Dedicated staff for the work your business already needs",
    rolesLead:
      "If you searched for a virtual assistant, you still want a dedicated team member. These are the roles we staff most often.",
    roles: [
      {
        title: "Administration",
        body: "Inbox, calendar, documents, and follow-up owned by one person.",
      },
      {
        title: "Bookkeeping",
        body: "Invoices, reconciliations, and routine reporting.",
      },
      {
        title: "Marketing",
        body: "Content, campaigns, posting, and reporting support.",
      },
      {
        title: "Customer support",
        body: "Tickets, chat, and customer follow-through.",
      },
      {
        title: "Sales support",
        body: "Lists, outreach support, and CRM hygiene.",
      },
      {
        title: "HR / recruiting",
        body: "Sourcing support, scheduling, and people admin.",
      },
    ] satisfies StaffingPartnerRole[],
    contrastEyebrow: "Not a marketplace",
    contrastTitle: "A staffing partner, not a freelance bench",
    contrastLead:
      "You are hiring a dedicated Filipino professional for your business, not browsing a directory or renting an anonymous seat.",
    contrasts: [
      {
        option: "Freelance marketplaces",
        body: "You browse profiles, manage contractors, and own continuity yourself.",
      },
      {
        option: "Job boards",
        body: "You post, screen applicants, and run the hiring process alone.",
      },
      {
        option: "Anonymous call-center seats",
        body: "Rotating agents. No dedicated person who learns your business.",
      },
      {
        option: "Virtual Coworker",
        body: "We recruit and vet. You interview the shortlist. You get a dedicated team member who works your hours.",
        highlight: true,
      },
    ] satisfies StaffingPartnerContrast[],
    proofEyebrow: "Why companies stay",
    proofTitle: "A staffing partner since 2011",
    proofs: [
      {
        title: `Founded in ${TRUST_PROOF.sinceYear}`,
        body: "US office. Philippines recruitment hub. Dedicated Filipino staff for employer businesses.",
      },
      {
        title: "You interview the shortlist",
        body: "We present vetted candidates. You meet them on video and choose who starts.",
      },
      {
        title: "Full-time or part-time",
        body: "Dedicated staff on your time zone. Hours are confirmed before recruiting starts.",
      },
    ],
    googleLine: `${google.rating} Google · ${google.reviewCount} reviews`,
    clutchLine: `${TRUST_PROOF.clutch.rating} Clutch · ${TRUST_PROOF.clutch.reviewCount} reviews`,
    gateEyebrow: "Employers",
    gateTitle: "Tell Us Who You Need",
    gateLead:
      "Answer three quick questions so our staffing team can prepare the right shortlist for your business. It takes about one minute.",
    finalTitle: "Prefer to Talk It Through?",
    finalLead:
      "Call our staffing team to discuss the role, schedule and experience you need.",
    finalPhoneCta: "Call (888) 964-8644",
    phoneDisplay: base.phoneDisplay,
    phoneHref: base.phoneHref,
    adminLabel: base.adminLabel,
    entity: COMPANY_IDENTITY.entityUs,
    nap: `US office · ${SITE.addressUs}`,
    sinceYear: TRUST_PROOF.sinceYear,
    heroSrc: base.heroSrc,
    heroAlt: base.heroAlt,
    teamSrc: base.teamSrc,
    teamAlt: base.teamAlt,
    closerSrc: base.closerSrc,
    closerAlt: base.closerAlt,
    seekerLine: JOB_SEEKER_LINE,
  };
}

export function staffingPartnerQuotes() {
  return PUBLIC_QUOTES.map((q) => ({
    text: q.quote,
    by: `${q.name} · ${q.role}${q.company ? ` · ${q.company}` : ""}`,
  }));
}
