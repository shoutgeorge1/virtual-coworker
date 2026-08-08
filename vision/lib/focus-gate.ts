/**
 * Scroll to #gate, flash the card, and focus the first actionable field
 * so popup / sticky / chat CTAs feel like something actually happened.
 */

export type FocusGateOpts = {
  behavior?: ScrollBehavior;
  /** Pre-select employer path in LeadGate (skip “who are you?” vague state). */
  selectEmployer?: boolean;
  /** Pre-select a role chip (must match a LeadGate `copy.roles` label). */
  role?: string;
  /** Land attention on role chips (“What do you need help with?”). */
  emphasize?: "role" | "intent";
};

export type GateAssistDetail = {
  intent?: "employer";
  /** Form role label to preselect (e.g. "Bookkeeping support"). */
  role?: string;
  emphasize?: "role" | "intent";
};

export const GATE_ASSIST_EVENT = "vc:gate-assist";

export function focusGate(opts?: FocusGateOpts): void {
  if (typeof document === "undefined") return;
  const gate = document.getElementById("gate");
  if (!gate) return;

  const behavior = opts?.behavior ?? "smooth";
  const selectEmployer = Boolean(opts?.selectEmployer);
  const role = opts?.role?.trim() || undefined;
  const emphasize =
    opts?.emphasize ?? (selectEmployer || role ? "role" : undefined);

  if (selectEmployer || emphasize || role) {
    const detail: GateAssistDetail = {
      intent: selectEmployer ? "employer" : undefined,
      role,
      emphasize,
    };
    window.dispatchEvent(new CustomEvent(GATE_ASSIST_EVENT, { detail }));
  }

  gate.scrollIntoView({ behavior, block: "start" });
  gate.classList.remove("is-gate-focus", "is-gate-focus-strong");
  // Restart CSS animation if already flashing
  void gate.offsetWidth;
  gate.classList.add("is-gate-focus");
  if (selectEmployer || emphasize === "role") {
    gate.classList.add("is-gate-focus-strong");
  }
  window.setTimeout(() => {
    gate.classList.remove("is-gate-focus", "is-gate-focus-strong");
  }, 2200);

  const preferSelector =
    emphasize === "role"
      ? '.gate-chips button, [data-gate-role-step] button, .gate-chips'
      : selectEmployer
        ? '.gate-chips button, .gate-intent button.on, input:not([type="hidden"]):not([disabled])'
        : 'input:not([type="hidden"]):not([disabled]), textarea:not([disabled]), .gate-intent button, .gate-chips button';

  const prefer =
    (gate.querySelector(preferSelector) as HTMLElement | null) ||
    (gate.querySelector("button, a, input, textarea") as HTMLElement | null);

  window.setTimeout(() => {
    try {
      prefer?.focus({ preventScroll: true });
    } catch {
      /* older browsers */
    }
  }, behavior === "smooth" ? 420 : 0);
}
