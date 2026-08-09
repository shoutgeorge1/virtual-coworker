"use client";

import { useEffect, useMemo, useState } from "react";
import { trackEvent, trackPhoneClick } from "../../lib/tracking";
import { focusGate } from "../../lib/focus-gate";
import {
  assignExperiment,
  trackExperimentClick,
  trackExperimentConvert,
  trackExperimentView,
  type ExpVariant,
} from "../../lib/experiments";
import { SITE } from "../../config/site";
import type { MarketId } from "../../config/markets";
import {
  formLabelForSlug,
  type AbVariant,
  type CategorySlug,
} from "../../config/categories";

/** Q1 drain → role path. One tap locks the recommendation lane. */
type DrainKey = "admin" | "marketing" | "books" | "support" | "sales";

/** Quiz drain lane → LeadGate role chip label. */
const DRAIN_TO_FORM_SLUG: Record<DrainKey, CategorySlug> = {
  admin: "administrative-support",
  marketing: "digital-marketing",
  books: "bookkeeping",
  support: "customer-service",
  sales: "sales",
};

function formRoleForDrain(drain: DrainKey): string {
  return formLabelForSlug(DRAIN_TO_FORM_SLUG[drain]);
}

type Answers = {
  drain: DrainKey | "";
  focus: string;
  detail: string;
};

type QuizOption = { id: string; label: string };

type QuizQuestion = {
  key: "drain" | "focus" | "detail";
  q: string;
  options: QuizOption[];
};

type RoleResult = {
  roleKey: DrainKey;
  /** Big bold payoff line — this is the whole result screen. */
  roleLabel: string;
  /** Reporting label (kept stable for dataLayer history where possible). */
  trackLabel: string;
  because: string;
  profileTip: string;
  /** Default “what changes” if detail has no override. */
  changeDefault: string;
};

type FocusPack = {
  because: string;
  profileTip: string;
};

type DetailPack = {
  change: string;
};

type PathConfig = {
  /** Q2 — specific to this drain. */
  focusQ: string;
  focusOptions: QuizOption[];
  /** Q3 — still specific; shapes coverage / software / load. */
  detailQ: string;
  detailOptions: QuizOption[];
  focusCopy: Record<string, FocusPack>;
  detailCopy: Record<string, DetailPack>;
};

type QuizFrame = {
  eyebrow: string;
  title: string;
  lead: string;
  kicker: string;
  whoLabel: string;
  timeLabel: string;
};

/**
 * quiz_copy A/B — benefit-led headline framing (George: the old
 * "it'll change how you hire" line was too soft). Each variant leads with the
 * payoff, and `kicker` sets the tone of the win screen.
 * Logic (branching Q2/Q3) is shared — variants are copy skin only.
 * AU frames: same quiz, understated B2B English — not US copy with hours swapped.
 */
const FRAMES_US: Record<ExpVariant, QuizFrame> = {
  a: {
    eyebrow: "Take the hiring quiz",
    title: "Who should you hire first?",
    lead: "Three taps. We’ll name the seat that buys back your week.",
    kicker: "Your first hire",
    whoLabel: "Look for",
    timeLabel: "What changes",
  },
  b: {
    eyebrow: "Take the hiring quiz",
    title: "See which teammate to hire.",
    lead: "Tap through. Get a clear answer. Then talk to a specialist.",
    kicker: "Hire this",
    whoLabel: "Look for",
    timeLabel: "What changes",
  },
  c: {
    eyebrow: "Take the hiring quiz",
    title: "Find the teammate that gets you your week back.",
    lead: "Three questions. A straight recommendation. Then talk — free, no pressure.",
    kicker: "Your answer",
    whoLabel: "Look for",
    timeLabel: "What changes",
  },
};

const FRAMES_AU: Record<ExpVariant, QuizFrame> = {
  a: {
    eyebrow: "Take the hiring quiz",
    title: "Who should you hire first?",
    lead: "Three taps. We’ll name the role that takes the load.",
    kicker: "Your first hire",
    whoLabel: "Look for",
    timeLabel: "What changes",
  },
  b: {
    eyebrow: "Take the hiring quiz",
    title: "See which teammate to hire.",
    lead: "Tap through. Get a clear answer. Then have a chat.",
    kicker: "Hire this",
    whoLabel: "Look for",
    timeLabel: "What changes",
  },
  c: {
    eyebrow: "Take the hiring quiz",
    title: "Find the teammate that gets you your week back.",
    lead: "Three questions. A straight recommendation. Then have a chat — free, no pressure.",
    kicker: "Your answer",
    whoLabel: "Look for",
    timeLabel: "What changes",
  },
};

function drainQuestion(market: MarketId): QuizQuestion {
  return {
    key: "drain",
    q: market === "au" ? "What’s chewing up the week?" : "What’s eating your week?",
    options: [
      { id: "admin", label: "Email, calendar, admin" },
      { id: "marketing", label: "Marketing never gets done" },
      { id: "books", label: "Invoices and bookkeeping" },
      { id: "support", label: "Customers waiting on replies" },
      { id: "sales", label: "Sales and follow-ups stall" },
    ],
  };
}

function pathsFor(market: MarketId): Record<DrainKey, PathConfig> {
  const isAu = market === "au";
  const hoursPhrase = isAu ? "Australian hours" : "your hours";

  return {
    admin: {
      focusQ: "What piles up first?",
      focusOptions: [
        { id: "inbox", label: "Inbox triage" },
        { id: "calendar", label: "Calendar and scheduling" },
        { id: "docs", label: "Docs, data entry, filing" },
        { id: "ops", label: "Travel and ops busywork" },
      ],
      detailQ: "How should they work?",
      detailOptions: isAu
        ? [
            { id: "overlap", label: "Online when I am — Australian hours" },
            { id: "full", label: "Full-time, just for my business" },
            { id: "flex", label: "Flexible — just get it done" },
          ]
        : [
            { id: "overlap", label: "Online when I am — my hours" },
            { id: "full", label: "Full-time, just for my business" },
            { id: "flex", label: "Flexible — just get it done" },
          ],
      focusCopy: {
        inbox: {
          because: "Your inbox stops owning the morning.",
          profileTip: "A steady organiser who triages mail without being asked.",
        },
        calendar: {
          because: "Meetings get booked — you just show up.",
          profileTip: "Someone sharp with calendars who protects your focus time.",
        },
        docs: {
          because: "Docs and data stop living in your head.",
          profileTip: "A detail person who keeps files and lists tidy.",
        },
        ops: {
          because: "Ops busywork gets handled before it hits you.",
          profileTip: "A reliable doer who owns the day-to-day errands.",
        },
      },
      detailCopy: {
        overlap: {
          change: `Working ${hoursPhrase}, so things move while you’re in meetings.`,
        },
        full: { change: "Full-time means a real weekly load comes off you." },
        flex: {
          change: "Flexible hours work fine once one person owns the day-to-day.",
        },
      },
    },
    marketing: {
      focusQ: "Where does marketing stall?",
      focusOptions: [
        { id: "social", label: "Social posts never go out" },
        { id: "ads", label: "Ads and campaigns" },
        { id: "content", label: "Blogs and longer content" },
        { id: "email", label: "Email newsletters" },
      ],
      detailQ: "How much do you want off your plate?",
      detailOptions: [
        { id: "rhythm", label: "A few hours a week — keep the rhythm" },
        { id: "most", label: "Most of the weekly marketing load" },
        { id: "seat", label: "Own the whole marketing seat" },
      ],
      focusCopy: {
        social: {
          because: "Posts actually ship on a weekly rhythm.",
          profileTip: "A doer who drafts, schedules, and keeps the feed alive.",
        },
        ads: {
          because: "Campaigns get built and checked — not stuck in drafts.",
          profileTip: "Someone who can set up ads and report what worked.",
        },
        content: {
          because: "Longer content leaves your plate and still gets published.",
          profileTip: "A writer who turns briefs into posts you can approve fast.",
        },
        email: {
          because: "Newsletters go out on time instead of slipping a week.",
          profileTip: "Someone who owns the list, the draft, and the send.",
        },
      },
      detailCopy: {
        rhythm: {
          change: "A light weekly cadence — enough to stay visible without owning it.",
        },
        most: {
          change: "Most of the weekly marketing load leaves your calendar.",
        },
        seat: {
          change: "One person owns the marketing seat so you only approve.",
        },
      },
    },
    books: {
      focusQ: "What’s the money mess?",
      focusOptions: [
        { id: "ar", label: "Invoices and chasing payments" },
        { id: "ap", label: "Bills and expenses" },
        { id: "payroll", label: "Payroll" },
        { id: "catchup", label: "Catching up the books" },
      ],
      detailQ: "What do you use today?",
      detailOptions: [
        { id: "qb", label: "QuickBooks" },
        { id: "xero", label: "Xero" },
        { id: "sheets", label: "Spreadsheets / mixed" },
        { id: "unsure", label: "Not sure yet" },
      ],
      focusCopy: {
        ar: {
          because: "Invoices go out and payments get chased — not ignored.",
          profileTip: "A detail person who owns AR follow-ups every week.",
        },
        ap: {
          because: "Bills and expenses stay coded instead of piling up.",
          profileTip: "Someone tidy with receipts who keeps AP current.",
        },
        payroll: {
          because: "Payroll prep stops being a monthly scramble.",
          profileTip: "A careful assistant who preps payroll on a fixed rhythm.",
        },
        catchup: {
          because: "The backlog clears and the books stay current.",
          profileTip: "Someone who can catch up months of books, then keep pace.",
        },
      },
      detailCopy: {
        qb: { change: "They work inside QuickBooks so your numbers stay in one place." },
        xero: { change: "They work inside Xero so your numbers stay in one place." },
        sheets: {
          change: "They tidy what you have now — then help you pick a cleaner system.",
        },
        unsure: {
          change: "We match someone who can work in common tools and help you choose.",
        },
      },
    },
    support: {
      focusQ: "What customer work is drowning you?",
      focusOptions: [
        { id: "tickets", label: "Ticket and email volume" },
        { id: "repeats", label: "Same questions every day" },
        { id: "after", label: "After-hours replies" },
        { id: "chat", label: "Chat while you’re in meetings" },
      ],
      detailQ: "When do you need coverage?",
      detailOptions: isAu
        ? [
            { id: "overlap", label: "Overlap with me — Australian hours" },
            { id: "biz", label: "Business hours, full coverage" },
            { id: "flex", label: "Flexible — just clear the queue" },
          ]
        : [
            { id: "overlap", label: "Overlap with me — my hours" },
            { id: "biz", label: "Business hours, full coverage" },
            { id: "flex", label: "Flexible — just clear the queue" },
          ],
      focusCopy: {
        tickets: {
          because: "The ticket pile gets answered before it owns your night.",
          profileTip: "A calm communicator who owns first replies end to end.",
        },
        repeats: {
          because: "Repeat questions get a playbook — and someone to run it.",
          profileTip: "Someone who learns your FAQs and answers without pinging you.",
        },
        after: {
          because: "After-hours messages don’t wait until you wake up.",
          profileTip: "A reliable first-reply person for the hours you can’t cover.",
        },
        chat: {
          because: "Live chat gets handled while you’re in meetings.",
          profileTip: "Someone quick and clear who can chat without escalating everything.",
        },
      },
      detailCopy: {
        overlap: {
          change: `Working ${hoursPhrase}, so nobody waits while you’re heads-down.`,
        },
        biz: { change: "Full business-hours coverage protects your response times." },
        flex: { change: "Flexible hours work when one person owns the customer inbox." },
      },
    },
    sales: {
      focusQ: "Where does sales stall?",
      focusOptions: [
        { id: "outbound", label: "Outbound and cold outreach" },
        { id: "followups", label: "Follow-ups falling through" },
        { id: "crm", label: "CRM never stays clean" },
        { id: "booking", label: "Booking meetings" },
      ],
      detailQ: "What do you need most?",
      detailOptions: [
        { id: "top", label: "Fill the top of the funnel" },
        { id: "pipeline", label: "Keep the pipeline moving" },
        { id: "close", label: "Support closing and handoffs" },
      ],
      focusCopy: {
        outbound: {
          because: "Outreach happens on a schedule — not when you remember.",
          profileTip: "A hunter who can run lists, opens, and first touches daily.",
        },
        followups: {
          because: "Warm leads get followed up before they go cold.",
          profileTip: "Someone relentless about reminders and next steps.",
        },
        crm: {
          because: "The CRM stays current so you trust the pipeline.",
          profileTip: "A tidy operator who logs notes and stages without nagging.",
        },
        booking: {
          because: "Qualified meetings land on your calendar.",
          profileTip: "Someone who qualifies, books, and confirms so you just show up.",
        },
      },
      detailCopy: {
        top: { change: "More first touches every week — without you writing every email." },
        pipeline: {
          change: "Deals keep moving because follow-ups and CRM hygiene are owned.",
        },
        close: {
          change: "You stay on closes; they handle prep, notes, and handoffs.",
        },
      },
    },
  };
}

function baseResults(): Record<DrainKey, RoleResult> {
  return {
    admin: {
      roleKey: "admin",
      roleLabel: "An admin assistant",
      trackLabel: "admin / VA support",
      because: "Your inbox and calendar stop owning your day.",
      profileTip: "A steady organiser who clears busywork without being asked.",
      changeDefault: "One person owns the day-to-day so you get your week back.",
    },
    marketing: {
      roleKey: "marketing",
      roleLabel: "A marketing & social assistant",
      trackLabel: "marketing / social support",
      because: "Content actually ships instead of sitting in drafts.",
      profileTip: "A doer who keeps posts moving on a weekly rhythm.",
      changeDefault: "Marketing leaves your plate — you only approve.",
    },
    books: {
      roleKey: "books",
      roleLabel: "A bookkeeping assistant",
      trackLabel: "bookkeeping / accounting support",
      because: "Clean books, invoices chased, decisions on real numbers.",
      profileTip: "A detail person who keeps invoices and books tidy.",
      changeDefault: "Money admin stops piling up every month.",
    },
    support: {
      roleKey: "support",
      roleLabel: "A customer support assistant",
      trackLabel: "customer support",
      because: "Customers get answers fast — without waiting on you.",
      profileTip: "A calm communicator who owns the first reply.",
      changeDefault: "Response times stay protected without you on every thread.",
    },
    sales: {
      roleKey: "sales",
      roleLabel: "A sales support assistant",
      trackLabel: "sales support",
      because: "Pipeline work happens daily — not when you have a spare hour.",
      profileTip: "A closer’s helper who owns outreach, follow-ups, and CRM.",
      changeDefault: "Sales busywork leaves your week so you can sell.",
    },
  };
}

function flagEnabled(): boolean {
  const raw = (process.env.NEXT_PUBLIC_ENABLE_ROLE_QUIZ || "").trim().toLowerCase();
  return raw !== "false";
}

function isDrainKey(id: string): id is DrainKey {
  return (
    id === "admin" ||
    id === "marketing" ||
    id === "books" ||
    id === "support" ||
    id === "sales"
  );
}

function buildResult(
  answers: Answers,
  market: MarketId,
): {
  roleKey: DrainKey;
  formRole: string;
  roleLabel: string;
  trackLabel: string;
  because: string;
  profileTip: string;
  timeInsight: string;
} | null {
  if (!answers.drain || !isDrainKey(answers.drain)) return null;
  const base = baseResults()[answers.drain];
  const path = pathsFor(market)[answers.drain];
  const focus = path.focusCopy[answers.focus];
  const detail = path.detailCopy[answers.detail];
  return {
    roleKey: answers.drain,
    formRole: formRoleForDrain(answers.drain),
    roleLabel: base.roleLabel,
    trackLabel: base.trackLabel,
    because: focus?.because || base.because,
    profileTip: focus?.profileTip || base.profileTip,
    timeInsight: detail?.change || base.changeDefault,
  };
}

export default function RoleQuiz({
  market,
  category,
  variant,
  light = false,
  phoneDisplay,
  phoneHref,
}: {
  market: MarketId;
  category?: string;
  variant?: AbVariant;
  light?: boolean;
  phoneDisplay?: string;
  phoneHref?: string | null;
}) {
  const enabled = flagEnabled();
  const isAu = market === "au";
  const [frameVariant, setFrameVariant] = useState<ExpVariant>("a");
  const [step, setStep] = useState(0);
  const [started, setStarted] = useState(false);
  const [answers, setAnswers] = useState<Answers>({
    drain: "",
    focus: "",
    detail: "",
  });

  useEffect(() => {
    const v = assignExperiment("quiz_copy");
    setFrameVariant(v);
    trackExperimentView("quiz_copy", v, { surface: "role_quiz", market });
  }, [market]);

  const paths = useMemo(() => pathsFor(market), [market]);
  const frames = isAu ? FRAMES_AU : FRAMES_US;
  const frame = frames[frameVariant] || frames.a;

  const questions = useMemo((): QuizQuestion[] => {
    const drain = answers.drain && isDrainKey(answers.drain) ? answers.drain : null;
    const path = drain ? paths[drain] : null;
    return [
      drainQuestion(market),
      {
        key: "focus",
        q: path?.focusQ || "What’s the biggest drag?",
        options: path?.focusOptions || [],
      },
      {
        key: "detail",
        q: path?.detailQ || "What would help most?",
        options: path?.detailOptions || [],
      },
    ];
  }, [answers.drain, paths, market, isAu]);

  const result = useMemo(() => {
    if (step < 3) return null;
    return buildResult(answers, market);
  }, [answers, market, step]);

  if (!enabled) return null;

  const usPhoneFallback =
    market === "us"
      ? { display: SITE.usPhoneDisplay, href: SITE.usPhoneHref }
      : null;
  const callDisplay = phoneDisplay || usPhoneFallback?.display;
  const callHref = phoneHref || usPhoneFallback?.href || null;
  const canCall = Boolean(callHref && callDisplay);

  const track = (event: string, extra: Record<string, string> = {}) => {
    trackEvent(event, {
      market,
      category: category || "",
      variant: variant || "",
      assist_type: "role_quiz",
      experiment_variant: frameVariant,
      ...extra,
    });
  };

  const current = questions[step];
  const note = isAu
    ? "A starting point, not a promise. Next: a short chat so we can shortlist real people for your Australian business — free, no pressure."
    : "A starting point, not a promise. Next: a short chat so we can shortlist real people for you.";

  return (
    <section
      id="role-quiz"
      className={`role-quiz${light ? " role-quiz-light" : ""}`}
      aria-labelledby="role-quiz-title"
      data-exp-quiz={frameVariant}
    >
      <div className="role-quiz-inner">
        <p className="role-quiz-eyebrow">{frame.eyebrow}</p>
        <h2 id="role-quiz-title">{frame.title}</h2>
        <p className="role-quiz-lead">{frame.lead}</p>

        {step < 3 && current ? (
          <div className="role-quiz-card">
            <div className="role-quiz-progress" aria-hidden>
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className={`role-quiz-dot${i <= step ? " is-on" : ""}`}
                />
              ))}
            </div>
            <p className="role-quiz-step">Question {step + 1} of 3</p>
            <h3>{current.q}</h3>
            <div className="role-quiz-options">
              {current.options.map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => {
                    if (!started) {
                      setStarted(true);
                      track("quiz_started", { step: "1" });
                      trackExperimentClick("quiz_copy", frameVariant, {
                        market,
                        cta: "quiz_start",
                      });
                    }
                    const nextAnswers: Answers = { ...answers };
                    if (current.key === "drain" && isDrainKey(opt.id)) {
                      nextAnswers.drain = opt.id;
                      nextAnswers.focus = "";
                      nextAnswers.detail = "";
                    } else if (current.key === "focus") {
                      nextAnswers.focus = opt.id;
                    } else {
                      nextAnswers.detail = opt.id;
                    }
                    setAnswers(nextAnswers);
                    const nextStep = step + 1;
                    setStep(nextStep);
                    track("quiz_step", {
                      step: String(nextStep),
                      answer: opt.id,
                      drain: nextAnswers.drain || "",
                    });
                    if (nextStep === 3) {
                      const r = buildResult(nextAnswers, market);
                      track("quiz_completed", {
                        result: r?.trackLabel || "",
                        drain: nextAnswers.drain || "",
                        focus: nextAnswers.focus || "",
                        detail: nextAnswers.detail || "",
                      });
                      trackEvent("lead_magnet_completed", {
                        market,
                        category: category || "",
                        variant: variant || "",
                        magnet: "role_quiz",
                        result_role: r?.trackLabel || "",
                        experiment_variant: frameVariant,
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
          <div className="role-quiz-result" role="status">
            <p className="role-quiz-result-kicker">
              <span className="role-quiz-ding" aria-hidden>
                ★
              </span>
              {frame.kicker}
            </p>
            <h3 className="role-quiz-win">{result.roleLabel}</h3>
            <p className="role-quiz-personalized">{result.because}</p>

            <div className="role-quiz-reward">
              <div className="role-quiz-reward-card">
                <span>{frame.whoLabel}</span>
                <p>{result.profileTip}</p>
              </div>
              <div className="role-quiz-reward-card">
                <span>{frame.timeLabel}</span>
                <p>{result.timeInsight}</p>
              </div>
            </div>

            <div className="role-quiz-actions">
              <a
                href="#gate"
                className="role-quiz-primary"
                onClick={(e) => {
                  e.preventDefault();
                  track("conversion_assist_cta_clicked", {
                    cta: "form",
                    result_role: result.trackLabel,
                    form_role: result.formRole,
                  });
                  trackExperimentClick("quiz_copy", frameVariant, {
                    market,
                    cta: "form",
                  });
                  // Skip “who are you?” — quiz completers are employers.
                  // Preselect the recommended role chip on the hire form.
                  focusGate({
                    behavior: "smooth",
                    selectEmployer: true,
                    role: result.formRole,
                    emphasize: "role",
                  });
                }}
              >
                {isAu ? "Chat about this role →" : "Hire for this role →"}
              </a>
              {canCall ? (
                <a
                  href={callHref!}
                  className="role-quiz-call"
                  onClick={() => {
                    trackPhoneClick({
                      market,
                      category: category || "",
                      variant: variant || "",
                      assist_type: "role_quiz",
                      cta: "phone",
                      result_role: result.trackLabel,
                    });
                    trackExperimentClick("quiz_copy", frameVariant, {
                      market,
                      cta: "phone",
                    });
                    trackExperimentConvert("phone_click", {
                      market,
                      source: "role_quiz",
                    });
                  }}
                >
                  Call {callDisplay}
                </a>
              ) : null}
              <button
                type="button"
                className="role-quiz-ghost"
                onClick={() => {
                  setStep(0);
                  setStarted(false);
                  setAnswers({ drain: "", focus: "", detail: "" });
                  track("quiz_retake");
                }}
              >
                Retake
              </button>
            </div>
            <p className="role-quiz-note">{note}</p>
          </div>
        ) : null}
      </div>
    </section>
  );
}
