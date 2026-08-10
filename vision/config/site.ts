/**
 * Public trust / legal facts for this Virtual Coworker website.
 * Addresses sourced from published Virtual Coworker contact details (2026-08-05).
 * Quotes sourced from published client stories - rendered as text only (no WP links).
 *
 * IA (George): market surfaces - /us, /au; job seekers exit to PH WordPress careers.
 * Root `/` redirects to `/us` (primary hiring market). No corporate hub.
 * Keep paid employer traffic on this host - only intentional job-seeker egress
 * is virtualcoworker.com.ph (see resolveCareersUrl).
 */

import type { MarketId } from "./markets";

export const SITE = {
  name: "Virtual Coworker",
  legalEntity: "Virtual Coworker Inc.",
  tagline: "Filipino staffing",
  disclaimer: "Hire dedicated Filipino staff for your business.",
  /**
   * Short footer legal lines - paraphrased from our Terms + Privacy
   * (employer microsite). Keep readable; not a wall of text.
   */
  footerLegal: [
    "For businesses hiring staff - not a job board. Job seekers use our Philippines careers site.",
    "A form starts a hiring conversation - not an instant hire or contract. Placement, rates, and terms are confirmed separately.",
    "Site content is general information only - not legal, tax, or employment advice. Results vary by role and business.",
  ] as const,
  /** US site + ads Call (George 2026-08-10 restore: verified 888-964). Prefer resolvePhone("us"). */
  usPhoneDisplay: "(888) 964-8644",
  usPhoneHref: "tel:+18889648644",
  /** AU site + ads Call asset (George-approved 2026-08-08). Prefer resolvePhone("au"). */
  auPhoneDisplay: "1300 886 740",
  auPhoneHref: "tel:+611300886740",
  /** Published street addresses from virtualcoworker.com/contact/ (2026-08). */
  addressUs: "750 N San Vicente Blvd, West Hollywood, CA 90069",
  addressAu: "Level 8/11 York St, Sydney NSW 2000, Australia",
  /**
   * PH street address: not published on virtualcoworker.com/contact/
   * (USA + Australia offices only as of 2026-08-07). Do not invent.
   * Footer still names Philippines recruitment presence for legitimacy.
   */
  addressPh: null as string | null,
  addressPhLabel: "Philippines recruitment hub",
  copyright: "© Virtual Coworker Inc. All Rights Reserved.",
  trademark:
    "Virtual Coworker® and related marks are trademarks of Virtual Coworker Inc. and its affiliates.",
} as const;

/**
 * Verifiable company identity for the footer - the stuff Google and cautious
 * buyers look for (NAP, registered entities, a named human).
 *
 * Every value below is evidenced in this repo or on published Virtual Coworker
 * pages: the AU entity + ABN come from our own privacy page, the founder name
 * from the About page and the Forbes Business Council profile title.
 * Rendered as plain text - no outbound profile links (George, 2026-08-07).
 */
export const COMPANY_IDENTITY = {
  entityUs: "Virtual Coworker Inc.",
  entityAu: "Virtual Coworker Pty. Ltd.",
  abn: "49 154 746 004",
  founderName: "Braden Yuill",
  founderTitle: "Founder & CEO",
} as const;

/**
 * Public directory / recognition proof.
 *
 * The `href` values are PROVENANCE ONLY - they record where each claim can be
 * verified and are deliberately **not rendered anywhere on the site**. George's
 * rule (2026-08-07): trust marks never link out, so paid visitors are not handed
 * off to Clutch, Forbes or Google. Do not wire these into an `<a>`.
 *
 * Clutch rating from the Clutch company profile (4.9 · 7 reviews).
 * Forbes: Braden Yuill Business Council profile.
 * Google Maps: published US office pin (provenance href only - not rendered).
 * Google Business Profile ratings (George 2026-08-09): US West Hollywood 5.0 / 39;
 *   AU Sydney 4.8 / 23. Stars + count only - do not swap site phones from GBP.
 * Trustpilot: live profile 2026-08-09 - 4.3 / 5 · 7 reviews (Google snippet 4.7/26 was stale).
 * Glassdoor: George live look 2026-08-09 - 4.1 / 5 · 87% would recommend · 24 reviews.
 *   On-page (2026-08-09): show recommend % + review count only - do NOT print 4.1.
 *   (OA’s page also prints a Glassdoor 4.3 - that is Glassdoor’s figure on OA, not OA’s score).
 * Outsource Accelerator: Featured In logo only - do not print “OA 4.3”.
 */
export const TRUST_PROOF = {
  clutch: {
    href: "https://clutch.co/profile/virtual-coworker",
    rating: "4.9",
    reviewCount: 7,
    label: "Clutch",
  },
  forbes: {
    href: "https://councils.forbes.com/profile/Braden-Yuill-Founder-CEO-Virtual-Coworker/b9fd9e7b-bb15-42df-9144-aa19ff54bfee",
    label: "Forbes Business Council",
  },
  googleMapsUs: {
    href: "https://goo.gl/maps/rZikUJ86PppBwULK9",
    label: "Google Maps - West Hollywood office",
  },
  /** GBP West Hollywood. Site phone stays (888) 964-8644 - not the Maps listing. */
  googleBusinessUs: {
    rating: "5.0",
    reviewCount: 39,
    label: "Google",
    sublabel: "39 reviews",
    place: "West Hollywood",
  },
  /** GBP Sydney. Listing / site phone stays 1300 886 740. */
  googleBusinessAu: {
    rating: "4.8",
    reviewCount: 23,
    label: "Google",
    sublabel: "23 reviews",
    place: "Sydney",
  },
  trustpilot: {
    href: "https://www.trustpilot.com/review/virtualcoworker.com",
    rating: "4.3",
    reviewCount: 7,
    label: "Trustpilot",
  },
  glassdoor: {
    rating: "4.1",
    recommendPct: 87,
    reviewCount: 24,
    label: "Glassdoor",
  },
  outsourceAccelerator: {
    href: "https://www.outsourceaccelerator.com/company/virtual-coworker/",
    label: "Outsource Accelerator",
    note: "Listed · Directory",
  },
  sinceYear: 2011,
} as const;

export type GoogleBusinessProof = {
  rating: string;
  reviewCount: number;
  label: "Google";
  sublabel: string;
  place: string;
};

export function googleBusinessForMarket(market: MarketId): GoogleBusinessProof {
  return market === "au" ? TRUST_PROOF.googleBusinessAu : TRUST_PROOF.googleBusinessUs;
}

/** Trading years - the strongest honest number this business owns. */
export function yearsTrading(now: Date = new Date()): number {
  return now.getFullYear() - TRUST_PROOF.sinceYear;
}

/**
 * Headline legitimacy figures for the animated counter row.
 * Every value is either arithmetic on the founding year or a published figure -
 * nothing estimated. `suffix`/`prefix` keep the counter animation numeric.
 */
export type ProofFigure = {
  id: string;
  value: number;
  prefix?: string;
  suffix?: string;
  /** Decimal places to animate to. */
  decimals?: number;
  label: string;
  note: string;
};

export function proofFigures(now: Date = new Date()): ProofFigure[] {
  return [
    {
      id: "years",
      value: yearsTrading(now),
      suffix: "+",
      label: "Years placing Filipino staff",
      note: `Trading since ${TRUST_PROOF.sinceYear}`,
    },
    {
      id: "rating",
      value: Number(TRUST_PROOF.clutch.rating),
      decimals: 1,
      suffix: "/5",
      label: "Clutch profile rating",
      note: `${TRUST_PROOF.clutch.reviewCount} public reviews`,
    },
    {
      id: "offices",
      value: 3,
      label: "Offices across 3 countries",
      note: "West Hollywood · Sydney · Philippines",
    },
  ];
}

/**
 * Short client quotes - text only; do not link out.
 * Sourced from the published Virtual Coworker Success Stories page
 * (virtualcoworker.com/success-stories, captured in raw/success.html).
 *
 * Roster rule (George, 2026-08-07): prefer fewer strong, still-trading businesses
 * over a long list of no-name or dead brands. Every company below was checked to
 * still resolve as a live business site. Do NOT add Fortune 500 or unverified marks.
 * Dropped from the old roster: GiggedIn (domain sold - now an unrelated site),
 * My Nappies and Allara Support Services (domains no longer resolve).
 */
export type PublicQuote = {
  quote: string;
  name: string;
  role: string;
  company?: string;
  /** Exact phrases to bold in the quote. */
  pop?: readonly string[];
  /** One word to display extra-large (e.g. “loads”). */
  boom?: string;
};

export type PublicQuoteWithLogo = PublicQuote & {
  /** Client logo, where the company publishes one we can legitimately show. */
  logo?: string;
  logoAlt?: string;
};

export const PUBLIC_QUOTES: readonly PublicQuoteWithLogo[] = [
  {
    quote:
      "They’ve exceeded our expectations! The recruiting process was well organized, and I feel we were matched very well.",
    pop: ["exceeded our expectations"],
    name: "Kyrstin H.",
    role: "General Manager",
    company: "College Hunks",
  },
  {
    quote:
      "I’m beyond happy with the candidate hired for the role I needed to fill! Everyone I’ve dealt with has been professional and polished.",
    pop: ["I’m beyond happy"],
    name: "Laura W.",
    role: "Founder",
    company: "Good Co.",
  },
  {
    quote:
      "They found me an awesome VA with loads of work experience in finance. Honestly, it’s something I should have done a long time ago!",
    pop: ["awesome VA", "I should have done a long time ago"],
    boom: "loads",
    name: "David Boyd",
    role: "Director",
    company: "Credit Card Compare",
  },
  {
    quote:
      "I have worked with a number of virtual staff services. The team at Virtual Coworker have provided me with the best value to date.",
    pop: ["best value to date"],
    name: "Logan Merrick",
    role: "Strategic Director",
    company: "Buzinga Apps",
  },
];

/**
 * Client marks for the "companies that hired through us" strip.
 *
 * Image-backed only. US-native marks on /us; AU success-story brands on /au
 * and also on /us when we need a fuller strip (George 2026-08-07).
 * Nothing links out.
 */
export type ClientMark = {
  id: string;
  name: string;
  /** Required - strip only shows image-backed marks. */
  src: string;
  alt?: string;
  /**
   * Visible label under/beside the mark. Use for icon-only logos that don’t
   * spell the company name (e.g. The Learning Deli box + teardrop).
   */
  caption?: string;
  /** Markets where this mark should appear. */
  markets: readonly ("us" | "au")[];
};

export const CLIENT_MARKS: readonly ClientMark[] = [
  {
    // Laura W. / GOODco. - Charleston, SC (US). Logo published on virtualcoworker.com/forbes/.
    id: "good-co",
    name: "Good Co.",
    src: "/brand/trust/client-good-co.png",
    alt: "Good Co.",
    markets: ["us"],
  },
  {
    id: "credit-card-compare",
    name: "Credit Card Compare",
    src: "/brand/trust/client-credit-card-compare.png",
    alt: "Credit Card Compare",
    // AU success story - also on /us until more US marks land (George 2026-08-09).
    markets: ["au", "us"],
  },
  {
    id: "buzinga",
    name: "Buzinga Apps",
    src: "/brand/trust/client-buzinga.png",
    alt: "Buzinga Apps",
    markets: ["au", "us"],
  },
  {
    // David Krynauw / ProActive Media - Success Stories; logo George saved 2026-08-07.
    id: "proactive-media",
    name: "ProActive Media",
    src: "/brand/trust/client-proactive-media.png",
    alt: "ProActive Media",
    markets: ["au", "us"],
  },
  {
    id: "learning-deli",
    name: "The Learning Deli",
    src: "/brand/trust/client-learning-deli.png",
    alt: "The Learning Deli",
    // Icon-only (cube in yellow teardrop) - caption so the strip isn’t nameless.
    caption: "The Learning Deli",
    markets: ["au", "us"],
  },
  {
    // Paul Slezak / RecruitLoop - Success Stories; AU-origin, global ops.
    id: "recruitloop",
    name: "RecruitLoop",
    src: "/brand/trust/client-recruitloop.png",
    alt: "RecruitLoop",
    markets: ["au", "us"],
  },
];

/**
 * Form cue - point at the gate, don’t fake a countdown.
 * George (2026-08-09): ribbon scarcity read cheap; pointer + specialist CTA is honest.
 */
export const FORM_CUE = {
  us: {
    label: "Start here",
    body: "Talk to a specialist - usually same business day.",
  },
  au: {
    label: "Start here",
    body: "Have a chat - obligation free, no lock-in.",
  },
} as const;

/**
 * US media / client-logo wishlist - NOT live until verified assets land.
 * Tracked on Launch Control checklist + TRUST-PROOF.md.
 */
export const TRUST_ASSET_WISHLIST = [
  "US-recognizable press logos (Inc, Entrepreneur, Business Insider, local biz press) - only if VC was actually featured",
  "Authorized client logos from active US accounts (written OK from VC / client)",
  "Video testimonials with face + name + company + outcome",
  "Any Fortune-level marks only with explicit authorization - never invent",
] as const;

export function clientMarksForMarket(market: "us" | "au"): readonly ClientMark[] {
  return CLIENT_MARKS.filter((c) => c.markets.includes(market));
}

/**
 * Press + awards actually claimed on virtualcoworker.com ("Featured In:").
 * Artwork mirrored into /public/brand/trust from the company's own media library.
 * Display-only - no outbound links (George: keep visitors on this host).
 */
export type PressMark = {
  id: string;
  src: string;
  alt: string;
  /** Short caption under the mark. */
  note: string;
  /** Wider marks get more grid room. */
  wide?: boolean;
  /** Markets where this mark should appear. Default: both. */
  markets?: readonly ("us" | "au")[];
};

export const PRESS_MARKS: readonly PressMark[] = [
  {
    // Braden Yuill - Forbes Business Council (only US-recognizable press we can verify).
    id: "forbes",
    src: "/brand/badge-forbes-navy.webp",
    alt: "Forbes Business Council",
    note: "Recognition",
    wide: true,
    markets: ["us", "au"],
  },
  {
    id: "clutch-us",
    src: "/brand/trust/badge-clutch-us-2024.webp",
    alt: "Clutch top virtual assistant company - United States 2024",
    note: "Award",
    markets: ["us", "au"],
  },
  {
    id: "google",
    src: "/brand/badge-google-5star.webp",
    alt: "Google Reviews",
    note: "Reviews",
    markets: ["us", "au"],
  },
  {
    id: "anthill",
    src: "/brand/trust/press-anthill.svg",
    alt: "Anthill Cool Company Awards - Top 100",
    note: "Award",
    markets: ["us", "au"],
  },
  {
    // Logo only in Featured In (George 2026-08-09) - no separate Reviews card.
    // Rating lives in TRUST_PROOF / docs; not printed under the mark.
    id: "trustpilot",
    src: "/brand/trust/press-trustpilot.svg",
    alt: "Trustpilot",
    note: "Reviews",
    wide: true,
    markets: ["us"],
  },
  {
    // Official VC “Featured In” row. SMH is AU-only - not a US press mark.
    id: "smh",
    src: "/brand/trust/press-smh.webp",
    alt: "The Sydney Morning Herald",
    note: "Press",
    wide: true,
    markets: ["au"],
  },
  {
    // Official Startup Daily wordmark paths, recolored navy for the white strip.
    id: "startupdaily",
    src: "/brand/trust/press-startupdaily.svg",
    alt: "Startup Daily",
    note: "Press",
    wide: true,
    markets: ["us", "au"],
  },
  {
    id: "startupsmart",
    src: "/brand/trust/press-startup.svg",
    alt: "StartupSmart",
    note: "Press",
    wide: true,
    markets: ["us", "au"],
  },
  {
    id: "brw",
    src: "/brand/trust/press-brw.svg",
    alt: "BRW",
    note: "Press",
    wide: true,
    markets: ["us", "au"],
  },
  {
    // Industry directory - logo in Featured In (George 2026-08-09). US home pack.
    id: "outsource-accelerator",
    src: "/brand/trust/press-outsource-accelerator.svg",
    alt: "Outsource Accelerator",
    note: "Directory",
    wide: true,
    markets: ["us"],
  },
  {
    // Platform directory presence - Featured In wordmark, not a social box.
    id: "zoho",
    src: "/brand/trust/press-zoho.svg",
    alt: "Zoho",
    note: "Directory",
    wide: true,
    markets: ["us"],
  },
];

export function pressMarksForMarket(market: "us" | "au"): readonly PressMark[] {
  return PRESS_MARKS.filter((p) => !p.markets || p.markets.includes(market));
}

export type FooterSocialMark = {
  id: string;
  src: string;
  name: string;
};

/**
 * Footer social / directory boxes - display only. No href field on purpose.
 * George 2026-08-09: LinkedIn, Indeed, Facebook, Instagram, ZipRecruiter, Glassdoor
 * at the bottom - grayed logos only so they read as non-clickable.
 * Glassdoor recommend % stays in TRUST_PROOF / docs (not on-page caption).
 * Provenance (TRUST-PROOF.md only, never rendered):
 *   linkedin.com/company/virtualcoworker
 *   facebook.com/virtualcoworkerinc
 *   instagram.com/virtualcoworker
 */
export const FOOTER_SOCIAL_MARKS: readonly FooterSocialMark[] = [
  { id: "linkedin", src: "/brand/trust/dir-linkedin.svg", name: "LinkedIn" },
  { id: "indeed", src: "/brand/trust/dir-indeed.svg", name: "Indeed" },
  { id: "facebook", src: "/brand/trust/dir-facebook.svg", name: "Facebook" },
  { id: "instagram", src: "/brand/trust/dir-instagram.svg", name: "Instagram" },
  { id: "ziprecruiter", src: "/brand/trust/dir-ziprecruiter.svg", name: "ZipRecruiter" },
  { id: "glassdoor", src: "/brand/trust/dir-glassdoor.svg", name: "Glassdoor" },
];

/**
 * Industry pain→gain stats - primary published sources only.
 * Numbers checked against Deloitte GOS 2024 PDF, Stanford/Nature 2024, BLS OOH May 2024.
 */
export type IndustryStat = {
  id: string;
  /** Big number / short figure shown in the card. */
  figure: string;
  /** Human pain/gain headline. */
  headline: string;
  body: string;
  sourceLabel: string;
  sourceHref?: string;
  /** When set, only render on that market. */
  markets?: readonly MarketId[];
};

export const INDUSTRY_STATS: readonly IndustryStat[] = [
  {
    id: "deloitte-talent",
    figure: "42%",
    headline: "of companies hire offshore for better people",
    body: "That’s now the #1 reason they outsource - ahead of chasing the lowest price.",
    sourceLabel: "Deloitte Global Outsourcing Survey 2024",
  },
  {
    id: "deloitte-invest",
    figure: "80%",
    headline: "plan to keep spending on outsourcing",
    body: "Four in five companies will spend the same or more next year. This isn’t a fad.",
    sourceLabel: "Deloitte Global Outsourcing Survey 2024",
  },
  {
    id: "stanford-retention",
    figure: "33%",
    headline: "fewer people quit with flexible work",
    body: "A Stanford study cut resignations by a third. Performance still held up.",
    sourceLabel: "Bloom, Han & Liang, Nature 2024",
  },
  {
    id: "ph-admin-va-rate",
    figure: "~$8",
    headline: "an hour for a typical admin VA",
    body: "Serious capacity without US payroll weight. That’s the rate that changes the math.",
    sourceLabel: "Industry VA rate guides, 2025–26",
    markets: ["us"],
  },
  {
    id: "deloitte-front-office",
    figure: "50%",
    headline: "also send sales and marketing overseas",
    body: "Half of companies offshore sales, marketing, or product work - not only back-office.",
    sourceLabel: "Deloitte Global Outsourcing Survey 2024",
    markets: ["au"],
  },
];

export function industryStatsForMarket(market: MarketId): IndustryStat[] {
  return INDUSTRY_STATS.filter(
    (s) => !s.markets || s.markets.includes(market),
  );
}

export type SiteSurface = MarketId | "ph";

export type NavId = "services" | "how" | "hire" | "apply";

export type NavItem = {
  href: string;
  label: string;
  id: NavId;
  primary?: boolean;
};

/** Market-scoped primary nav - never US · AU · Careers as peer equals. */
export function navForSurface(surface: SiteSurface): NavItem[] {
  if (surface === "ph") {
    return [
      { href: "/ph", label: "Careers", id: "services" },
      { href: "/ph/apply", label: "Apply", id: "apply", primary: true },
    ];
  }
  const home = surface === "au" ? "/au" : "/us";
  const q = `?market=${surface}`;
  return [
    { href: `/services${q}`, label: "Services", id: "services" },
    { href: `/how-it-works${q}`, label: "How it works", id: "how" },
    {
      href: `${home}#gate`,
      label: surface === "au" ? "Have a chat" : "Start Hiring",
      id: "hire",
      primary: true,
    },
  ];
}

export function homeForSurface(surface: SiteSurface): string {
  if (surface === "ph") return "/ph";
  if (surface === "au") return "/au";
  return "/us";
}
