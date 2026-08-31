import { beforeEach, describe, expect, it, vi } from "vitest";
import { DEFAULT_CAREERS_URL } from "../config/markets";

describe("exitToCareers", () => {
  beforeEach(() => {
    vi.resetModules();
    const replace = vi.fn();
    vi.stubGlobal("window", {
      dataLayer: [] as Array<Record<string, unknown>>,
      location: {
        replace,
        href: "https://www.virtualcoworker.app/us",
        search: "",
        pathname: "/us",
      },
    });
    vi.stubGlobal("document", { referrer: "" });
  });

  it("fires job_seeker_redirected then location.replace", async () => {
    const { exitToCareers } = await import("./job-seeker-exit");
    exitToCareers("https://virtualcoworker.com.ph", {
      market: "us",
      source: "lead_gate",
    });
    const dl = (
      window as unknown as { dataLayer: Array<Record<string, unknown>> }
    ).dataLayer;
    const ev = dl.find((e) => e.event === "job_seeker_redirected");
    expect(ev).toMatchObject({
      event: "job_seeker_redirected",
      market: "us",
      redirect_location: "lead_gate",
      redirect_reason: "careers_escape",
      intent: "job_seeker",
      destination: "https://virtualcoworker.com.ph",
      primary_eligible: false,
      bidding_primary: false,
    });
    expect(window.location.replace).toHaveBeenCalledWith(
      "https://virtualcoworker.com.ph",
    );
  });

  it("falls back to the PH careers host when url is empty", async () => {
    const { exitToCareers } = await import("./job-seeker-exit");
    exitToCareers("  ");
    expect(window.location.replace).toHaveBeenCalledWith(DEFAULT_CAREERS_URL);
  });
});
