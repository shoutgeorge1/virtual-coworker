"use client";

import { useEffect, useRef, useState, type MouseEvent } from "react";
import { trackEvent } from "../../lib/tracking";
import { exitToCareers } from "../../lib/job-seeker-exit";
import { focusGate } from "../../lib/focus-gate";
import {
  chatRevealDelayMs,
  hasReachedChatScrollAssist,
  isAssistPopupOpen,
  markAssistEngaged,
  setFormBusyClass,
  shouldSuppressSecondaryAssist,
  wasPrimaryConverted,
} from "../../lib/conversion-assist";
import {
  assignExperiment,
  trackExperimentClick,
  trackExperimentConvert,
  trackExperimentView,
  type ExpVariant,
} from "../../lib/experiments";
import type { MarketId } from "../../config/markets";
import type { AbVariant } from "../../config/categories";
import { primaryHireCta } from "../../config/employer-cro";

const LAUNCHER: Record<ExpVariant, string> = {
  a: "Chat with us",
  b: "Chat - hiring help",
  c: "Chat with us", // unused - chat_launcher is A/B only
};

type StepId = "open" | "role" | "path" | "done";

const FACES = ["/brand/va-face-1.jpg", "/brand/va-face-2.jpg", "/brand/va-face-3.jpg"] as const;
const FACE_KEY = "vc_chat_face";

/** Off unless explicitly true. Hold 2026-08-14 — obscures LP, especially mobile. A/B later. */
function flagEnabled(): boolean {
  const raw = (process.env.NEXT_PUBLIC_ENABLE_CHAT || "").trim().toLowerCase();
  return raw === "true";
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
 * Lightweight scripted chat - opt-in launcher only (never auto-opens).
 * Hold 2026-08-14: off unless NEXT_PUBLIC_ENABLE_CHAT=true. A/B later.
 * CTAs → form (#gate) or phone only. Exit popup stays separate (coordinated).
 */
export default function EngageChat({
  market,
  category,
  variant,
  phoneHref,
  phoneDisplay,
  gateHref = "#gate",
  careersHref,
  skipIntentGate = false,
}: {
  market: MarketId;
  category?: string;
  variant?: AbVariant;
  phoneHref?: string | null;
  phoneDisplay?: string;
  gateHref?: string;
  careersHref: string;
  /** Ungated employer LPs: skip hire vs job-seeker first step. */
  skipIntentGate?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const [nudge, setNudge] = useState(false);
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
  }, [enabled, market]);

  // Absorb first — do not paint the launcher on load. Never auto-opens the panel.
  // Never reveal while the employer form is active or after a primary conversion.
  useEffect(() => {
    if (!enabled) return;
    if (wasPrimaryConverted()) return;
    let shown = false;
    let cancelled = false;
    let retryTimer: number | undefined;
    let impressionFired = false;

    const reveal = () => {
      if (cancelled || shown) return;
      if (shouldSuppressSecondaryAssist()) return;
      if (isAssistPopupOpen()) {
        retryTimer = window.setTimeout(reveal, 1200);
        return;
      }
      shown = true;
      setRevealed(true);
      if (!impressionFired) {
        impressionFired = true;
        trackEvent("chat_widget_impression", {
          market,
          category: category || "",
          variant: variant || "",
          widget_version: "engage_chat_v1",
        });
      }
      setNudge(true);
      window.setTimeout(() => {
        if (!cancelled) setNudge(false);
      }, 4500);
    };

    const onScroll = () => {
      if (shouldSuppressSecondaryAssist()) return;
      if (hasReachedChatScrollAssist()) reveal();
    };

    const timer = window.setTimeout(reveal, chatRevealDelayMs());
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
      if (retryTimer !== undefined) window.clearTimeout(retryTimer);
      window.removeEventListener("scroll", onScroll);
    };
  }, [enabled, market, category, variant]);

  // Park launcher while form fields are focused / after primary convert.
  useEffect(() => {
    if (!enabled) return;

    const syncBusy = () => {
      const formFocus =
        document.activeElement instanceof HTMLElement &&
        Boolean(document.activeElement.closest("#gate, .gate-card, form"));
      setFormBusyClass(formFocus);
      if (wasPrimaryConverted()) {
        setOpen(false);
        setRevealed(false);
        return;
      }
      if (formFocus) setOpen(false);
    };
    document.addEventListener("focusin", syncBusy, true);
    document.addEventListener("focusout", syncBusy, true);
    document.addEventListener("input", syncBusy, true);
    window.addEventListener("vc-primary-converted", syncBusy);
    return () => {
      document.removeEventListener("focusin", syncBusy, true);
      document.removeEventListener("focusout", syncBusy, true);
      document.removeEventListener("input", syncBusy, true);
      window.removeEventListener("vc-primary-converted", syncBusy);
      setFormBusyClass(false);
    };
  }, [enabled]);

  useEffect(() => {
    if (!open) return;
    setNudge(false);
    panelRef.current?.focus();
  }, [open]);

  if (!enabled || !revealed) return null;

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
      markAssistEngaged("chat");
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
      trackEvent("chat_widget_open", {
        market,
        category: category || "",
        variant: variant || "",
        widget_version: "engage_chat_v1",
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
          aria-label="Hiring chat"
          tabIndex={-1}
          ref={panelRef}
        >
          <header className="engage-chat-head">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={face} alt="" width={40} height={40} loading="lazy" decoding="async" />
            <div>
              <strong>Chat</strong>
              <span>Quick answers · not a live agent</span>
            </div>
            <button type="button" className="engage-chat-close" onClick={toggle} aria-label="Close">
              ×
            </button>
          </header>

          <div className="engage-chat-body">
            {skipIntentGate && step === "open" ? (
              <>
                <p className="engage-chat-bubble">
                  The hiring form is on this page. Book a free strategy call when
                  you’re ready.
                </p>
                <div className="engage-chat-choices">
                  <a
                    href={gateHref}
                    className="engage-chat-primary"
                    onClick={(e: MouseEvent<HTMLAnchorElement>) => {
                      e.preventDefault();
                      track("conversion_assist_cta_clicked", { cta: "form" });
                      setStep("done");
                      setOpen(false);
                      window.setTimeout(
                        () => focusGate({ behavior: "smooth" }),
                        40,
                      );
                    }}
                  >
                    {primaryHireCta(market)}
                  </a>
                </div>
                <p className="engage-chat-careers">
                  <a
                    href={careersHref}
                    onClick={(e) => {
                      e.preventDefault();
                      exitToCareers(careersHref, {
                        market,
                        category: category || "",
                        variant: variant || "",
                        source: "chat_ungated_link",
                      });
                    }}
                  >
                    Looking for work? Visit our Philippines careers site.
                  </a>
                </p>
              </>
            ) : null}

            {!skipIntentGate && step === "open" ? (
              <>
                <p className="engage-chat-bubble">
                  Hi - are you hiring staff for a business, or looking for a job?
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
                    onClick={(e) => {
                      e.preventDefault();
                      exitToCareers(careersHref, {
                        market,
                        category: category || "",
                        variant: variant || "",
                        source: "chat",
                      });
                    }}
                  >
                    I’m looking for a job →
                  </a>
                </div>
              </>
            ) : null}

            {!skipIntentGate && step === "role" ? (
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

            {!skipIntentGate && step === "path" ? (
              <>
                <p className="engage-chat-bubble">
                  {roleHint
                    ? `Thanks - ${roleHint.toLowerCase()} is a common first hire.`
                    : "Thanks."}{" "}
                  {market === "au"
                    ? `Fastest next step: ${showPhone ? "give us a call, or " : ""}tell us the role on the form (about a minute).`
                    : `Fastest next step: ${showPhone ? "call us, or " : ""}tell us the role on the form (about a minute).`}
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
                            selectEmployer: skipIntentGate ? false : true,
                            emphasize: skipIntentGate ? undefined : "role",
                          }),
                        40,
                      );
                    }}
                  >
                    {market === "au" ? "Book a free strategy call" : "Book a Free Strategy Call"}
                  </a>
                </div>
              </>
            ) : null}

            {step === "done" ? (
              <p className="engage-chat-bubble">
                {market === "au"
                  ? "Got it - have a chat when it suits. Obligation free, at no cost."
                  : "Got it - talk to a specialist when you like. Obligation free, at no cost."}
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
        aria-label={open ? "Close chat" : "Open chat"}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={face} alt="" width={28} height={28} loading="lazy" decoding="async" />
        <span>{open ? "Close" : launcherLabel}</span>
      </button>
    </div>
  );
}
