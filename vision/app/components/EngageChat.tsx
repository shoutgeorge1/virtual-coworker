"use client";

import { useEffect, useRef, useState, type MouseEvent } from "react";
import { trackEvent } from "../../lib/tracking";
import { focusGate } from "../../lib/focus-gate";
import {
  assignExperiment,
  trackExperimentClick,
  trackExperimentConvert,
  trackExperimentView,
  type ExpVariant,
} from "../../lib/experiments";
import type { MarketId } from "../../config/markets";
import type { AbVariant } from "../../config/categories";

const LAUNCHER: Record<ExpVariant, string> = {
  a: "Need help hiring?",
  b: "Ask a quick question",
  c: "Need help hiring?", // unused — chat_launcher is A/B only
};

type StepId = "open" | "role" | "path" | "done";

const FACES = ["/brand/va-face-1.jpg", "/brand/va-face-2.jpg", "/brand/va-face-3.jpg"] as const;
const FACE_KEY = "vc_chat_face";

function flagEnabled(): boolean {
  const raw = (process.env.NEXT_PUBLIC_ENABLE_CHAT || "").trim().toLowerCase();
  return raw !== "false";
}

function pickFace(): string {
  if (typeof window === "undefined") return FACES[0];
  try {
    const stored = localStorage.getItem(FACE_KEY);
    if (stored && (FACES as readonly string[]).includes(stored)) return stored;
  } catch {
    /* ignore */
  }
  const face = FACES[Math.floor(Math.random() * FACES.length)];
  try {
    localStorage.setItem(FACE_KEY, face);
  } catch {
    /* ignore */
  }
  return face;
}

/**
 * Lightweight scripted chat — opt-in launcher only (never auto-opens).
 * Not live AI. Employer LPs only. Exit-intent popup stays separate.
 */
export default function EngageChat({
  market,
  category,
  variant,
  phoneHref,
  phoneDisplay,
  gateHref = "#gate",
  careersHref,
}: {
  market: MarketId;
  category?: string;
  variant?: AbVariant;
  phoneHref?: string | null;
  phoneDisplay?: string;
  gateHref?: string;
  careersHref: string;
}) {
  // Opt-in only — do not auto-open (avoids stacking on exit popup)
  const [open, setOpen] = useState(false);
  const [nudge, setNudge] = useState(true);
  const [step, setStep] = useState<StepId>("open");
  const [roleHint, setRoleHint] = useState("");
  const [face, setFace] = useState<string>(FACES[0]);
  const [launcherVariant, setLauncherVariant] = useState<ExpVariant>("a");
  const panelRef = useRef<HTMLDivElement>(null);
  const enabled = flagEnabled();
  const showPhone = Boolean(phoneHref && phoneDisplay);

  useEffect(() => {
    if (!enabled) return;
    setFace(pickFace());
    const v = assignExperiment("chat_launcher");
    setLauncherVariant(v);
    trackExperimentView("chat_launcher", v, { market });
    const t = window.setTimeout(() => setNudge(false), 4500);
    return () => window.clearTimeout(t);
  }, [enabled, market]);

  useEffect(() => {
    if (!open) return;
    setNudge(false);
    panelRef.current?.focus();
  }, [open]);

  if (!enabled) return null;

  const track = (event: string, extra: Record<string, string | boolean> = {}) => {
    trackEvent(event, {
      market,
      category: category || "",
      variant: variant || "",
      assist_type: "chat",
      ...extra,
    });
  };

  const toggle = () => {
    const next = !open;
    setOpen(next);
    if (next) {
      trackExperimentClick("chat_launcher", launcherVariant, {
        market,
        cta: "open",
      });
      track("conversion_assist_opened", { reason: "chat_open" });
      trackEvent("chat_opened", {
        market,
        category: category || "",
        variant: variant || "",
      });
    }
  };

  const launcherLabel = LAUNCHER[launcherVariant] || LAUNCHER.a;

  return (
    <div className="engage-chat">
      {open ? (
        <div
          className="engage-chat-panel"
          role="dialog"
          aria-label="Hiring help"
          tabIndex={-1}
          ref={panelRef}
        >
          <header className="engage-chat-head">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={face} alt="" width={40} height={40} loading="lazy" decoding="async" />
            <div>
              <strong>Hiring help</strong>
              <span>Virtual Coworker · quick answers</span>
            </div>
            <button type="button" className="engage-chat-close" onClick={toggle} aria-label="Close">
              ×
            </button>
          </header>

          <div className="engage-chat-body">
            {step === "open" ? (
              <>
                <p className="engage-chat-bubble">
                  Hi — are you hiring staff for a business, or looking for a job?
                </p>
                <div className="engage-chat-choices">
                  <button
                    type="button"
                    onClick={() => {
                      setStep("role");
                      track("chat_step", { step: "employer" });
                    }}
                  >
                    I’m hiring for a business
                  </button>
                  <a
                    href={careersHref}
                    {...(/^https?:\/\//i.test(careersHref)
                      ? { target: "_blank", rel: "noopener noreferrer" }
                      : {})}
                    onClick={() =>
                      trackEvent("job_seeker_redirected", {
                        market,
                        category: category || "",
                        variant: variant || "",
                        destination: careersHref,
                        source: "chat",
                        primary_eligible: false,
                      })
                    }
                  >
                    I’m looking for a job →
                  </a>
                </div>
              </>
            ) : null}

            {step === "role" ? (
              <>
                <p className="engage-chat-bubble">
                  Got it. What kind of help do you need most right now?
                </p>
                <div className="engage-chat-choices">
                  {[
                    "Virtual assistant / admin",
                    "Marketing or social",
                    "Books / accounting",
                    "Customer support",
                    "Something else",
                  ].map((label) => (
                    <button
                      key={label}
                      type="button"
                      onClick={() => {
                        setRoleHint(label);
                        setStep("path");
                        track("chat_step", { step: "role", role_hint: label });
                      }}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </>
            ) : null}

            {step === "path" ? (
              <>
                <p className="engage-chat-bubble">
                  {roleHint
                    ? `Thanks — ${roleHint.toLowerCase()} is a common first hire.`
                    : "Thanks."}{" "}
                  Fastest next step: {showPhone ? "call us, or " : ""}
                  tell us the role on the form (about a minute).
                </p>
                <div className="engage-chat-choices">
                  {showPhone ? (
                    <a
                      href={phoneHref!}
                      className="engage-chat-primary"
                      onClick={() => {
                        track("conversion_assist_cta_clicked", { cta: "phone" });
                        trackExperimentConvert("phone_click", {
                          market,
                          source: "chat",
                        });
                        trackEvent("phone_cta_clicked", {
                          market,
                          category: category || "",
                          variant: variant || "",
                          source: "chat",
                        });
                        setStep("done");
                      }}
                    >
                      ☎ Call {phoneDisplay}
                    </a>
                  ) : null}
                  <a
                    href={gateHref}
                    className={showPhone ? "" : "engage-chat-primary"}
                    onClick={(e: MouseEvent<HTMLAnchorElement>) => {
                      e.preventDefault();
                      track("conversion_assist_cta_clicked", { cta: "form" });
                      setStep("done");
                      setOpen(false);
                      window.setTimeout(
                        () =>
                          focusGate({
                            behavior: "smooth",
                            selectEmployer: true,
                            emphasize: "role",
                          }),
                        40,
                      );
                    }}
                  >
                    Start Hiring
                  </a>
                </div>
              </>
            ) : null}

            {step === "done" ? (
              <p className="engage-chat-bubble">
                Perfect — we’re ready when you are.
              </p>
            ) : null}
          </div>
        </div>
      ) : null}

      <button
        type="button"
        className={`engage-chat-launcher${nudge && !open ? " engage-chat-launcher-nudge" : ""}`}
        onClick={toggle}
        aria-expanded={open}
        aria-label={open ? "Close hiring help" : "Open hiring help"}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={face} alt="" width={28} height={28} loading="lazy" decoding="async" />
        <span>{open ? "Close" : launcherLabel}</span>
      </button>
    </div>
  );
}
