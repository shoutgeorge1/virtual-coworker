import { afterEach, describe, expect, it, vi } from "vitest";
import {
  clearZohoTokenCache,
  createEmployerLead,
  refreshAccessToken,
  upsertEmployerLead,
} from "./client";
import { parseZohoCrmConfig } from "./config";
import { formatZohoDateTime, mapLeadToCrmPayload } from "./payload";
import { leadLogSafe, redactText } from "./redact";

const baseEnv = {
  ZOHO_SUBMISSION_ENABLED: "true",
  ZOHO_CRM_CLIENT_ID: "cid",
  ZOHO_CRM_CLIENT_SECRET: "csecret",
  ZOHO_CRM_REFRESH_TOKEN: "rtoken",
  ZOHO_CRM_ACCOUNTS_URL: "https://accounts.zoho.com",
  ZOHO_CRM_API_DOMAIN: "https://www.zohoapis.com",
  ZOHO_CRM_MODULE: "Leads",
  ZOHO_CRM_TIMEOUT_MS: "5000",
};

const sampleLead = {
  submission_id: "VC-ZOHO-TEST-1",
  firstName: "Zoho",
  lastName: "Integration Test",
  email: "ada@example.com",
  phone: "+15550100199",
  company: "[TEST] Virtual Coworker API",
  market: "us",
  lead_source: "API Integration Test",
  form_source: "API Integration Test",
  message: "TEST RECORD — DO NOT CONTACT — DO NOT QUALIFY — DO NOT CONVERT",
  gclid: "TEST-gclid",
  gbraid: "TEST-gbraid",
  wbraid: "TEST-wbraid",
  category: "digital-marketing",
};

afterEach(() => {
  clearZohoTokenCache();
  vi.restoreAllMocks();
});

describe("zoho config", () => {
  it("requires ZOHO_SUBMISSION_ENABLED + credentials; ignores ZOHO_CRM_ENABLED", () => {
    expect(parseZohoCrmConfig({}).enabled).toBe(false);
    expect(parseZohoCrmConfig({ ZOHO_CRM_ENABLED: "true" }).enabled).toBe(false);
    expect(
      parseZohoCrmConfig({
        ZOHO_CRM_ENABLED: "true",
        ZOHO_CRM_CLIENT_ID: "cid",
        ZOHO_CRM_CLIENT_SECRET: "sec",
        ZOHO_CRM_REFRESH_TOKEN: "rt",
      }).enabled,
    ).toBe(false);
    expect(parseZohoCrmConfig(baseEnv).enabled).toBe(true);
  });
});

describe("payload mapping", () => {
  it("maps verified Sales Enquiry fields and never writes Ads-filter statuses", () => {
    const cfg = parseZohoCrmConfig(baseEnv);
    const mapped = mapLeadToCrmPayload(sampleLead, cfg);
    expect(mapped.data.utm_gclid).toBe("TEST-gclid");
    expect(mapped.data.$gclid).toBeUndefined();
    expect(mapped.usesGclidSystemKey).toBe(false);
    expect(mapped.data.Gravity_Form_Entry_ID).toBe("VC-ZOHO-TEST-1");
    expect(mapped.data.Region).toBe("USA");
    expect(mapped.data.Lead_Status).toBe("New Enquiry (Auto)");
    expect(mapped.data.Lead_Status).not.toMatch(/Discovery|Job Order|Placement|Qualified/);
    expect(mapped.data.Form_Source).toBe("API Integration Test");
    expect(mapped.data.Lead_Source).toBeUndefined();
    expect(String(mapped.data.Other_Client_Profile_Information)).toContain("DO NOT CONVERT");
    expect(mapped.data.Job_Order_submitted_via_form).toBeUndefined();
    expect(mapped.data.Blueprint_Lead_Status).toBeUndefined();
    expect(mapped.data.Book_free_consultation).toBeUndefined();
    expect(mapped.duplicateCheckFields).toEqual([]);
    expect(mapped.omitted).toContain("gbraid");
    expect(mapped.omitted).toContain("wbraid");
  });

  it("formats Submission_Timestamp for Zoho datetime", () => {
    const cfg = parseZohoCrmConfig(baseEnv);
    const mapped = mapLeadToCrmPayload(
      { ...sampleLead, submitted_at: "2026-08-17T21:27:11.847Z" },
      cfg,
    );
    expect(mapped.data.Submission_Timestamp).toBe("2026-08-17T21:27:11+00:00");
    expect(formatZohoDateTime("2026-08-17T21:27:11.847123+00:00")).toBe(
      "2026-08-17T21:27:11+00:00",
    );
    expect(formatZohoDateTime("not-a-date")).toBeUndefined();
  });

  it("puts company website on Website, not a new field", () => {
    const cfg = parseZohoCrmConfig(baseEnv);
    const mapped = mapLeadToCrmPayload(
      { ...sampleLead, company_website: "https://acme.com" },
      cfg,
    );
    expect(mapped.data.Website).toBe("https://acme.com");
  });
});

describe("redact + safe logs", () => {
  it("redacts tokens emails urls click ids", () => {
    const s = redactText(
      "Bearer secretTOKEN email ada@example.com https://evil.test/?gclid=abc123",
    );
    expect(s).not.toMatch(/secretTOKEN/);
    expect(s).not.toMatch(/ada@example/);
    expect(s).not.toMatch(/https:\/\//);
    expect(s).toMatch(/\[REDACTED/);
  });

  it("safe log has no PII keys", () => {
    const log = leadLogSafe({
      submission_id: "vc_1",
      market: "us",
      channel: "zoho_crm",
      ok: false,
      error: "ada@example.com failed",
      duration_ms: 12,
    });
    expect(JSON.stringify(log)).not.toMatch(/ada@/);
    expect(log).toMatchObject({
      submission_id: "vc_1",
      market: "us",
      channel: "zoho_crm",
      ok: false,
      duration_ms: 12,
    });
  });
});

describe("token refresh + create", () => {
  it("caches access token across calls", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ access_token: "at1", expires_in: 3600 }), {
          status: 200,
        }),
      );
    const cfg = parseZohoCrmConfig(baseEnv);
    const t1 = await refreshAccessToken(cfg, fetchImpl as unknown as typeof fetch);
    const t2 = await refreshAccessToken(cfg, fetchImpl as unknown as typeof fetch);
    expect(t1).toBe("at1");
    expect(t2).toBe("at1");
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it("POSTs create (not upsert) and retries once after 401", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ access_token: "at1", expires_in: 3600 }), {
          status: 200,
        }),
      )
      .mockResolvedValueOnce(new Response("{}", { status: 401 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ access_token: "at2", expires_in: 3600 }), {
          status: 200,
        }),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({ data: [{ details: { id: "z123" }, status: "success", code: "SUCCESS" }] }),
          { status: 201 },
        ),
      );

    const result = await createEmployerLead(sampleLead, {
      env: baseEnv,
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.zoho_synced).toBe(true);
    expect(result.recordId).toBe("z123");
    expect(result.code).toBe("SUCCESS");
    const createUrl = String(fetchImpl.mock.calls[1][0]);
    expect(createUrl).toMatch(/\/crm\/v8\/Leads$/);
    expect(createUrl).not.toMatch(/upsert/);
    const createBody = JSON.parse(String(fetchImpl.mock.calls[3][1].body));
    expect(createBody.trigger).toEqual([]);
    expect(createBody.duplicate_check_fields).toBeUndefined();
  });

  it("200 without record id is not zoho_synced", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ access_token: "at1", expires_in: 3600 }), {
          status: 200,
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ data: [{ status: "error", code: "INVALID" }] }), {
          status: 200,
        }),
      );

    const result = await createEmployerLead(sampleLead, {
      env: baseEnv,
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.ok).toBe(false);
    expect(result.zoho_synced).toBe(false);
    expect(result.recordId).toBeUndefined();
  });

  it("disabled config never syncs", async () => {
    const result = await createEmployerLead(sampleLead, {
      env: { ZOHO_SUBMISSION_ENABLED: "false" },
    });
    expect(result.zoho_synced).toBe(false);
    expect(result.detail).toBe("zoho_submission_disabled");
  });

  it("legacy upsert stays unused by create path", async () => {
    const result = await upsertEmployerLead(sampleLead, {
      env: { ZOHO_CRM_ENABLED: "true" },
    });
    expect(result.zoho_synced).toBe(false);
  });
});
