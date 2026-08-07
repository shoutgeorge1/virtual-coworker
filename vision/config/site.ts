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
  /** Confirmed NA business line (published contact). */
  usPhoneDisplay: "310-730-9126",
  usPhoneHref: "tel:3107309126",
  addressUs: "750 N San Vicente Blvd, West Hollywood, CA 90069",
  addressAu: "11 York Street, Sydney NSW 2000, Australia",
  copyright: "© Virtual Coworker Inc. All Rights Reserved.",
} as const;

/** Short client quotes — text only; do not link out to WordPress. */
export const PUBLIC_QUOTES = [
  {
    quote:
      "The recruiting process was well organised, and I feel we were matched very well.",
    name: "Kyrstin H.",
    role: "General Manager",
  },
  {
    quote:
      "The hard part is having to go through the arduous recruitment process… That’s why I found Virtual Coworker really useful.",
    name: "Edwin O.",
    role: "Founder",
  },
  {
    quote:
      "They’ve been able to connect us with skilled candidates who really get our work and make a difference in what we do.",
    name: "Nicole G.",
    role: "Business Manager",
  },
] as const;

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
    { href: `${home}#gate`, label: "Start hiring", id: "hire", primary: true },
  ];
}

export function homeForSurface(surface: SiteSurface): string {
  if (surface === "ph") return "/ph";
  if (surface === "au") return "/au";
  return "/us";
}
