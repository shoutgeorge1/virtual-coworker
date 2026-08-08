/**
 * Public trust / legal facts for this Virtual Coworker website.
 * Addresses sourced from published Virtual Coworker contact details (2026-08-05).
 * Quotes sourced from published client stories — rendered as text only (no WP links).
 *
 * IA (George): market surfaces — /us, /au; job seekers exit to PH WordPress careers.
 * Root `/` redirects to `/us` (primary hiring market). No corporate hub.
 * Keep paid employer traffic on this host — only intentional job-seeker egress
 * is virtualcoworker.com.ph (see resolveCareersUrl).
 */

import type { MarketId } from "./markets";

export const SITE = {
  name: "Virtual Coworker",
  legalEntity: "Virtual Coworker Inc.",
  tagline: "Filipino staffing",
  disclaimer: "Hire dedicated Filipino staff for your business.",
  /**
   * Short footer legal lines — paraphrased from our Terms + Privacy
   * (employer microsite). Keep readable; not a wall of text.
   */
  footerLegal: [
    "For businesses hiring staff — not a job board. Job seekers use our Philippines careers site.",
    "A form starts a hiring conversation — not an instant hire or contract. Placement, rates, and terms are confirmed separately.",
    "Site content is general information only — not legal, tax, or employment advice. Results vary by role and business.",
  ] as const,
  /** US site + ads Call asset (aligned 2026-08-07). */
  usPhoneDisplay: "(888) 954-8644",
  usPhoneHref: "tel:8889548644",
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
 * Verifiable company identity for the footer — the stuff Google and cautious
 * buyers look for (NAP, registered entities, a named human).
 *
 * Every value below is evidenced in this repo or on published Virtual Coworker
 * pages: the AU entity + ABN come from our own privacy page, the founder name
 * from the About page and the Forbes Business Council profile title.
 * Rendered as plain text — no outbound profile links (George, 2026-08-07).
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
 * The `href` values are PROVENANCE ONLY — they record where each claim can be
 * verified and are deliberately **not rendered anywhere on the site**. George's
 * rule (2026-08-07): trust marks never link out, so paid visitors are not handed
 * off to Clutch, Forbes or Google. Do not wire these into an `<a>`.
 *
 * Clutch rating from the Clutch company profile (4.9 · 7 reviews).
 * Forbes: Braden Yuill Business Council profile.
 * Google Maps: published US office pin (badge artwork only — no invented count).
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
    label: "Google Maps — West Hollywood office",
  },
  sinceYear: 2011,
} as const;

/** Trading years — the strongest honest number this business owns. */
export function yearsTrading(now: Date = new Date()): number {
  return now.getFullYear() - TRUST_PROOF.sinceYear;
}

/**
 * Headline legitimacy figures for the animated counter row.
 * Every value is either arithmetic on the founding year or a published figure —
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
 * Short client quotes — text only; do not link out.
 * Sourced from the published Virtual Coworker Success Stories page
 * (virtualcoworker.com/success-stories, captured in raw/success.html).
 *
 * Roster rule (George, 2026-08-07): prefer fewer strong, still-trading businesses
 * over a long list of no-name or dead brands. Every company below was checked to
 * still resolve as a live business site. Do NOT add Fortune 500 or unverified marks.
 * Dropped from the old roster: GiggedIn (domain sold — now an unrelated site),
 * My Nappies and Allara Support Services (domains no longer resolve).
 */
export type PublicQuote = {
  quote: string;
  name: string;
  role: string;
  company?: string;
};

export type PublicQuoteWithLogo = PublicQuote & {
  /** Client logo, where the company publishes one we can legitimately show. */
  logo?: string;
  logoAlt?: string;
};

export const PUBLIC_QUOTES: readonly PublicQuoteWithLogo[] = [
  {
    quote:
      "They’ve exceeded our expectations. The recruiting process was well organized, and I feel we were matched very well.",
    name: "Kyrstin H.",
    role: "General Manager",
    company: "College Hunks",
  },
  {
    quote:
      "I’m beyond happy with the candidate hired for the role I needed to fill. Everyone I’ve dealt with has been professional and polished.",
    name: "Laura W.",
    role: "Founder",
    company: "Good Co.",
  },
  {
    quote:
      "They found me an awesome VA with loads of work experience in finance. Honestly, it’s something I should have done a long time ago.",
    name: "David Boyd",
    role: "Director",
    company: "Credit Card Compare",
  },
  {
    quote:
      "I have worked with a number of virtual staff services. The team at Virtual Coworker have provided me with the best value to date.",
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
  /** Required — strip only shows image-backed marks. */
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
    // Laura W. / GOODco. — Charleston, SC (US). Logo published on virtualcoworker.com/forbes/.
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
    // AU success story — also shown on /us to fill the US strip.
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
    id: "learning-deli",
    name: "The Learning Deli",
    src: "/brand/trust/client-learning-deli.png",
    alt: "The Learning Deli",
    // Icon-only (cube in yellow teardrop) — caption so the strip isn’t nameless.
    caption: "The Learning Deli",
    markets: ["au", "us"],
  },
  {
    // Paul Slezak / RecruitLoop — Success Stories; AU-origin, global ops.
    id: "recruitloop",
    name: "RecruitLoop",
    src: "/brand/trust/client-recruitloop.png",
    alt: "RecruitLoop",
    markets: ["au", "us"],
  },
];

export function clientMarksForMarket(market: "us" | "au"): readonly ClientMark[] {
  return CLIENT_MARKS.filter((c) => c.markets.includes(market));
}

/**
 * Press + awards actually claimed on virtualcoworker.com ("Featured In:").
 * Artwork mirrored into /public/brand/trust from the company's own media library.
 * Display-only — no outbound links (George: keep visitors on this host).
 */
export type PressMark = {
  id: string;
  src: string;
  alt: string;
  /** Short caption under the mark. */
  note: string;
  /** Wider marks get more grid room. */
  wide?: boolean;
};

export const PRESS_MARKS: readonly PressMark[] = [
  {
    // Rebuilt crisp navy lockup (VC Featured In mark) — not the crushed 3× webp upscale.
    id: "smh",
    src: "/brand/trust/press-smh.webp",
    alt: "The Sydney Morning Herald",
    note: "Press",
    wide: true,
  },
  {
    id: "brw",
    src: "/brand/trust/press-brw.svg",
    alt: "BRW",
    note: "Press",
    wide: true,
  },
  {
    // Official Startup Daily wordmark paths, recolored navy for the white strip.
    id: "startupdaily",
    src: "/brand/trust/press-startupdaily.svg",
    alt: "Startup Daily",
    note: "Press",
    wide: true,
  },
  {
    id: "startupsmart",
    src: "/brand/trust/press-startup.svg",
    alt: "StartupSmart",
    note: "Press",
    wide: true,
  },
  {
    id: "anthill",
    src: "/brand/trust/press-anthill.svg",
    alt: "Anthill Cool Company Awards — Top 100",
    note: "Award",
  },
  // Dropped StartupSmart Awards 2014 — dated / mushy raster on the strip.
];

/**
 * Industry pain→gain stats — primary published sources only.
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
    headline: "It’s about people, not price",
    body: "Finding good people is now the #1 reason companies hire offshore — not chasing the cheapest quote.",
    sourceLabel: "Deloitte Global Outsourcing Survey 2024",
  },
  {
    id: "deloitte-invest",
    figure: "80%",
    headline: "Most keep doing it",
    body: "Four in five companies plan to spend the same or more on outsourcing next year.",
    sourceLabel: "Deloitte Global Outsourcing Survey 2024",
  },
  {
    id: "stanford-retention",
    figure: "33%",
    headline: "Flexible work = fewer quits",
    body: "A Stanford trial cut resignations by a third. Performance held up.",
    sourceLabel: "Bloom, Han & Liang, Nature 2024",
  },
  {
    id: "ph-admin-va-rate",
    figure: "~$8",
    headline: "More left in the budget",
    body: "Typical hourly rate for general admin VAs in the Philippines — capacity without US payroll weight.",
    sourceLabel: "Industry VA rate guides, 2025–26",
    markets: ["us"],
  },
  {
    id: "deloitte-front-office",
    figure: "50%",
    headline: "Sales & marketing too",
    body: "Half of companies also offshore sales, marketing, or product work — not only back-office.",
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

/** Market-scoped primary nav — never US · AU · Careers as peer equals. */
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
    { href: `${home}#gate`, label: "Start Hiring", id: "hire", primary: true },
  ];
}

export function homeForSurface(surface: SiteSurface): string {
  if (surface === "ph") return "/ph";
  if (surface === "au") return "/au";
  return "/us";
}
