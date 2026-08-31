import { NextRequest, NextResponse } from "next/server";
import { assertCronAuthorized } from "@/lib/sync/auth";
import { createStore } from "@/lib/db/store";
import { redactUnknown } from "@/lib/sync/redact";
import { sanitizeDashboardStatus, statusLooksSafe } from "@/lib/sync/status-safe";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** Protected dashboard status (last sync, freshness, row counts, partial failures). */
export async function GET(req: NextRequest) {
  const auth = assertCronAuthorized(req);
  if (!auth.ok) {
    return NextResponse.json({ ok: false, error: auth.error }, { status: auth.status });
  }

  try {
    const store = createStore();
    await store.ensureSchema();
    const raw = await store.getDashboardStatus();
    const status = sanitizeDashboardStatus(raw);
    const row_counts = await store.countRows();
    const body = {
      ok: true,
      status,
      row_counts,
    };
    if (!statusLooksSafe(body)) {
      return NextResponse.json(
        { ok: false, error: "status_payload_blocked" },
        { status: 500 },
      );
    }
    return NextResponse.json(body);
  } catch (err) {
    return NextResponse.json(
      { ok: false, error: redactUnknown(err) },
      { status: 500 },
    );
  }
}
