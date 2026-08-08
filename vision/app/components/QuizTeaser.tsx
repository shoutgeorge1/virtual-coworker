"use client";

import { useEffect, useState } from "react";
import {
  assignExperiment,
  trackExperimentClick,
  trackExperimentView,
  type ExpVariant,
} from "../../lib/experiments";

/** Benefit-led teasers — each leads with what the reader gets, not the quiz. */
const TEASERS: Record<
  ExpVariant,
  { kicker: string; label: string }
> = {
  a: {
    kicker: "Free · 60 sec",
    label: "Find the hire that buys back your week →",
  },
  b: {
    kicker: "Free · 3 taps",
    label: "Which job should you hand off first? →",
  },
  c: {
    kicker: "Free · 60 sec",
    label: "Stop guessing your next hire →",
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
