/**
 * SEO helpers for the employer microsite.
 * Canonical host: www.virtualcoworker.app
 *
 * Indexability:
 * - NEXT_PUBLIC_PILOT_NOINDEX=true → force noindex everywhere (QA / pre-launch)
 * - Unset or false → page-level robots win (employer money pages index; thank-you noindex)
 */

import type { Metadata } from "next";
import { SITE } from "../config/site";
import { CATEGORY_SLUGS } from "../config/categories";

export const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL || "https://www.virtualcoworker.app"
).replace(/\/$/, "");

export const DEFAULT_OG_IMAGE = `${SITE_URL}/brand/hero-us-2026.jpg`;

/** Explicit pilot kill-switch. Production should leave unset or "false". */
export function isPilotNoindex(): boolean {
  return (process.env.NEXT_PUBLIC_PILOT_NOINDEX || "").trim() === "true";
}

export function robotsFor(
  intent: "index" | "noindex" = "index",
): NonNullable<Metadata["robots"]> {
  if (isPilotNoindex() || intent === "noindex") {
    return {
      index: false,
      follow: false,
      googleBot: { index: false, follow: false },
    };
  }
  return { index: true, follow: true };
}

export function absoluteUrl(path: string): string {
  if (!path) return SITE_URL;
  if (/^https?:\/\//i.test(path)) return path;
  return `${SITE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

export function buildPageMetadata(opts: {
  title: string;
  description: string;
  path: string;
  /** Default true for employer surfaces; thank-you / consult / ph exit → false */
  indexable?: boolean;
  ogImage?: string;
  ogType?: "website" | "article";
}): Metadata {
  const url = absoluteUrl(opts.path);
  const image = opts.ogImage
    ? absoluteUrl(opts.ogImage)
    : DEFAULT_OG_IMAGE;
  const indexable = opts.indexable !== false;

  return {
    title: opts.title,
    description: opts.description,
    alternates: { canonical: url },
    robots: robotsFor(indexable ? "index" : "noindex"),
    openGraph: {
      type: opts.ogType || "website",
      url,
      siteName: SITE.name,
      title: opts.title,
      description: opts.description,
      images: [{ url: image, alt: SITE.name }],
      locale: "en_US",
    },
    twitter: {
      card: "summary_large_image",
      title: opts.title,
      description: opts.description,
      images: [image],
    },
  };
}

export function organizationJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: SITE.name,
    legalName: SITE.legalEntity,
    url: SITE_URL,
    logo: absoluteUrl("/brand/logo-vc.png"),
    telephone: SITE.usPhoneDisplay,
    sameAs: ["https://virtualcoworker.com.ph"],
    address: [
      {
        "@type": "PostalAddress",
        streetAddress: "750 N San Vicente Blvd",
        addressLocality: "West Hollywood",
        addressRegion: "CA",
        postalCode: "90069",
        addressCountry: "US",
      },
      {
        "@type": "PostalAddress",
        streetAddress: "11 York Street",
        addressLocality: "Sydney",
        addressRegion: "NSW",
        postalCode: "2000",
        addressCountry: "AU",
      },
    ],
  };
}

export function professionalServiceJsonLd(market: "us" | "au") {
  const isAu = market === "au";
  return {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    name: `${SITE.name} · ${isAu ? "Australia" : "United States"}`,
    description: isAu
      ? "Hire dedicated Filipino staff for Australian businesses - recruit, screen, interview, and hire."
      : "Hire dedicated Filipino virtual assistants and remote staff for US businesses - recruit, vet, you interview and decide.",
    url: absoluteUrl(isAu ? "/au" : "/us"),
    telephone: isAu ? undefined : SITE.usPhoneDisplay,
    image: absoluteUrl(isAu ? "/brand/hero-au-2026.jpg" : "/brand/hero-us-2026.jpg"),
    areaServed: isAu
      ? { "@type": "Country", name: "Australia" }
      : { "@type": "Country", name: "United States" },
    address: {
      "@type": "PostalAddress",
      streetAddress: isAu ? "11 York Street" : "750 N San Vicente Blvd",
      addressLocality: isAu ? "Sydney" : "West Hollywood",
      addressRegion: isAu ? "NSW" : "CA",
      postalCode: isAu ? "2000" : "90069",
      addressCountry: isAu ? "AU" : "US",
    },
    parentOrganization: { "@type": "Organization", name: SITE.name, url: SITE_URL },
  };
}

export function websiteJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: SITE.name,
    url: SITE_URL,
    publisher: { "@type": "Organization", name: SITE.name },
  };
}

export function breadcrumbJsonLd(
  items: { name: string; path: string }[],
) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.name,
      item: absoluteUrl(item.path),
    })),
  };
}

export function faqPageJsonLd(faqs: { q: string; a: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: f.a },
    })),
  };
}

/** Paths included in sitemap (employer + trust surfaces only). */
export function sitemapPaths(): { path: string; priority: number }[] {
  const paths: { path: string; priority: number }[] = [
    { path: "/us", priority: 1 },
    { path: "/au", priority: 1 },
    { path: "/services?market=us", priority: 0.8 },
    { path: "/services?market=au", priority: 0.8 },
    { path: "/how-it-works?market=us", priority: 0.8 },
    { path: "/how-it-works?market=au", priority: 0.8 },
    { path: "/privacy", priority: 0.3 },
    { path: "/terms", priority: 0.3 },
  ];
  for (const slug of CATEGORY_SLUGS) {
    paths.push({ path: `/us/${slug}`, priority: 0.9 });
    paths.push({ path: `/au/${slug}`, priority: 0.9 });
  }
  paths.push({ path: "/us/real-estate", priority: 0.8 });
  return paths;
}
