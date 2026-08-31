import { NextRequest } from "next/server";

/**
 * Vercel Cron sends Authorization: Bearer <CRON_SECRET> when CRON_SECRET is set.
 * Manual sync uses the same header.
 */
export function assertCronAuthorized(req: NextRequest): { ok: true } | { ok: false; status: number; error: string } {
  const secret = (process.env.CRON_SECRET || "").trim();
  if (!secret) {
    return { ok: false, status: 503, error: "CRON_SECRET not configured" };
  }

  const header = req.headers.get("authorization") || "";
  const bearer = header.match(/^Bearer\s+(.+)$/i)?.[1]?.trim() || "";
  const alt = (req.headers.get("x-cron-secret") || "").trim();
  const provided = bearer || alt;

  if (!provided || !timingSafeEqual(provided, secret)) {
    return { ok: false, status: 401, error: "unauthorized" };
  }
  return { ok: true };
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let out = 0;
  for (let i = 0; i < a.length; i++) {
    out |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return out === 0;
}
