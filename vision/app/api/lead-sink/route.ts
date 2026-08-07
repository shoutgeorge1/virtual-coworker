import { NextRequest, NextResponse } from "next/server";
import { formatLeadEmailText } from "../../../lib/lead-delivery";

/**
 * Durable pilot lead inbox: private GitHub Issues.
 * Called via LEAD_WEBHOOK_URL (same app). Resend/Zoho can replace later.
 *
 * Auth: ?token=LEAD_SINK_SECRET or Authorization: Bearer LEAD_SINK_SECRET
 */

type LeadBody = {
  submission_id?: string;
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  company?: string;
  role?: string;
  category?: string;
  timeline?: string;
  message?: string;
  market?: string;
  landing_page_url?: string;
  referrer?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  gclid?: string;
  gbraid?: string;
  wbraid?: string;
  submitted_at?: string;
};

function sinkConfigured(): boolean {
  return Boolean(
    (process.env.LEAD_SINK_SECRET || "").trim() &&
      (process.env.GITHUB_LEADS_TOKEN || "").trim(),
  );
}

function authorized(req: NextRequest): boolean {
  const expected = (process.env.LEAD_SINK_SECRET || "").trim();
  if (!expected) return false;
  const q = req.nextUrl.searchParams.get("token") || "";
  if (q && q === expected) return true;
  const auth = req.headers.get("authorization") || "";
  if (auth.toLowerCase().startsWith("bearer ")) {
    return auth.slice(7).trim() === expected;
  }
  return false;
}

function issueTitle(lead: LeadBody): string {
  const market = String(lead.market || "??").toUpperCase();
  const name =
    [lead.firstName, lead.lastName].filter(Boolean).join(" ").trim() ||
    lead.email ||
    "employer";
  const company = String(lead.company || "").trim();
  const base = company ? `${name} · ${company}` : name;
  return `${market} lead — ${base}`.slice(0, 200);
}

export async function POST(req: NextRequest) {
  if (!sinkConfigured()) {
    return NextResponse.json(
      { ok: false, error: "lead-sink not configured" },
      { status: 503 },
    );
  }
  if (!authorized(req)) {
    return NextResponse.json({ ok: false, error: "unauthorized" }, { status: 401 });
  }

  let lead: LeadBody;
  try {
    lead = (await req.json()) as LeadBody;
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON" }, { status: 400 });
  }

  const market = String(lead.market || "").toLowerCase();
  const labels = ["lead"];
  if (market === "us" || market === "au") labels.push(`market:${market}`);

  const repo =
    (process.env.GITHUB_LEADS_REPO || "").trim() || "shoutgeorge1/vc-employer-leads";
  const token = (process.env.GITHUB_LEADS_TOKEN || "").trim();

  const body = [
    formatLeadEmailText(lead),
    "",
    "---",
    "_Pilot inbox (GitHub Issues). Team email also fires to us@ / apac@ via Resend. Zoho CRM API still later._",
  ].join("\n");

  try {
    const res = await fetch(`https://api.github.com/repos/${repo}/issues`, {
      method: "POST",
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${token}`,
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "virtual-coworker-lead-sink",
      },
      body: JSON.stringify({
        title: issueTitle(lead),
        body,
        labels,
      }),
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      console.error(
        "[lead-sink]",
        JSON.stringify({
          ok: false,
          status: res.status,
          submission_id: lead.submission_id,
          detail: text.slice(0, 200),
        }),
      );
      return NextResponse.json(
        { ok: false, error: `GitHub HTTP ${res.status}` },
        { status: 502 },
      );
    }
    const data = (await res.json()) as { html_url?: string; number?: number };
    console.info(
      "[lead-sink]",
      JSON.stringify({
        ok: true,
        submission_id: lead.submission_id,
        market,
        issue: data.number,
      }),
    );
    return NextResponse.json({
      ok: true,
      issue_number: data.number,
      html_url: data.html_url,
    });
  } catch (err) {
    console.error(
      "[lead-sink]",
      JSON.stringify({
        ok: false,
        error: err instanceof Error ? err.message : "network error",
      }),
    );
    return NextResponse.json(
      { ok: false, error: "lead-sink network error" },
      { status: 502 },
    );
  }
}
