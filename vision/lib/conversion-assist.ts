/**
 * Session hook after a meaningful conversion action.
 * tracking.ts already dispatches `vc-primary-converted` for UI.
 * Keep this a no-throw hook so form/phone tracking never crashes.
 */
export function markPrimaryConverted(
  _reason: "phone_click" | "form_submit",
): void {}
