/**
 * Public trust / legal facts scraped from live Virtual Coworker sites.
 * Do not invent reviews, ratings, client counts, licenses, or addresses here.
 *
 * Sources (2026-08-05 public HTML):
 * - https://virtualcoworker.com/contact/ — US + AU street addresses
 * - https://virtualcoworker.com/privacy/ · /terms/
 * - https://virtualcoworker.com/ — client quotes, Clutch / Google / Featured badges
 */

export const SITE = {
  name: "Virtual Coworker",
  legalEntity: "Virtual Coworker Inc.",
  tagline: "Paid hiring microsite",
  disclaimer:
    "Independent paid hiring microsite for employer inquiries. Separate from the main WordPress site.",
  corporateUrl: "https://virtualcoworker.com",
  corporateAuUrl: "https://virtualcoworker.com.au",
  privacyCorporate: "https://virtualcoworker.com/privacy/",
  termsCorporate: "https://virtualcoworker.com/terms/",
  /** Confirmed NA business line for this pilot (operator brief). */
  usPhoneDisplay: "310-426-8776",
  usPhoneHref: "tel:3104268776",
  /** Public footer addresses from virtualcoworker.com/contact/ */
  addressUs: "750 N San Vicente Blvd, West Hollywood, CA 90069",
  addressAu: "11 York Street, Sydney NSW 2000, Australia",
  copyright: "© Virtual Coworker Inc. All Rights Reserved.",
} as const;

/** Short client quotes published on virtualcoworker.com homepage. */
export const PUBLIC_QUOTES = [
  {
    quote:
      "The recruiting process was well organized, and I feel we were matched very well.",
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

export const NAV = [
  { href: "/services", label: "Services", id: "services" },
  { href: "/how-it-works", label: "How it works", id: "how" },
  { href: "/us", label: "US", id: "us" },
  { href: "/au", label: "AU", id: "au" },
  { href: "/us#gate", label: "Start hiring", id: "hire", primary: true },
  { href: "/ph", label: "Careers", id: "careers" },
] as const;

export type NavId = (typeof NAV)[number]["id"];
