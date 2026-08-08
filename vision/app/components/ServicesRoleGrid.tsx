"use client";

import Link from "next/link";
import {
  RolePortraitThumb,
  useRoleImageryVariant,
} from "./RoleImagery";
import { CATEGORY_SLUGS, CATEGORIES } from "../../config/categories";
import type { CategorySlug } from "../../config/categories";
import { PRIMARY_HIRE_CTA, ROLE_OUTCOMES } from "../../config/employer-cro";
import type { MarketId } from "../../config/markets";

/**
 * Tasteful per-card layout variety so the grid doesn’t read as one
 * uniform AI headshot strip. Content (unique image per title) stays put.
 */
const CARD_TREATMENTS: Record<
  CategorySlug,
  { frame: "flush" | "inset" | "mat"; crop: "high" | "mid" | "soft"; tone: "warm" | "cool" | "neutral"; accent: "cyan" | "gold" }
> = {
  "digital-marketing": { frame: "flush", crop: "high", tone: "warm", accent: "gold" },
  "social-media": { frame: "inset", crop: "mid", tone: "cool", accent: "cyan" },
  accounting: { frame: "mat", crop: "soft", tone: "neutral", accent: "cyan" },
  bookkeeping: { frame: "flush", crop: "mid", tone: "cool", accent: "gold" },
  "administrative-support": { frame: "inset", crop: "high", tone: "warm", accent: "cyan" },
  "customer-service": { frame: "mat", crop: "high", tone: "warm", accent: "gold" },
  hr: { frame: "flush", crop: "soft", tone: "neutral", accent: "cyan" },
  recruitment: { frame: "inset", crop: "soft", tone: "cool", accent: "gold" },
  sales: { frame: "mat", crop: "mid", tone: "warm", accent: "cyan" },
};

/**
 * Services role grid with unique portraits per title.
 * Assigns role_imagery once for the page; thumbs follow A/B.
 */
export default function ServicesRoleGrid({ market }: { market: MarketId }) {
  const variant = useRoleImageryVariant(market, "services_grid");

  return (
    <div className="services-grid">
      {CATEGORY_SLUGS.map((slug) => {
        const c = CATEGORIES[slug];
        const t = CARD_TREATMENTS[slug];
        return (
          <article
            className={`services-card services-card-with-photo services-card--${t.frame} services-card--tone-${t.tone} services-card--accent-${t.accent}`}
            key={slug}
            data-crop={t.crop}
          >
            <RolePortraitThumb category={slug} variant={variant} />
            <div className="services-card-body">
              <em>{c.shortLabel}</em>
              <h2>{c.label}</h2>
              <p>{ROLE_OUTCOMES[slug].problem}</p>
              <p className="services-card-gain">{ROLE_OUTCOMES[slug].gain}</p>
              <div className="services-card-links">
                <Link href={`/${market}/${slug}#gate`}>{PRIMARY_HIRE_CTA} →</Link>
                <Link href={`/${market}/${slug}`}>Role details</Link>
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
}
