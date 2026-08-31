/**
 * As-you-type phone display + CRM-safe normalize + US employer validation.
 * AU still formats without a NANP gate. US server validation is authoritative.
 */

import type { MarketId } from "../config/markets";

export function phoneDigits(raw: string): string {
  return String(raw || "").replace(/\D/g, "");
}

function grouped(digits: string, sizes: number[]): string {
  const parts: string[] = [];
  let i = 0;
  for (const n of sizes) {
    if (i >= digits.length) break;
    parts.push(digits.slice(i, i + n));
    i += n;
  }
  if (i < digits.length) parts.push(digits.slice(i));
  return parts.join(" ");
}

function formatUsDisplay(digits: string, hadPlus: boolean): string {
  if (!digits && hadPlus) return "+";

  // Non-US country code pasted on a US page — don't force NANP.
  if (hadPlus && digits.length >= 2 && !digits.startsWith("1")) {
    return `+${digits}`;
  }

  let rest = digits;
  let prefix = "";
  if (rest.startsWith("1") && (hadPlus || rest.length > 10)) {
    prefix = "+1 ";
    rest = rest.slice(1);
  }

  const nanp = rest.slice(0, 10);
  const ext = rest.slice(10, 16);
  if (!nanp) return prefix.trim() || (hadPlus ? "+" : "");

  let out = "";
  if (nanp.length < 4) out = `(${nanp}`;
  else if (nanp.length < 7) out = `(${nanp.slice(0, 3)}) ${nanp.slice(3)}`;
  else out = `(${nanp.slice(0, 3)}) ${nanp.slice(3, 6)}-${nanp.slice(6)}`;

  if (ext) out += ` ${ext}`;
  return `${prefix}${out}`.trim();
}

function formatAuDisplay(digits: string, hadPlus: boolean): string {
  if (!digits && hadPlus) return "+";

  let national = digits;
  let intl = false;

  // Only treat as +61 once the country code is complete — typing "+6"
  // must not jump to "+61 6" (that duplicates the "1" and mangles the rest).
  if (national.startsWith("61")) {
    intl = true;
    national = national.slice(2);
    if (national.startsWith("0")) national = national.slice(1);
  } else if (hadPlus) {
    // Incomplete (+ / +6) or non-AU country code — don't force +61.
    return `+${digits}`;
  }

  // +61 4XX XXX XXX (mobile) / +61 2 XXXX XXXX (landline) / +61 1300 XXX XXX
  if (intl) {
    if (national.startsWith("4")) {
      return `+61 ${grouped(national.slice(0, 9), [3, 3, 3])}`.trim();
    }
    if (/^(1300|1800)/.test(national)) {
      return `+61 ${grouped(national.slice(0, 10), [4, 3, 3])}`.trim();
    }
    if (/^[2378]/.test(national)) {
      return `+61 ${grouped(national.slice(0, 9), [1, 4, 4])}`.trim();
    }
    if (!national) return "+61";
    return `+61 ${national}`.trim();
  }

  // National 04XX XXX XXX
  if (national.startsWith("04") || (national.startsWith("4") && national.length <= 9)) {
    const d = national.startsWith("04") ? national : `0${national}`;
    return grouped(d.slice(0, 10), [4, 3, 3]);
  }

  // 1300 / 1800 XXX XXX
  if (/^(1300|1800)/.test(national)) {
    return grouped(national.slice(0, 10), [4, 3, 3]);
  }

  // 13 XX XX
  if (national.startsWith("13") && !national.startsWith("1300")) {
    return grouped(national.slice(0, 6), [2, 2, 2]);
  }

  // (0X) XXXX XXXX landline
  if (/^0[2378]/.test(national)) {
    const area = national.slice(0, 2);
    const rest = national.slice(2, 10);
    if (!rest) return `(${area}`;
    if (rest.length <= 4) return `(${area}) ${rest}`;
    return `(${area}) ${rest.slice(0, 4)} ${rest.slice(4)}`;
  }

  return national;
}

/** Format as the user types. Never throws; unknown shapes pass through lightly. */
export function formatPhoneInput(raw: string, market: MarketId): string {
  const value = String(raw || "");
  if (!value.trim()) return "";
  const hadPlus = value.trim().startsWith("+");
  const digits = phoneDigits(value);
  if (!digits && !hadPlus) return value.trim();
  return market === "au"
    ? formatAuDisplay(digits, hadPlus)
    : formatUsDisplay(digits, hadPlus);
}

/**
 * E.164-ish value for CRM / email. Incomplete numbers stay as digits
 * (or +digits) so we never invent a country code.
 */
export function normalizePhoneForStorage(raw: string, market: MarketId): string {
  const value = String(raw || "").trim();
  if (!value) return "";
  const hadPlus = value.startsWith("+");
  const digits = phoneDigits(value);
  if (!digits) return value;

  if (market === "us") {
    if (digits.length === 10) return `+1${digits}`;
    if (digits.length === 11 && digits.startsWith("1")) return `+${digits}`;
    if (hadPlus) return `+${digits}`;
    return digits;
  }

  if (digits.startsWith("61")) return `+${digits}`;
  if (/^(1300|1800|13)\d+$/.test(digits)) return `+61${digits}`;
  if (digits.startsWith("0") && digits.length >= 9) return `+61${digits.slice(1)}`;
  if (hadPlus) return `+${digits}`;
  return digits;
}

export type UsPhoneRejectCode = "invalid_us_phone" | "ph_job_seeker_phone";

export type UsPhoneValidation =
  | { ok: true; e164: string; national10: string }
  | { ok: false; code: UsPhoneRejectCode };

function isNanpNational(digits10: string): boolean {
  if (digits10.length !== 10) return false;
  const npa = digits10[0];
  const nxx = digits10[3];
  return npa >= "2" && npa <= "9" && nxx >= "2" && nxx <= "9";
}

function looksLikePhMobile(digits: string): boolean {
  if (digits.startsWith("63")) {
    const rest = digits.slice(2).replace(/^0/, "");
    return rest.length === 10 && rest.startsWith("9");
  }
  if (digits.startsWith("09") && digits.length === 11) return true;
  if (digits.startsWith("9") && digits.length === 11) return true;
  return false;
}

/**
 * Accept valid US +1 / 10-digit NANP. Reject PH +63 and 09xx local mobiles,
 * incomplete, and overlong numbers. 555 test numbers (e.g. 951-555-0123) pass.
 */
export function validateUsPhone(raw: string): UsPhoneValidation {
  const value = String(raw || "").trim();
  if (!value) return { ok: false, code: "invalid_us_phone" };
  const digits = phoneDigits(value);
  if (!digits) return { ok: false, code: "invalid_us_phone" };

  if (looksLikePhMobile(digits)) {
    return { ok: false, code: "ph_job_seeker_phone" };
  }

  let national = digits;
  if (national.startsWith("1") && national.length === 11) {
    national = national.slice(1);
  }

  if (national.length < 10) return { ok: false, code: "invalid_us_phone" };
  if (national.length > 10) return { ok: false, code: "invalid_us_phone" };
  if (!isNanpNational(national)) return { ok: false, code: "invalid_us_phone" };

  return { ok: true, e164: `+1${national}`, national10: national };
}

export const US_PHONE_ERROR =
  "Enter a valid US phone number, like (951) 555-0123.";

export const PH_PHONE_CAREERS_MESSAGE =
  "That number looks like a Philippines mobile. This page is for US employers hiring staff. If you are looking for work, view careers in the Philippines.";

