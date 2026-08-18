/**
 * Preview-only employer form sink.
 * Never writes Zoho. Never sends email. Never fires production conversions.
 */

import { NextRequest, NextResponse } from "next/server";
import {
  rejectLogPayload,
  validateEmployerLead,
  type LeadInput,
} from "../../../lib/lead-validation";
import { TRUST_FIRST_LANDING_PAGE_TYPE, TRUST_FIRST_LP_VERSION } from "../../../config/trust-first";

export async function POST(req: NextRequest) {
  let body: LeadInput & { preview?: boolean; lp_key?: string };
  try {
    body = (await req.json()) as LeadInput & { preview?: boolean; lp_key?: string };
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON" }, { status: 400 });
  }

  const company = String(body.company || "").trim();
  if (!company) {
    return NextResponse.json(
      { ok: false, error: "Company name is required.", code: "missing_fields" },
      { status: 400 },
    );
  }

  const validation = validateEmployerLead({
    ...body,
    market: "us",
    intent: "employer",
  });

  if (!validation.ok) {
    console.info(
      "[lead-preview-reject]",
      JSON.stringify(
        rejectLogPayload(validation.code, "us", { reason: validation.reason }),
      ),
    );
    const status =
      validation.code === "job_seeker" || validation.code === "honeypot" ? 403 : 400;
    return NextResponse.json(
      {
        ok: false,
        error: validation.code === "honeypot" ? "Unable to submit." : validation.reason,
        code: validation.code,
        preview: true,
      },
      { status },
    );
  }

  console.info(
    "[lead-preview-accept]",
    JSON.stringify({
      preview: true,
      zoho: false,
      email: false,
      production_conversion: false,
      market: "us",
      lp_version: body.lp_version || TRUST_FIRST_LP_VERSION,
      landing_page_type: TRUST_FIRST_LANDING_PAGE_TYPE,
      lp_key: body.lp_key || "",
      lp_variant: body.lp_variant || "",
      role: body.role || "",
      company_size: body.company_size || "",
      hiring_timeline: body.hiring_timeline || "",
    }),
  );

  return NextResponse.json({
    ok: true,
    preview: true,
    delivered: false,
    message:
      "Preview only. This inquiry was not sent to Virtual Coworker, Zoho, or email.",
  });
}
