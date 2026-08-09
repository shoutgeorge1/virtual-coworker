"use client";

import { useEffect, useState } from "react";
import { trackEvent } from "../../lib/tracking";
import { focusGate } from "../../lib/focus-gate";
import {
  assignExperiment,
  trackExperimentClick,
  trackExperimentConvert,
  trackExperimentView,
  type ExpVariant,
} from "../../lib/experiments";
import { DEFAULT_CAREERS_URL } from "../../config/markets";
import type { MarketId } from "../../config/markets";
import type { AbVariant } from "../../config/categories";

const SESSION_KEY = "vc_exit_intent_seen";

type PopupVariant = {
  id: ExpVariant;
  image: string;
  eyebrow: string;
  title: string;
  body: string;
  phoneCta: string;
};

/** Shared 2-step choices — copy variants only change the intro. */
const HIRE_CTA = "I’m hiring for a business";
const JOB_CTA = "I’m looking for a job";

const VARIANTS: PopupVariant[] = [
  {
    id: "a",
    image: "/brand/va-face-1.jpg",
    eyebrow: "Skip Upwork roulette",
    title: "Want someone who sticks — not another freelancer?",
    body: "One quick question so we send you the right way.",
    phoneCta: "Call now",
  },
  {
    id: "b",
    image: "/brand/va-face-2.jpg",
    eyebrow: "Dedicated teammate",
    title: "Tired of hiring eating the week?",
    body: "Quick check first — hiring for a company, or looking for work?",
    phoneCta: "Talk to us",
  },
  {
    id: "c",
    image: "/brand/va-face-3.jpg",
    eyebrow: "Filipino VA, your way",
    title: "One clear seat. People you actually meet.",
    body: "Before we point you anywhere — are you hiring, or looking for a job?",
    phoneCta: "Call the team",
  },
];

/**
 * Opt-in only. Auto timed / exit / scroll popups interrupt reading and
 * duplicate the inline employer/job-seeker gate — default OFF (CRO pass 2026-08).
 * Set NEXT_PUBLIC_ENABLE_EXIT_INTENT=true only if deliberately re-enabling.
 */
function flagEnabled(): boolean {
  const raw = (process.env.NEXT_PUBLIC_ENABLE_EXIT_INTENT || "").trim().toLowerCase();
  return raw === "true";
}

function isCoarsePointer(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return window.matchMedia("(pointer: coarse)").matches || window.innerWidth < 760;
  } catch {
    return window.innerWidth < 760;
  }
}

/**
 * Soft offer popup — exit-intent on desktop; scroll-depth or long wait on mobile.
 * Light 2-step gate: hiring vs job seeker → form or PH careers egress.
 * Never immediate. 3 creative A/B/C variants via experiments.ts.
 */
export default function ExitIntent({
  market,
  gateHref = "#gate",
  category,
  variant,
  phoneHref,
  phoneDisplay,
  careersHref = DEFAULT_CAREERS_URL,
}: {
  market: MarketId;
  gateHref?: string;
  category?: string;
  variant?: AbVariant;
  phoneHref?: string | null;
  phoneDisplay?: string;
  careersHref?: string;
}) {
  const [open, setOpen] = useState(false);
  const [popup, setPopup] = useState<PopupVariant>(VARIANTS[0]);
  const enabled = flagEnabled();

  useEffect(() => {
    if (!enabled) return;
    if (typeof window === "undefined") return;
    const assignedId = assignExperiment("exit_popup");
    const assigned = VARIANTS.find((v) => v.id === assignedId) || VARIANTS[0];
    setPopup(assigned);

    try {
      if (sessionStorage.getItem(SESSION_KEY) === "1") return;
    } catch {
      /* ignore */
    }

    let shown = false;
    let formTouched = false;
    const mobile = isCoarsePointer();
    const engagedAt = Date.now();
    const EXIT_MIN_MS = 12_000;
    const TIMED_MS = mobile ? 75_000 : 90_000;
    const SCROLL_DEPTH = 0.5;

    const formBusy = () => {
      if (formTouched) return true;
      const el = document.activeElement;
      if (!el || !(el instanceof HTMLElement)) return false;
      return Boolean(el.closest("#gate, .gate-card, form"));
    };

    const onFormInteract = () => {
      formTouched = true;
    };

    const show = (reason: string) => {
      if (shown) return;
      if (formBusy()) return;
      shown = true;
      try {
        sessionStorage.setItem(SESSION_KEY, "1");
      } catch {
        /* ignore */
      }
      document.documentElement.classList.add("vc-popup-open");
      setOpen(true);
      trackExperimentView("exit_popup", assigned.id, {
        market,
        category: category || "",
        reason,
      });
      trackEvent("conversion_assist_opened", {
        market,
        category: category || "",
        variant: variant || "",
        reason,
        assist_type: "exit_intent",
        popup_variant: assigned.id,
      });
      trackEvent("exit_intent_shown", {
        market,
        category: category || "",
        variant: variant || "",
        reason,
        popup_variant: assigned.id,
      });
    };

    const onLeave = (e: globalThis.MouseEvent) => {
      if (mobile) return;
      if (Date.now() - engagedAt < EXIT_MIN_MS) return;
      if (e.clientY > 8) return;
      show("exit_intent");
    };

    const onScroll = () => {
      const doc = document.documentElement;
      const scrollable = doc.scrollHeight - window.innerHeight;
      if (scrollable < 240) return;
      const depth = window.scrollY / scrollable;
      if (depth >= SCROLL_DEPTH) {
        if (mobile || Date.now() - engagedAt >= EXIT_MIN_MS) {
          show(mobile ? "scroll_50" : "scroll_50_desktop");
        }
      }
    };

    const timer = window.setTimeout(() => show(mobile ? "timed_75s" : "timed_90s"), TIMED_MS);
    if (!mobile) document.addEventListener("mouseout", onLeave);
    window.addEventListener("scroll", onScroll, { passive: true });
    document.addEventListener("focusin", onFormInteract, true);
    document.addEventListener("input", onFormInteract, true);

    return () => {
      window.clearTimeout(timer);
      document.removeEventListener("mouseout", onLeave);
      window.removeEventListener("scroll", onScroll);
      document.removeEventListener("focusin", onFormInteract, true);
      document.removeEventListener("input", onFormInteract, true);
      document.documentElement.classList.remove("vc-popup-open");
    };
  }, [enabled, market, category, variant]);

  useEffect(() => {
    if (!open) document.documentElement.classList.remove("vc-popup-open");
  }, [open]);

  if (!enabled || !open) return null;

  const dismiss = () => {
    document.documentElement.classList.remove("vc-popup-open");
    setOpen(false);
  };
  const showPhone = Boolean(phoneHref && phoneDisplay);
  const careers = careersHref || DEFAULT_CAREERS_URL;

  const acceptHire = () => {
    trackExperimentClick("exit_popup", popup.id, {
      market,
      cta: "hire",
    });
    trackEvent("conversion_assist_cta_clicked", {
      market,
      category: category || "",
      variant: variant || "",
      assist_type: "exit_intent",
      popup_variant: popup.id,
      cta: "hire",
    });
    trackEvent("exit_intent_accepted", {
      market,
      category: category || "",
      variant: variant || "",
      popup_variant: popup.id,
      intent: "employer",
    });
    dismiss();
    window.setTimeout(
      () =>
        focusGate({
          behavior: "smooth",
          selectEmployer: true,
          emphasize: "role",
        }),
      40,
    );
  };

  const acceptJobSeeker = () => {
    trackExperimentClick("exit_popup", popup.id, {
      market,
      cta: "job_seeker",
    });
    trackEvent("job_seeker_redirected", {
      market,
      category: category || "",
      variant: variant || "",
      gate_variant: "exit_intent",
      intent: "job_seeker",
      destination: careers,
      primary_eligible: false,
      popup_variant: popup.id,
    });
    dismiss();
    window.open(careers, "_blank", "noopener,noreferrer");
  };

  return (
    <div
      className="exit-intent"
      role="dialog"
      aria-modal="true"
      aria-labelledby="exit-intent-title"
    >
      <button
        type="button"
        className="exit-intent-scrim"
        aria-label="Close"
        onClick={dismiss}
      />
      <div className="exit-intent-card exit-intent-card-media">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          className="exit-intent-face"
          src={popup.image}
          alt=""
          width={96}
          height={96}
          loading="lazy"
          decoding="async"
        />
        <p className="exit-intent-eyebrow">{popup.eyebrow}</p>
        <h2 id="exit-intent-title">{popup.title}</h2>
        <p>{popup.body}</p>
        <div className="exit-intent-choices" role="group" aria-label="Are you hiring or looking for a job?">
          <button type="button" className="exit-intent-primary" onClick={acceptHire}>
            {HIRE_CTA}
          </button>
          <button type="button" className="exit-intent-secondary" onClick={acceptJobSeeker}>
            {JOB_CTA}
          </button>
        </div>
        <div className="exit-intent-actions">
          {showPhone ? (
            <a
              href={phoneHref!}
              className="exit-intent-phone"
              onClick={() => {
                trackExperimentClick("exit_popup", popup.id, {
                  market,
                  cta: "phone",
                });
                trackExperimentConvert("phone_click", {
                  market,
                  source: "exit_intent",
                });
                trackEvent("conversion_assist_cta_clicked", {
                  market,
                  category: category || "",
                  variant: variant || "",
                  assist_type: "exit_intent",
                  popup_variant: popup.id,
                  cta: "phone",
                });
                trackEvent("phone_cta_clicked", {
                  market,
                  category: category || "",
                  variant: variant || "",
                  source: "exit_intent",
                });
              }}
            >
              ☎ {market === "au" ? "Give us a call" : popup.phoneCta}
            </a>
          ) : null}
          <button type="button" className="exit-intent-ghost" onClick={dismiss}>
            Not now
          </button>
        </div>
        {/* gateHref kept for a11y / hash parity; hire CTA scrolls via focusGate */}
        <a href={gateHref} className="sr-only" onClick={(e) => { e.preventDefault(); acceptHire(); }}>
          Go to hiring form
        </a>
      </div>
    </div>
  );
}
