"use client";

import { useMemo, useState } from "react";
import { trackEvent } from "../../lib/tracking";
import type { MarketId } from "../../config/markets";
import type { AbVariant } from "../../config/categories";

type Answers = {
  bottleneck: string;
  hours: string;
  firstSeat: string;
};

const RESULT_COPY: Record<
  string,
  { title: string; blurb: string; roleHint: string }
> = {
  admin: {
    title: "Start with a dedicated admin / VA seat",
    blurb:
      "Inbox, calendar, and ops follow-through free you up fastest — then layer specialists.",
    roleHint: "Administrative support",
  },
  marketing: {
    title: "Start with marketing or social support",
    blurb:
      "If growth work is stuck in drafts and posting, a dedicated marketing seat pays back first.",
    roleHint: "Digital marketing",
  },
  books: {
    title: "Start with bookkeeping or accounting support",
    blurb:
      "Clean books and AP/AR cadence usually unlock better decisions before you scale headcount.",
    roleHint: "Bookkeeping",
  },
  support: {
    title: "Start with customer support",
    blurb:
      "If response time is the bottleneck, a dedicated support seat protects revenue and reviews.",
    roleHint: "Customer service",
  },
};

function flagEnabled(): boolean {
  const raw = (process.env.NEXT_PUBLIC_ENABLE_ROLE_QUIZ || "").trim().toLowerCase();
  return raw !== "false";
}

function scoreResult(a: Answers): keyof typeof RESULT_COPY {
  if (a.firstSeat === "marketing" || a.bottleneck === "growth") return "marketing";
  if (a.firstSeat === "books" || a.bottleneck === "finance") return "books";
  if (a.firstSeat === "support" || a.bottleneck === "customers") return "support";
  return "admin";
}

/**
 * “What role should you hire first?” — short quiz → shortlist CTA / #gate.
 */
export default function RoleQuiz({
  market,
  category,
  variant,
  light = false,
}: {
  market: MarketId;
  category?: string;
  variant?: AbVariant;
  light?: boolean;
}) {
  const enabled = flagEnabled();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Answers>({
    bottleneck: "",
    hours: "",
    firstSeat: "",
  });

  const result = useMemo(() => {
    if (step < 3) return null;
    return RESULT_COPY[scoreResult(answers)];
  }, [answers, step]);

  if (!enabled) return null;

  const track = (event: string, extra: Record<string, string> = {}) => {
    trackEvent(event, {
      market,
      category: category || "",
      variant: variant || "",
      assist_type: "role_quiz",
      ...extra,
    });
  };

  const questions = [
    {
      key: "bottleneck" as const,
      q: "Where does work pile up most?",
      options: [
        { id: "ops", label: "Inbox, admin, scheduling" },
        { id: "growth", label: "Marketing / content / social" },
        { id: "finance", label: "Books, invoices, AP/AR" },
        { id: "customers", label: "Customer questions & tickets" },
      ],
    },
    {
      key: "hours" as const,
      q: "What coverage matters most?",
      options: [
        { id: "overlap", label: "Overlap with my business hours" },
        { id: "full", label: "Full-time dedicated seat" },
        { id: "flex", label: "Flexible as long as work ships" },
      ],
    },
    {
      key: "firstSeat" as const,
      q: "If you could hire one seat this month…",
      options: [
        { id: "admin", label: "Admin / VA" },
        { id: "marketing", label: "Marketing / social" },
        { id: "books", label: "Bookkeeping / accounting" },
        { id: "support", label: "Customer support" },
      ],
    },
  ];

  const current = questions[step];

  return (
    <section
      className={`role-quiz${light ? " role-quiz-light" : ""}`}
      aria-labelledby="role-quiz-title"
    >
      <div className="role-quiz-inner">
        <p className="role-quiz-eyebrow">60-second guide</p>
        <h2 id="role-quiz-title">What role should you hire first?</h2>
        <p className="role-quiz-lead">
          Three quick questions — then we’ll point you at the right shortlist conversation.
        </p>

        {step < 3 && current ? (
          <div className="role-quiz-card">
            <p className="role-quiz-step">
              {step + 1} / 3
            </p>
            <h3>{current.q}</h3>
            <div className="role-quiz-options">
              {current.options.map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => {
                    const nextAnswers = { ...answers, [current.key]: opt.id };
                    setAnswers(nextAnswers);
                    const nextStep = step + 1;
                    setStep(nextStep);
                    track("quiz_step", {
                      step: String(nextStep),
                      answer: opt.id,
                    });
                    if (nextStep === 3) {
                      const r = RESULT_COPY[scoreResult(nextAnswers)];
                      track("quiz_completed", { result: r.roleHint });
                      trackEvent("lead_magnet_completed", {
                        market,
                        category: category || "",
                        variant: variant || "",
                        magnet: "role_quiz",
                        result_role: r.roleHint,
                      });
                    }
                  }}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        ) : null}

        {result ? (
          <div className="role-quiz-result">
            <p className="role-quiz-result-kicker">Your first-hire read</p>
            <h3>{result.title}</h3>
            <p>{result.blurb}</p>
            <div className="role-quiz-actions">
              <a
                href="#gate"
                className="role-quiz-primary"
                onClick={() =>
                  track("conversion_assist_cta_clicked", {
                    cta: "form",
                    result_role: result.roleHint,
                  })
                }
              >
                Tell us about this role →
              </a>
              <button
                type="button"
                className="role-quiz-ghost"
                onClick={() => {
                  setStep(0);
                  setAnswers({ bottleneck: "", hours: "", firstSeat: "" });
                }}
              >
                Retake
              </button>
            </div>
            <p className="role-quiz-note">
              Next step is a short hiring conversation — not an instant hire.
            </p>
          </div>
        ) : null}
      </div>
    </section>
  );
}
