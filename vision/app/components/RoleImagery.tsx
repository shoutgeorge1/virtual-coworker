"use client";

import { useEffect, useState } from "react";
import {
  assignExperiment,
  trackExperimentView,
  type ExpVariant,
} from "../../lib/experiments";
import {
  portraitAltForCategory,
  portraitSrcForCategory,
  roleImageryFor,
} from "../../config/role-imagery";
import type { CategorySlug } from "../../config/categories";
import type { MarketId } from "../../config/markets";

/** Sticky assign + view fire for role_imagery. */
export function useRoleImageryVariant(
  market: MarketId,
  surface: string,
): ExpVariant {
  const [variant, setVariant] = useState<ExpVariant>("a");
  useEffect(() => {
    const v = assignExperiment("role_imagery");
    setVariant(v);
    trackExperimentView("role_imagery", v, { surface, market });
  }, [market, surface]);
  return variant;
}

/** Hero va-card with per-category portrait A/B (category LPs) or market fallback. */
export function RoleHeroCard({
  category,
  market,
  fallbackSrc,
  fallbackAlt,
  shell,
  shortLabel,
  captionTitle,
  captionSub,
}: {
  category?: CategorySlug | null;
  market: MarketId;
  fallbackSrc: string;
  fallbackAlt: string;
  shell: string;
  shortLabel: string;
  captionTitle: string;
  captionSub: string;
}) {
  const variant = useRoleImageryVariant(market, "market_landing");
  const heroSrc = category
    ? portraitSrcForCategory(category, variant)
    : fallbackSrc;
  const heroAlt = category ? portraitAltForCategory(category) : fallbackAlt;

  return (
    <figure
      className={`va-card ${shell}-va anim-rise-d1`}
      data-role-imagery={variant}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={heroSrc} alt={heroAlt} />
      <span className="va-card-tag">
        <i />
        {shortLabel}
      </span>
      <figcaption>
        <b>{captionTitle}</b>
        <span>{captionSub}</span>
      </figcaption>
    </figure>
  );
}

/** Late-page trust photo near FAQ — consult (a) vs team table (b). */
export function TrustLatePhoto({
  market,
  light = false,
}: {
  market: MarketId;
  light?: boolean;
}) {
  // Sticky assignment shared with RoleHeroCard; view deduped per session.
  const [variant, setVariant] = useState<ExpVariant>("a");
  useEffect(() => {
    const v = assignExperiment("role_imagery");
    setVariant(v);
    trackExperimentView("role_imagery", v, {
      surface: "market_landing_trust",
      market,
    });
  }, [market]);
  const arm = roleImageryFor(variant);
  return (
    <figure
      className={`trust-late${light ? " trust-late-light" : ""}`}
      data-role-imagery={variant}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={arm.trust} alt={arm.trustAlt} />
      <figcaption>
        Real people. Real shortlists. You interview before anyone starts.
      </figcaption>
    </figure>
  );
}

/** Portrait thumb for a services card — one unique image per category title. */
export function RolePortraitThumb({
  category,
  variant,
}: {
  category: CategorySlug;
  variant: ExpVariant;
}) {
  return (
    <span className="services-card-photo" aria-hidden>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={portraitSrcForCategory(category, variant)}
        alt=""
        data-role-imagery={variant}
      />
    </span>
  );
}
