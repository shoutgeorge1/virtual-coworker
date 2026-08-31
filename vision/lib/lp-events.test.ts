import { beforeEach, describe, expect, it, vi } from "vitest";
import { AUTHORITATIVE_LP_VERSION, US_BASELINE_LABEL } from "../config/lp-version";

function createSessionStore() {
  const map = new Map<string, string>();
  return {
    getItem: (k: string) => map.get(k) ?? null,
    setItem: (k: string, v: string) => {
      map.set(k, v);
    },
    removeItem: (k: string) => {
      map.delete(k);
    },
    clear: () => map.clear(),
    get length() {
      return map.size;
    },
    key: (i: number) => [...map.keys()][i] ?? null,
  };
}

function events() {
  return (
    window as unknown as { dataLayer: Array<Record<string, unknown>> }
  ).dataLayer;
}

describe("canonical LP events", () => {
  beforeEach(async () => {
    vi.resetModules();
    const store = createSessionStore();
    const durable = createSessionStore();
    vi.stubGlobal("window", {
      dataLayer: [] as Array<Record<string, unknown>>,
      sessionStorage: store,
      localStorage: durable,
      location: {
        href: "https://www.virtualcoworker.app/us?gclid=abc&utm_source=google&utm_medium=cpc&utm_campaign=241&utm_content=ag1&utm_term=kw&utm_matchtype=e&utm_device=m",
        search:
          "?gclid=abc&utm_source=google&utm_medium=cpc&utm_campaign=241&utm_content=ag1&utm_term=kw&utm_matchtype=e&utm_device=m",
        pathname: "/us",
      },
    });
    vi.stubGlobal("sessionStorage", store);
    vi.stubGlobal("localStorage", durable);
    vi.stubGlobal("document", { referrer: "https://google.com" });
    const { resetLpEventDedupeForTests } = await import("./lp-events");
    resetLpEventDedupeForTests();
  });

  it("fires lp_view once per path", async () => {
    const { trackLpView } = await import("./lp-events");
    trackLpView({ market: "us" });
    trackLpView({ market: "us" });
    expect(events().filter((e) => e.event === "lp_view")).toHaveLength(1);
    expect(events()[0]).toMatchObject({
      event: "lp_view",
      market: "us",
      lp_version: AUTHORITATIVE_LP_VERSION,
      baseline_label: US_BASELINE_LABEL,
      page_path: "/us",
      landing_page_type: "employer_paid_lp",
    });
    expect(events()[0].experiment_id).toBeUndefined();
  });

  it("fires form_start once and employer_form_step_completed once per step", async () => {
    const { trackFormStart, trackEmployerFormStepCompleted } = await import("./lp-events");
    trackFormStart({ market: "us", role_selected: "Admin/EA" });
    trackFormStart({ market: "us", role_selected: "Admin/EA" });
    trackEmployerFormStepCompleted({
      market: "us",
      step_number: 1,
      step_name: "role",
      role_selected: "Admin/EA",
    });
    trackEmployerFormStepCompleted({
      market: "us",
      step_number: 1,
      step_name: "role",
      role_selected: "Admin/EA",
    });
    expect(events().filter((e) => e.event === "form_start")).toHaveLength(1);
    expect(events().filter((e) => e.event === "employer_form_started")).toHaveLength(0);
    expect(events().filter((e) => e.event === "employer_form_step_completed")).toHaveLength(1);
  });

  it("does not send PII on form_validation_error or phone_cta_clicked", async () => {
    const { trackFormValidationError, trackPhoneCtaClicked } = await import("./lp-events");
    trackFormValidationError({
      market: "us",
      error_category: "invalid_us_phone",
      form_step: "contact",
    });
    trackPhoneCtaClicked({ market: "us", cta_location: "header" });
    const blob = JSON.stringify(events());
    expect(blob).not.toMatch(/@/);
    expect(blob).not.toMatch(/555-0123/);
    expect(events().some((e) => e.event === "phone_click")).toBe(false);
    expect(events().find((e) => e.event === "phone_cta_clicked")).toMatchObject({
      cta_location: "header",
      is_qualified_call: false,
    });
  });

  it("fires employer_inquiry_submitted once and never on ineligible or duplicate", async () => {
    const { trackValidEmployerSubmit } = await import("./tracking");
    trackValidEmployerSubmit({
      market: "us",
      submissionId: "sid_ok",
      role: "Admin",
      positionsNeeded: "1",
      schedule: "full_time",
    });
    trackValidEmployerSubmit({
      market: "us",
      submissionId: "sid_ok",
      role: "Admin",
    });
    trackValidEmployerSubmit({
      market: "us",
      submissionId: "sid_fail",
      conversionEligible: false,
    });
    const names = events().map((e) => e.event);
    expect(names.filter((e) => e === "employer_inquiry_submitted")).toHaveLength(1);
    expect(names).toContain("employer_inquiry_submitted_deduped");
    expect(names).toContain("employer_inquiry_log_only");
    expect(names).not.toContain("form_submit");
    const submitted = events().find((e) => e.event === "employer_inquiry_submitted");
    expect(submitted?.lead_reference).toBe("sid_ok");
    expect(submitted?.gclid).toBeUndefined();
    expect(submitted?.email).toBeUndefined();
    expect(submitted?.phone).toBeUndefined();
  });

  it("keeps gclid and UTMs in session storage through a later read", async () => {
    const { captureAttribution, readAttribution } = await import("./tracking");
    const first = captureAttribution("us", { lp_version: AUTHORITATIVE_LP_VERSION });
    expect(first.gclid).toBe("abc");
    expect(first.utm_source).toBe("google");
    expect(first.utm_matchtype).toBe("e");
    expect(first.utm_device).toBe("m");
    expect(first.session_id).toMatch(/^vc_/);
    expect(first.lp_version).toBe(AUTHORITATIVE_LP_VERSION);
    expect(first.baseline_label).toBe(US_BASELINE_LABEL);

    (window as unknown as { location: { href: string; search: string; pathname: string } }).location =
      {
        href: "https://www.virtualcoworker.app/us#gate",
        search: "",
        pathname: "/us",
      };
    const later = readAttribution("us");
    expect(later.gclid).toBe("abc");
    expect(later.utm_campaign).toBe("241");
    expect(later.utm_content).toBe("ag1");
    expect(later.utm_term).toBe("kw");
    expect(later.utm_matchtype).toBe("e");
    expect(later.utm_device).toBe("m");
    expect(later.session_id).toBe(first.session_id);
    expect(later.landing_page_url).toContain("/us");
  });

  it("keeps gclid after the tab session is gone", async () => {
    const { captureAttribution, readAttribution } = await import("./tracking");
    const first = captureAttribution("us");
    expect(first.gclid).toBe("abc");

    window.sessionStorage.clear();
    (window as unknown as { location: { href: string; search: string; pathname: string } }).location =
      {
        href: "https://www.virtualcoworker.app/us",
        search: "",
        pathname: "/us",
      };
    const later = readAttribution("us");
    expect(later.gclid).toBe("abc");
    expect(later.utm_source).toBe("google");
  });
});
