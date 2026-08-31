"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import LeadGate, { type GateCopy } from "./LeadGate";
import RoleQuiz, { type QuizCompletePayload } from "./RoleQuiz";
import { captureAttribution, trackEvent } from "../../lib/tracking";
import { exitToCareers } from "../../lib/job-seeker-exit";
import type { MarketId } from "../../config/markets";
import type { AbVariant, CategorySlug } from "../../config/categories";

const FORM_REVEAL_MS = 1800;

/**
 * Quiz LP hero slot: quiz first (no form on first paint). After the reward,
 * the employer form reveals in-place - prefilled role + size + seats.
 * Do not auto-scroll into the form; let the reward stay readable.
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
  const [showForm, setShowForm] = useState(false);
  const revealed = useRef(false);
  const isAu = market === "au";

  useEffect(() => {
    captureAttribution(market, {
      category: category || "",
      variant: variant || "",
      lp_variant: "quiz",
    });
  }, [market, category, variant]);

  const revealForm = useCallback(() => {
    setShowForm(true);
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("vc-quiz-form-ready"));
    }
  }, []);

  const onComplete = useCallback((payload: QuizCompletePayload) => {
    setDone(payload);
  }, []);

  const onRetake = useCallback(() => {
    revealed.current = false;
    setDone(null);
    setShowForm(false);
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("vc-quiz-retake"));
    }
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
      lp_variant: "quiz",
      company_size: done.companySize || "",
      positions_needed: done.positionsNeeded || "",
      form_role: done.formRole,
      result_role: done.trackLabel,
    });
    const t = window.setTimeout(revealForm, FORM_REVEAL_MS);
    return () => window.clearTimeout(t);
  }, [done, market, category, variant, revealForm]);

  return (
    <>
      <p className="quiz-lp-jobseeker quiz-lp-jobseeker-top">
        For businesses hiring staff.{" "}
        <a
          href={careersHref}
          onClick={(e) => {
            e.preventDefault();
            exitToCareers(careersHref, {
              market,
              category: category || "",
              variant: variant || "",
              source: "quiz_lp_link",
              lp_surface: "quiz",
              landing_type: "quiz_lp",
              lp_variant: "quiz",
            });
          }}
        >
          Looking for a job? Philippines careers →
        </a>
      </p>
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
        onRevealForm={revealForm}
      />
      {showForm && done ? (
        <div className="quiz-gate-reveal" id="quiz-form">
          <LeadGate
            copy={{
              ...gate,
              eyebrow: isAu
                ? "About 30 seconds · obligation free"
                : "About 30 seconds · free strategy call",
              title: isAu
                ? "Book a free strategy call"
                : "Book a free strategy call",
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
