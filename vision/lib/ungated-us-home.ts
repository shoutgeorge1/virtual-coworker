/**
 * Employer form LPs (US/AU home + category): skip hire vs job-seeker
 * buttons and show the employer form immediately.
 *
 * Quiz LPs stay gated. PH / thank-you / apply are not this surface.
 */

export type ConversionSurface = "form" | "quiz";

export function isUngatedEmployerLp(opts: {
  market: string;
  category?: string | null;
  conversionSurface?: ConversionSurface;
}): boolean {
  const employerMarket = opts.market === "us" || opts.market === "au";
  return employerMarket && (opts.conversionSurface ?? "form") === "form";
}

export type FormStartReason =
  | "page_load"
  | "form_visible"
  | "gate_click"
  | "field_interaction";

/**
 * employer_form_started: once per page session, never because the form is
 * merely visible. Ungated employer LPs fire only on first field interaction.
 * Gated / quiz LPs keep existing start points (Yes click, first field, quiz reveal).
 */
export function shouldFireEmployerFormStarted(opts: {
  alreadyFired: boolean;
  reason: FormStartReason;
  ungated: boolean;
}): boolean {
  if (opts.alreadyFired) return false;
  if (opts.reason === "page_load") return false;
  if (opts.ungated) return opts.reason === "field_interaction";
  return (
    opts.reason === "field_interaction" ||
    opts.reason === "gate_click" ||
    opts.reason === "form_visible"
  );
}

/**
 * employer_gate_selected must not fire on ungated employer LP load (or because
 * the form is visible). Gated pages still fire on the Yes click / assist.
 */
export function shouldFireEmployerGateSelected(opts: {
  ungated: boolean;
  alreadyEmployer: boolean;
  reason: "page_load" | "user_click" | "gate_assist";
}): boolean {
  if (opts.ungated) return false;
  if (opts.alreadyEmployer) return false;
  if (opts.reason === "page_load") return false;
  return opts.reason === "user_click" || opts.reason === "gate_assist";
}
