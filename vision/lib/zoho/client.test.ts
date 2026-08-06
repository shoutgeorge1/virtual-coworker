import { afterEach, describe, expect, it, vi } from "vitest";
import {
  clearZohoTokenCache,
  refreshAccessToken,
  upsertEmployerLead,
} from "./client";
import { parseZohoCrmConfig } from "./config";
import { mapLeadToCrmPayload } from "./payload";
import { leadLogSafe, redactText } from "./redact";

const baseEnv = {
  ZOHO_CRM_ENABLED: "true",
  ZOHO_CRM_CLIENT_ID: "cid",
  ZOHO_CRM_CLIENT_SECRET: "csecret",
  ZOHO_CRM_REFRESH_TOKEN: "rtoken",
  ZOHO_CRM_ACCOUNTS_URL: "https://accounts.zoho.com",
  ZOHO_CRM_API_DOMAIN: "https://www.zohoapis.com",
  ZOHO_CRM_MODULE: "Leads",
  ZOHO_CRM_SUBMISSION_ID_FIELD: "VC_Submission_ID",
  ZOHO_CRM_FIELD_GBRAID: "GBRAID",
  ZOHO_CRM_FIELD_WBRAID: "WBRAID",
  ZOHO_CRM_FIELD_MARKET: "VC_Market",
  ZOHO_CRM_TIMEOUT_MS: "5000",
};

const sampleLead = {
  submission_id: "vc_us_test_1",
  firstName: "Ada",
  lastName: "Lovelace",
  email: "ada@example.com",
  phone: "+15551234567",
  company: "Analytical Engines",
  market: "us",
  gclid: "gclid_abc",
  gbraid: "gbraid_xyz",
  wbraid: "wbraid_xyz",
  category: "digital-marketing",
};

afterEach(() => {
  clearZohoTokenCache();
  vi.restoreAllMocks();
});

describe("zoho config", () => {
  it("requires flag + credentials to enable", () => {
    expect(parseZohoCrmConfig({}).enabled).toBe(false);
    expect(parseZohoCrmConfig({ ZOHO_CRM_ENABLED: "true" }).enabled).toBe(false);
    expect(parseZohoCrmConfig(baseEnv).enabled).toBe(true);
  });
});

describe("payload mapping", () => {
  it("uses $gclid when present and preserves click ids + submission id", () => {
    const cfg = parseZohoCrmConfig(baseEnv);
    const mapped = mapLeadToCrmPayload(sampleLead, cfg);
    expect(mapped.data.$gclid).toBe("gclid_abc");
    expect(mapped.usesGclidSystemKey).toBe(true);
    expect(mapped.data.GBRAID).toBe("gbraid_xyz");
    expect(mapped.data.WBRAID).toBe("wbraid_xyz");
    expect(mapped.data.VC_Submission_ID).toBe("vc_us_test_1");
    expect(mapped.data.VC_Market).toBe("us");
    expect(mapped.duplicateCheckFields).toEqual(["VC_Submission_ID"]);
  });

  it("does not invent unverified custom fields", () => {
    const cfg = parseZohoCrmConfig({
      ...baseEnv,
      ZOHO_CRM_FIELD_GBRAID: "",
      ZOHO_CRM_FIELD_WBRAID: "",
      ZOHO_CRM_FIELD_MARKET: "",
    });
    const mapped = mapLeadToCrmPayload(sampleLead, cfg);
    expect(mapped.data.GBRAID).toBeUndefined();
    expect(mapped.omitted).toContain("gbraid");
    expect(mapped.omitted).toContain("market");
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

describe("token refresh + cache + retry", () => {
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

  it("retries upsert once after 401", async () => {
    const fetchImpl = vi
      .fn()
      // token
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ access_token: "at1", expires_in: 3600 }), {
          status: 200,
        }),
      )
      // first upsert 401
      .mockResolvedValueOnce(new Response("{}", { status: 401 }))
      // refresh again
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ access_token: "at2", expires_in: 3600 }), {
          status: 200,
        }),
      )
      // second upsert ok with id
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({ data: [{ details: { id: "z123" }, status: "success" }] }),
          { status: 200 },
        ),
      );

    const result = await upsertEmployerLead(sampleLead, {
      env: baseEnv,
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.zoho_synced).toBe(true);
    expect(result.recordId).toBe("z123");
    expect(fetchImpl).toHaveBeenCalledTimes(4);
  });

  it("webhook-style 200 without record id is not zoho_synced", async () => {
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

    const result = await upsertEmployerLead(sampleLead, {
      env: baseEnv,
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.ok).toBe(false);
    expect(result.zoho_synced).toBe(false);
    expect(result.recordId).toBeUndefined();
  });

  it("times out and returns redacted failure", async () => {
    const fetchImpl = vi.fn().mockImplementation(
      (_url: string, init?: RequestInit) =>
        new Promise((_resolve, reject) => {
          const signal = init?.signal;
          if (signal) {
            signal.addEventListener("abort", () => {
              const err = new Error("Aborted");
              err.name = "AbortError";
              reject(err);
            });
          }
        }),
    );

    const result = await upsertEmployerLead(sampleLead, {
      env: { ...baseEnv, ZOHO_CRM_TIMEOUT_MS: "20" },
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    expect(result.zoho_synced).toBe(false);
    expect(result.detail.toLowerCase()).toMatch(/timed out|timeout/);
  });

  it("disabled config never syncs", async () => {
    const result = await upsertEmployerLead(sampleLead, {
      env: { ZOHO_CRM_ENABLED: "false" },
    });
    expect(result.zoho_synced).toBe(false);
    expect(result.detail).toBe("zoho_crm_disabled");
  });
});
