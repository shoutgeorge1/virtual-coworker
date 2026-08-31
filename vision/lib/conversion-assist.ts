/**
 * Absorb-first conversion assist for short money LPs.
 *
 * Hierarchy:
 *   Stage 1–2 — clean primary (phone / employer form / book)
 *   Stage 3–4 — observe engagement; detect non-conversion
 *   Stage 5 — recover (chat / quiz / popup)
 *   Stage 6 — suppress after primary success
 *
 * Chat launcher and exit popup: on hold 2026-08-14 (obscure LP, especially mobile).
 * Flags default off. A/B vs clean LP later. Must not fire immediately or stack if remounted.
 */

export const CONVERSION_ASSIST = {
  /** Min dwell before exit-intent may fire (desktop). */
  absorbMs: 30_000,
  /** Chat launcher dwell on desktop (or chat scroll). */
  chatRevealMs: 45_000,
  /** Chat launcher dwell on mobile — sticky already covers form/phone. */
  chatRevealMobileMs: 60_000,
  /** Timed exit fallback if no leave / scroll trigger. */
  timedExitMs: 45_000,
  /** Scroll depth (0–1) that can allow exit assist. */
  scrollDepth: 0.32,
  /** Deeper scroll required before chat launcher may appear. */
  chatScrollDepth: 0.55,
} as const;

export const EXIT_SESSION_KEY = "vc_exit_intent_seen";
export const CHAT_ENGAGED_KEY = "vc_chat_engaged";
/** Session flag: visitor completed a primary conversion — suppress secondary. */
export const PRIMARY_CONVERTED_KEY = "vc_primary_converted";
/** Session flag: visitor started the employer form — protect completion. */
export const FORM_STARTED_KEY = "vc_form_started";

export type AssistKind = "exit" | "chat";

export function readSessionFlag(key: string): boolean {
  if (typeof window === "undefined") return false;
  try {
    return sessionStorage.getItem(key) === "1";
  } catch {
    return false;
  }
}

export function writeSessionFlag(key: string): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(key, "1");
  } catch {
    /* ignore */
  }
}

export function markAssistEngaged(kind: AssistKind): void {
  writeSessionFlag(kind === "exit" ? EXIT_SESSION_KEY : CHAT_ENGAGED_KEY);
}

export function wasExitShown(): boolean {
  return readSessionFlag(EXIT_SESSION_KEY);
}

export function wasChatEngaged(): boolean {
  return readSessionFlag(CHAT_ENGAGED_KEY);
}

/** Call after form submit, meaningful phone CTA, or booked consultation. */
export function markPrimaryConverted(reason = "primary"): void {
  writeSessionFlag(PRIMARY_CONVERTED_KEY);
  if (typeof document !== "undefined") {
    document.documentElement?.classList?.add("vc-primary-converted");
    if (document.documentElement?.dataset) {
      document.documentElement.dataset.vcPrimaryReason = reason;
    }
  }
}

export function wasPrimaryConverted(): boolean {
  return readSessionFlag(PRIMARY_CONVERTED_KEY);
}

export function markFormStarted(): void {
  writeSessionFlag(FORM_STARTED_KEY);
  if (typeof document !== "undefined") {
    document.documentElement.classList.add("vc-form-started");
  }
}

export function wasFormStarted(): boolean {
  return readSessionFlag(FORM_STARTED_KEY);
}

export function isFormBusy(): boolean {
  if (typeof document === "undefined") return false;
  const el = document.activeElement;
  if (!el || !(el instanceof HTMLElement)) return false;
  return Boolean(el.closest("#gate, .gate-card, form"));
}

/** True when secondary widgets must stay quiet. */
export function shouldSuppressSecondaryAssist(): boolean {
  if (wasPrimaryConverted()) return true;
  if (isFormBusy()) return true;
  return false;
}

/** Form is being filled — park chat without permanently killing recovery. */
export function setFormBusyClass(busy: boolean): void {
  if (typeof document === "undefined") return;
  document.documentElement.classList.toggle("vc-form-busy", busy);
}

export function isChatPanelOpen(): boolean {
  if (typeof document === "undefined") return false;
  return Boolean(document.querySelector(".engage-chat-panel"));
}

export function isAssistPopupOpen(): boolean {
  if (typeof document === "undefined") return false;
  return document.documentElement.classList.contains("vc-popup-open");
}

export function pageScrollDepth(): number {
  if (typeof window === "undefined") return 0;
  const doc = document.documentElement;
  const scrollable = doc.scrollHeight - window.innerHeight;
  if (scrollable < 160) return 1;
  return window.scrollY / scrollable;
}

export function hasReachedScrollAssist(): boolean {
  return pageScrollDepth() >= CONVERSION_ASSIST.scrollDepth;
}

export function hasReachedChatScrollAssist(): boolean {
  return pageScrollDepth() >= CONVERSION_ASSIST.chatScrollDepth;
}

export function isCoarsePointer(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return window.matchMedia("(pointer: coarse)").matches || window.innerWidth < 760;
  } catch {
    return window.innerWidth < 760;
  }
}

/** Dwell before the chat launcher may appear (mobile gets more absorb time). */
export function chatRevealDelayMs(): number {
  return isCoarsePointer()
    ? CONVERSION_ASSIST.chatRevealMobileMs
    : CONVERSION_ASSIST.chatRevealMs;
}
