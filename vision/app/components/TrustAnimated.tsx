"use client";

import { useEffect, useRef, useState } from "react";
import type { IndustryStat, ProofFigure } from "../../config/site";

/**
 * Scroll-triggered trust-band reveals.
 * Final proof figures always paint (SSR + client) — never count up from 0
 * (that flashed "0+", "0.0/5", "0" while the card faded in).
 * Entrance motion is CSS (.proof-figure.is-in / .trust-stat-card.is-in).
 */

/** Fires once when the element first scrolls into view. */
function useInView<T extends HTMLElement>() {
  const ref = useRef<T | null>(null);
  const [seen, setSeen] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el || seen) return;
    if (typeof IntersectionObserver === "undefined") {
      setSeen(true);
      return;
    }
    const obs = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setSeen(true);
          obs.disconnect();
        }
      },
      { threshold: 0.35, rootMargin: "0px 0px -8% 0px" },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [seen]);

  return { ref, seen };
}

function formatFigure(
  value: number,
  prefix = "",
  suffix = "",
  decimals = 0,
): string {
  return `${prefix}${value.toFixed(decimals)}${suffix}`;
}

/** Big legitimacy numbers — years trading, rating, offices. */
export function ProofRow({ figures }: { figures: ProofFigure[] }) {
  const { ref, seen } = useInView<HTMLDivElement>();

  return (
    <div className="proof-row" ref={ref} aria-label="Company track record">
      {figures.map((f) => {
        const decimals = f.decimals || 0;
        const text = formatFigure(f.value, f.prefix, f.suffix, decimals);
        return (
          <div className={`proof-figure${seen ? " is-in" : ""}`} key={f.id}>
            <p className="proof-figure-value">{text}</p>
            <p className="proof-figure-label">{f.label}</p>
            <p className="proof-figure-note">{f.note}</p>
          </div>
        );
      })}
    </div>
  );
}

/**
 * Splits a published figure string ("42%", "~$8") into animatable parts.
 * Percentages also drive the bar fill; anything else renders without a bar.
 */
function parseFigure(figure: string): {
  prefix: string;
  value: number;
  suffix: string;
  decimals: number;
  percent: number | null;
} {
  const m = figure.match(/^([^\d.]*)([\d.]+)(.*)$/);
  if (!m) {
    return { prefix: figure, value: 0, suffix: "", decimals: 0, percent: null };
  }
  const [, prefix, digits, suffix] = m;
  const decimals = digits.includes(".") ? digits.split(".")[1].length : 0;
  const value = Number(digits);
  const percent = suffix.trim().startsWith("%") ? Math.min(100, value) : null;
  return { prefix, value, suffix, decimals, percent };
}

function StatCard({ stat }: { stat: IndustryStat }) {
  const { ref, seen } = useInView<HTMLElement>();
  const parsed = parseFigure(stat.figure);
  const text = formatFigure(
    parsed.value,
    parsed.prefix,
    parsed.suffix,
    parsed.decimals,
  );

  return (
    <article className={`trust-stat-card${seen ? " is-in" : ""}`} ref={ref}>
      <p className="trust-stat-figure">{text}</p>
      {parsed.percent !== null ? (
        <div
          className="trust-stat-bar"
          role="img"
          aria-label={`${stat.figure} of those surveyed`}
        >
          <span
            className="trust-stat-bar-fill"
            style={{ width: seen ? `${parsed.percent}%` : "0%" }}
          />
        </div>
      ) : null}
      <h4>{stat.headline}</h4>
      <p>{stat.body}</p>
      <p className="trust-stat-source">Source: {stat.sourceLabel}</p>
    </article>
  );
}

export function StatsGrid({ stats }: { stats: IndustryStat[] }) {
  return (
    <div className="trust-stats-grid">
      {stats.map((s) => (
        <StatCard stat={s} key={s.id} />
      ))}
    </div>
  );
}
