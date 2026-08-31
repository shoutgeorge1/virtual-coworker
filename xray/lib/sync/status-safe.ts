import { redactText } from "@/lib/sync/redact";
import type { DashboardStatus } from "@/lib/sync/types";

const SECRETISH =
  /(access_token|refresh_token|client_secret|developer_token|CRON_SECRET|Bearer\s|Zoho-oauthtoken|BEGIN PRIVATE KEY|private_key)/i;

/**
 * Public status payload must never leak credentials or raw upstream auth errors.
 */
export function sanitizeDashboardStatus(status: DashboardStatus | null): DashboardStatus | null {
  if (!status) return null;
  return {
    ...status,
    freshness: status.freshness.map((f) => ({
      ...f,
      error: f.error ? sanitizeErrorMessage(f.error) : undefined,
    })),
    partial_failures: status.partial_failures.map((p) => ({
      source: p.source,
      error: sanitizeErrorMessage(p.error),
    })),
  };
}

export function sanitizeErrorMessage(msg: string): string {
  let redacted = redactText(msg);
  // Collapse Google HTML 404 bodies / large markup into a short code
  if (/<!DOCTYPE html>/i.test(redacted) || /<html[\s>]/i.test(redacted)) {
    const code = redacted.match(/HTTP\s+(\d{3})/i)?.[1];
    return code
      ? `upstream_http_${code} (html body redacted)`
      : "upstream_html_error (details redacted)";
  }
  if (SECRETISH.test(redacted)) {
    return "upstream_error (details redacted)";
  }
  if (redacted.length > 280) {
    return `${redacted.slice(0, 240)}…`;
  }
  return redacted;
}

export function statusLooksSafe(payload: unknown): boolean {
  try {
    const text = JSON.stringify(payload);
    return !SECRETISH.test(text);
  } catch {
    return false;
  }
}
