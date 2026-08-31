import { NextRequest, NextResponse } from "next/server";
import { assertCronAuthorized } from "@/lib/sync/auth";
import { runDailySync } from "@/lib/sync/orchestrator";
import { redactUnknown } from "@/lib/sync/redact";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
/** Allow long multi-source pulls within Vercel limits. */
export const maxDuration = 300;

async function handle(req: NextRequest, trigger: "cron" | "manual") {
  const auth = assertCronAuthorized(req);
  if (!auth.ok) {
    return NextResponse.json({ ok: false, error: auth.error }, { status: auth.status });
  }

  try {
    const result = await runDailySync({ trigger });
    const status = result.ok ? 200 : result.partial ? 207 : 502;
    return NextResponse.json(
      {
        ok: result.ok,
        partial: result.partial,
        run_id: result.run_id,
        window_start: result.window_start,
        window_end: result.window_end,
        status: result.status,
        errors: result.errors,
      },
      { status },
    );
  } catch (err) {
    return NextResponse.json(
      { ok: false, error: redactUnknown(err) },
      { status: 500 },
    );
  }
}

/** Vercel Cron — GET /api/cron/daily-sync at 12:30 UTC. */
export async function GET(req: NextRequest) {
  return handle(req, "cron");
}

export async function POST(req: NextRequest) {
  return handle(req, "cron");
}
