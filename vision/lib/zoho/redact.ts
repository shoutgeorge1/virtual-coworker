/**
 * Redact tokens and PII from strings destined for logs / errors.
 * Never log access tokens, refresh tokens, emails, phones, click IDs, or URLs.
 */

const TOKEN_KEYS =
  /(?:access_token|refresh_token|client_secret|authorization|api_key|grant_code|code)\s*[:=]\s*["']?([^\s"',}]+)/gi;

const BEARER = /(?:Bearer|Zoho-oauthtoken)\s+[A-Za-z0-9._\-]+/gi;

const EMAIL = /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi;

const PHONE = /\b(?:\+?\d[\d\s().-]{7,}\d)\b/g;

const CLICK_ID = /\b(?:gclid|gbraid|wbraid)=([A-Za-z0-9._\-]+)/gi;

const URL = /https?:\/\/[^\s"'<>]+/gi;

export function maskSecret(value: string | undefined | null, keep = 4): string {
  if (!value) return "(empty)";
  if (value.length <= keep * 2) return "***";
  return `${value.slice(0, keep)}…${value.slice(-keep)}`;
}

export function redactText(input: string): string {
  return input
    .replace(TOKEN_KEYS, (m) => {
      const idx = m.search(/[:=]/);
      const key = idx >= 0 ? m.slice(0, idx + 1) : "secret=";
      return `${key}[REDACTED]`;
    })
    .replace(BEARER, "[REDACTED_AUTH]")
    .replace(EMAIL, "[REDACTED_EMAIL]")
    .replace(CLICK_ID, (_m, _id, offset, s) => {
      // preserve key name only
      const slice = String(s).slice(Math.max(0, offset), offset + 12);
      const key = slice.split("=")[0] || "click_id";
      return `${key}=[REDACTED]`;
    })
    .replace(URL, "[REDACTED_URL]")
    .replace(PHONE, "[REDACTED_PHONE]");
}

export function redactUnknown(err: unknown): string {
  if (err instanceof Error) return redactText(err.message);
  if (typeof err === "string") return redactText(err);
  try {
    return redactText(JSON.stringify(err));
  } catch {
    return "[REDACTED_ERROR]";
  }
}

/** Safe production log fields only — no PII, GCLID, URLs, or payloads. */
export function leadLogSafe(fields: {
  submission_id: string;
  market: string;
  channel: string;
  ok: boolean;
  error?: string;
  duration_ms: number;
}): Record<string, string | number | boolean> {
  return {
    submission_id: fields.submission_id,
    market: fields.market,
    channel: fields.channel,
    ok: fields.ok,
    error: fields.error ? redactText(fields.error) : "",
    duration_ms: fields.duration_ms,
  };
}
