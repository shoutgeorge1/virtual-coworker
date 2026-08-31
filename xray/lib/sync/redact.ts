/** Redact secrets / click IDs from sync logs. Server-only. */

const TOKEN_KEYS =
  /(?:access_token|refresh_token|client_secret|authorization|api_key|developer_token|CRON_SECRET)\s*[:=]\s*["']?([^\s"',}]+)/gi;
const BEARER = /(?:Bearer|Zoho-oauthtoken)\s+[A-Za-z0-9._\-]+/gi;
const EMAIL = /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi;
const CLICK_ID = /\b(?:gclid|gbraid|wbraid)=([A-Za-z0-9._\-]+)/gi;

export function redactText(input: string): string {
  return input
    .replace(TOKEN_KEYS, (m) => {
      const idx = m.search(/[:=]/);
      const key = idx >= 0 ? m.slice(0, idx + 1) : "secret=";
      return `${key}[REDACTED]`;
    })
    .replace(BEARER, "[REDACTED_AUTH]")
    .replace(EMAIL, "[REDACTED_EMAIL]")
    .replace(CLICK_ID, (m) => `${m.split("=")[0]}=[REDACTED]`);
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

export function syncLog(fields: Record<string, string | number | boolean | null | undefined>): void {
  const safe: Record<string, string | number | boolean | null> = {};
  for (const [k, v] of Object.entries(fields)) {
    if (v === undefined) continue;
    if (typeof v === "string") safe[k] = redactText(v);
    else safe[k] = v;
  }
  console.info("[daily-sync]", JSON.stringify(safe));
}
