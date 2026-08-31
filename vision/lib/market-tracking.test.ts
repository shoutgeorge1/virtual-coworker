import { afterEach, describe, expect, it } from "vitest";
import { resolveGa4Id, resolveGtmId } from "./market-tracking";

const ENV_KEYS = [
  "NEXT_PUBLIC_GTM_US",
  "NEXT_PUBLIC_GTM_AU",
  "NEXT_PUBLIC_GTM_PH",
  "NEXT_PUBLIC_GA4_US",
  "NEXT_PUBLIC_GA4_AU",
  "NEXT_PUBLIC_GA4_PH",
  "NEXT_PUBLIC_GTM_ID",
  "NEXT_PUBLIC_GA4_ID",
] as const;

afterEach(() => {
  for (const k of ENV_KEYS) delete process.env[k];
});

describe("market tracking env wire", () => {
  it("AU reads NEXT_PUBLIC_GTM_AU / NEXT_PUBLIC_GA4_AU", () => {
    process.env.NEXT_PUBLIC_GTM_AU = "GTM-TESTAU";
    process.env.NEXT_PUBLIC_GA4_AU = "G-TESTAU";
    expect(resolveGtmId("au")).toBe("GTM-TESTAU");
    expect(resolveGa4Id("au")).toBe("G-TESTAU");
  });

  it("AU stays empty when unset — no US or legacy fallback", () => {
    process.env.NEXT_PUBLIC_GTM_US = "GTM-TESTUS";
    process.env.NEXT_PUBLIC_GA4_US = "G-TESTUS";
    process.env.NEXT_PUBLIC_GTM_ID = "GTM-LEGACY";
    process.env.NEXT_PUBLIC_GA4_ID = "G-LEGACY";
    expect(resolveGtmId("au")).toBe("");
    expect(resolveGa4Id("au")).toBe("");
  });

  it("US may fall back to legacy NEXT_PUBLIC_GTM_ID / NEXT_PUBLIC_GA4_ID", () => {
    process.env.NEXT_PUBLIC_GTM_ID = "GTM-LEGACY";
    process.env.NEXT_PUBLIC_GA4_ID = "G-LEGACY";
    expect(resolveGtmId("us")).toBe("GTM-LEGACY");
    expect(resolveGa4Id("us")).toBe("G-LEGACY");
  });
});
