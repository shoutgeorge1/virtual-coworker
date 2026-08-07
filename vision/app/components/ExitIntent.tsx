"use client";

import { useEffect, useState } from "react";
import { trackEvent } from "../../lib/tracking";
import type { MarketId } from "../../config/markets";
import type { AbVariant } from "../../config/categories";

const SESSION_KEY = "vc_exit_intent_seen";
const VARIANT_KEY = "vc_exit_popup_variant";

type PopupVariantId = "a" | "b" | "c";

type PopupVariant = {
  id: PopupVariantId;
  image: string;
  eyebrow: string;
  title: string;
  body: string;
  primaryCta: string;
  phoneCta: string;
};

const VARIANTS: PopupVariant[] = [
  {
    id: "a",
    image: "/brand/va-face-1.jpg",
    eyebrow: "Hire Filipino VA",
    title: "Need a dedicated seat — not Upwork?",
    body: "We recruit and shortlist. You interview who joins. Tell us the role in about a minute.",
    primaryCta: "Tell us who you need →",
    phoneCta: "Call now",
  },
  {
    id: "b",
    image: "/brand/va-face-2.jpg",
    eyebrow: "Dedicated Filipino teammate",
    title: "You interview. We handle the shortlist.",
    body: "Not a freelance marketplace — a staffing partner for a dedicated seat on your hours.",
    primaryCta: "Start hiring →",
    phoneCta: "Talk to us",
  },
  {
    id: "c",
    image: "/brand/va-face-3.jpg",
    eyebrow: "Skip the gig maze",
    title: "Hire a Filipino VA your way.",
    body: "Dedicated seat, vetted shortlist, you decide. Prefer to talk? Call — or send the role.",
    primaryCta: "Send the role →",
    phoneCta: "Call the team",
  },
];

function pickVariant(): PopupVariant {
  if (typeof window === "undefined") return VARIANTS[0];
  try {
    const stored = localStorage.getItem(VARIANT_KEY) as PopupVariantId | null;
    const found = VARIANTS.find((v) => v.id === stored);
    if (found) return found;
  } catch {
    /* ignore */
  }
  const picked = VARIANTS[Math.floor(Math.random() * VARIANTS.length)];
  try {
    localStorage.setItem(VARIANT_KEY, picked.id);
    document.cookie = `${VARIANT_KEY}=${picked.id};path=/;max-age=${60 * 60 * 24 * 90};samesite=lax`;
  } catch {
    /* ignore */
  }
  return picked;
}

function flagEnabled(): boolean {
  const raw = (process.env.NEXT_PUBLIC_ENABLE_EXIT_INTENT || "").trim().toLowerCase();
  return raw !== "false";
}

/**
 * Exit-intent OR timed nudge — 3 creative A/B/C variants (image + copy).
 * Employer microsites only. Persist variant in localStorage/cookie. Track dataLayer.
 */
export default function ExitIntent({
  market,
  gateHref = "#gate",
  category,
  variant,
  phoneHref,
  phoneDisplay,
}: {
  market: MarketId;
  gateHref?: string;
  category?: string;
  variant?: AbVariant;
  phoneHref?: string | null;
  phoneDisplay?: string;
}) {
  const [open, setOpen] = useState(false);
  const [popup, setPopup] = useState<PopupVariant>(VARIANTS[0]);
  const enabled = flagEnabled();

  useEffect(() => {
    if (!enabled) return;
    if (typeof window === "undefined") return;
    const assigned = pickVariant();
    setPopup(assigned);

    try {
      if (sessionStorage.getItem(SESSION_KEY) === "1") return;
    } catch {
      /* ignore */
    }

    let shown = false;
    let formTouched = false;

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
      // Don't stack on someone already filling the form
      if (formBusy()) return;
      shown = true;
      try {
        sessionStorage.setItem(SESSION_KEY, "1");
      } catch {
        /* ignore */
      }
      setOpen(true);
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

    const onLeave = (e: MouseEvent) => {
      if (e.clientY <= 8) show("exit_intent");
    };

    const timer = window.setTimeout(() => show("timed_45s"), 45_000);
    document.addEventListener("mouseout", onLeave);
    document.addEventListener("focusin", onFormInteract, true);
    document.addEventListener("input", onFormInteract, true);

    return () => {
      window.clearTimeout(timer);
      document.removeEventListener("mouseout", onLeave);
      document.removeEventListener("focusin", onFormInteract, true);
      document.removeEventListener("input", onFormInteract, true);
    };
  }, [enabled, market, category, variant]);

  if (!enabled || !open) return null;

  const dismiss = () => setOpen(false);
  const showPhone = Boolean(phoneHref && phoneDisplay);

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
        <div className="exit-intent-actions">
          <a
            href={gateHref}
            className="exit-intent-primary"
            onClick={() => {
              trackEvent("conversion_assist_cta_clicked", {
                market,
                category: category || "",
                variant: variant || "",
                assist_type: "exit_intent",
                popup_variant: popup.id,
                cta: "form",
              });
              trackEvent("exit_intent_accepted", {
                market,
                category: category || "",
                variant: variant || "",
                popup_variant: popup.id,
              });
              dismiss();
            }}
          >
            {popup.primaryCta}
          </a>
          {showPhone ? (
            <a
              href={phoneHref!}
              className="exit-intent-phone"
              onClick={() => {
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
              ☎ {popup.phoneCta}
            </a>
          ) : null}
          <button type="button" className="exit-intent-ghost" onClick={dismiss}>
            Not now
          </button>
        </div>
        <p className="exit-intent-jobseeker">
          Looking for work? Use Looking for a job? in the footer.
        </p>
      </div>
    </div>
  );
}
