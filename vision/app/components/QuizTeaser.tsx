"use client";

import { useEffect, useState } from "react";
import {
  assignExperiment,
  trackExperimentClick,
  trackExperimentView,
  type ExpVariant,
} from "../../lib/experiments";

/** Benefit-led teasers — “take the hiring quiz”, not “free 60 sec / stop guessing”. */
const TEASERS: Record<
  ExpVariant,
  { kicker: string; label: string }
> = {
  a: {
    kicker: "Hiring quiz",
    label: "Take the hiring quiz — who should you hire first? →",
  },
  b: {
    kicker: "Take the hiring quiz",
    label: "Who should you hire first? →",
  },
  c: {
    kicker: "Hiring quiz",
    label: "Take the hiring quiz →",
  },
};

/** Hero magnet — shares quiz_copy experiment with RoleQuiz. */
export default function QuizTeaser({ light = false }: { light?: boolean }) {
  const [variant, setVariant] = useState<ExpVariant>("a");

  useEffect(() => {
    const v = assignExperiment("quiz_copy");
    setVariant(v);
    trackExperimentView("quiz_copy", v, { surface: "hero_teaser" });
  }, []);

  const copy = TEASERS[variant] || TEASERS.a;

  return (
    <p className={`quiz-teaser anim-rise-d2${light ? " quiz-teaser-light" : ""}`}>
      <a
        href="#role-quiz"
        onClick={() =>
          trackExperimentClick("quiz_copy", variant, {
            surface: "hero_teaser",
            cta: "scroll_quiz",
          })
        }
      >
        <span className="quiz-teaser-kicker">{copy.kicker}</span>
        {copy.label}
      </a>
    </p>
  );
}
