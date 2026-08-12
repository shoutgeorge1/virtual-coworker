/**
 * As-you-type phone display + CRM-safe normalize.
 * Do not reject short/international numbers — formatting is a convenience,
 * not a gate. Server still only requires a non-empty phone.
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
  let intl = hadPlus;

  if (national.startsWith("61")) {
    intl = true;
    national = national.slice(2);
    if (national.startsWith("0")) national = national.slice(1);
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
