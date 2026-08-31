"use client";

/**
 * US hub (/us) hero — selective live A/B:
 * A = female navy (va-us) · B = male portrait (va-au, AU control challenger).
 * Boot script stamps documentElement.dataset.usHeroPortrait before paint.
 */

import { useEffect, useState } from "react";
import {
  US_HERO_PORTRAIT_ARMS,
  assignExperiment,
  trackExperimentView,
  type ExpVariant,
} from "../../lib/experiments";

function armFromDom(): ExpVariant | null {
  if (typeof document === "undefined") return null;
  const raw = document.documentElement.dataset.usHeroPortrait;
  return raw === "a" || raw === "b" ? raw : null;
}

export default function UsBaselineHero({
  className,
  width = 960,
  height = 1280,
}: {
  className: string;
  width?: number;
  height?: number;
}) {
  const [variant, setVariant] = useState<ExpVariant>(() => armFromDom() || "a");

  useEffect(() => {
    const v = assignExperiment("us_hero_portrait");
    setVariant(v);
    try {
      document.documentElement.dataset.usHeroPortrait = v;
    } catch {
      /* ignore */
    }
    trackExperimentView("us_hero_portrait", v, {
      surface: "us_hub",
      market: "us",
      hero_label: US_HERO_PORTRAIT_ARMS[v === "b" ? "b" : "a"].label,
    });
  }, []);

  const arm = US_HERO_PORTRAIT_ARMS[variant === "b" ? "b" : "a"];

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      className={className}
      src={arm.src}
      alt={arm.alt}
      width={width}
      height={height}
      fetchPriority="high"
      decoding="async"
      data-us-hero={variant}
      data-hero-label={arm.label}
    />
  );
}
