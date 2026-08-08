"use client";

import { useEffect, useRef, useState } from "react";
import type { IndustryStat, ProofFigure } from "../../config/site";

/**
 * Scroll-triggered number animation for the trust band.
 * Counters run once when the card enters view; `prefers-reduced-motion` and
 * no-IntersectionObserver both fall through to the final value immediately.
 */

const DURATION_MS = 1100;

function prefersReducedMotion(): boolean {
  if (typeof window === "undefined" || !window.matchMedia) return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

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

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3);
}

function useCountUp(target: number, run: boolean, decimals: number): number {
  // Always paint the approved figure first (SSR + delayed JS + never-in-view).
  // Animation is progressive enhancement once the card is seen.
  const [value, setValue] = useState(target);

  useEffect(() => {
    if (!run) {
      setValue(target);
      return;
    }
    if (prefersReducedMotion()) {
      setValue(target);
      return;
    }
    let raf = 0;
    setValue(0);
    const start = performance.now();
    const tick = (now: number) => {
      const p = Math.min(1, (now - start) / DURATION_MS);
      const next = target * easeOutCubic(p);
      setValue(Number(next.toFixed(decimals)));
      if (p < 1) raf = requestAnimationFrame(tick);
      else setValue(target);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [run, target, decimals]);

  return value;
}

function Counter({
  value,
  prefix = "",
  suffix = "",
  decimals = 0,
  run,
}: {
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  run: boolean;
}) {
  const shown = useCountUp(value, run, decimals);
  return (
    <>
      {prefix}
      {shown.toFixed(decimals)}
      {suffix}
    </>
  );
}

/** Big legitimacy numbers — years trading, rating, offices. */
export function ProofRow({ figures }: { figures: ProofFigure[] }) {
  const { ref, seen } = useInView<HTMLDivElement>();

  return (
    <div className="proof-row" ref={ref} aria-label="Company track record">
      {figures.map((f) => {
        const decimals = f.decimals || 0;
        const fallback = `${f.prefix || ""}${f.value.toFixed(decimals)}${f.suffix || ""}`;
        return (
          <div className={`proof-figure${seen ? " is-in" : ""}`} key={f.id}>
            <p className="proof-figure-value" data-fallback={fallback}>
              <noscript>{fallback}</noscript>
              <Counter
                value={f.value}
                prefix={f.prefix}
                suffix={f.suffix}
                decimals={decimals}
                run={seen}
              />
            </p>
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

  return (
    <article className={`trust-stat-card${seen ? " is-in" : ""}`} ref={ref}>
      <p className="trust-stat-figure">
        <Counter
          value={parsed.value}
          prefix={parsed.prefix}
          suffix={parsed.suffix}
          decimals={parsed.decimals}
          run={seen}
        />
      </p>
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
