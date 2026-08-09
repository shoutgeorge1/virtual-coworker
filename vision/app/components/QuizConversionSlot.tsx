"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import LeadGate, { type GateCopy } from "./LeadGate";
import RoleQuiz, { type QuizCompletePayload } from "./RoleQuiz";
import { trackEvent } from "../../lib/tracking";
import type { MarketId } from "../../config/markets";
import type { AbVariant, CategorySlug } from "../../config/categories";

/**
 * Quiz LP hero slot: quiz first (no form on first paint). After the reward,
 * the employer form reveals in-place — prefilled role + size + seats.
 */
export default function QuizConversionSlot({
  market,
  category,
  variant,
  light,
  phoneDisplay,
  phoneHref,
  careersHref,
  gate,
}: {
  market: MarketId;
  category?: CategorySlug;
  variant: AbVariant;
  light: boolean;
  phoneDisplay?: string;
  phoneHref?: string | null;
  careersHref: string;
  gate: GateCopy;
}) {
  const [done, setDone] = useState<QuizCompletePayload | null>(null);
  const revealed = useRef(false);
  const isAu = market === "au";

  const onComplete = useCallback((payload: QuizCompletePayload) => {
    setDone(payload);
  }, []);

  const onRetake = useCallback(() => {
    revealed.current = false;
    setDone(null);
  }, []);

  useEffect(() => {
    if (!done || revealed.current) return;
    revealed.current = true;
    trackEvent("employer_gate_selected", {
      market,
      category: category || "",
      variant: variant || "",
      gate_variant: "inline",
      intent: "employer",
      source: "quiz_complete",
      cta_mode: "quiz_lp",
      landing_type: "quiz_lp",
      lp_surface: "quiz",
      company_size: done.companySize || "",
      positions_needed: done.positionsNeeded || "",
      form_role: done.formRole,
      result_role: done.trackLabel,
    });
    const t = window.setTimeout(() => {
      document.getElementById("gate")?.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    }, 420);
    return () => window.clearTimeout(t);
  }, [done, market, category, variant]);

  return (
    <>
      <RoleQuiz
        market={market}
        category={category}
        variant={variant}
        light={light}
        phoneDisplay={phoneDisplay}
        phoneHref={phoneHref}
        placement="hero"
        onComplete={onComplete}
        onRetake={onRetake}
      />
      <p className="quiz-lp-jobseeker">
        For businesses hiring staff.{" "}
        <a href={careersHref}>Looking for a job? Philippines careers →</a>
      </p>
      {done ? (
        <div className="quiz-gate-reveal">
          <LeadGate
            copy={{
              ...gate,
              eyebrow: isAu
                ? "Businesses only · 30 seconds"
                : "Employers only · 30 seconds",
              title: isAu
                ? "Have a chat — no obligation."
                : "Talk to a staffing specialist.",
            }}
            market={market}
            category={category}
            variant={variant}
            assumeEmployer
            preselectedRole={done.formRole}
            preselectedCompanySize={done.companySize}
            preselectedPositions={done.positionsNeeded}
            compactAfterQuiz
            lpSurface="quiz"
            ctaMode="quiz_lp"
          />
        </div>
      ) : null}
    </>
  );
}
