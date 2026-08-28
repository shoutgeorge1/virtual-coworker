import { describe, expect, it } from "vitest";
import {
  attributionCoverage,
  blendedCostPerDiscovery,
  blendedCostPerEnquiry,
  blendedCostPerJobOrder,
  blendedCostPerPlacement,
  compareRateToAgency,
  currencyForMarket,
  elapsedDays,
  formatRatioDisplay,
  monthBounds,
  monthOverMonthCompare,
  perThousand,
  periodActivityRate,
  safeDiv,
  sumAdsByDate,
  sumSalesLabeled,
} from "@/lib/executive/metrics";

describe("safeDiv / blended costs", () => {
  it("computes blended cost per enquiry", () => {
    const r = blendedCostPerEnquiry(2036.15, 13);
    expect(r.status).toBe("ok");
    expect(r.value).toBeCloseTo(156.6269, 2);
  });

  it("returns — path for zero denominator", () => {
    const r = blendedCostPerDiscovery(500, 0);
    expect(r.value).toBeNull();
    expect(r.status).toBe("zero_denom");
    expect(formatRatioDisplay(r, "USD")).toBe("—");
  });

  it("never returns Infinity or NaN", () => {
    expect(safeDiv(10, 0).value).toBeNull();
    expect(safeDiv(NaN, 5).value).toBeNull();
    expect(blendedCostPerJobOrder(100, null).status).toBe("pending");
    expect(blendedCostPerPlacement(null, 2).status).toBe("pending");
  });
});

describe("perThousand", () => {
  it("scales outcomes per $1000 spend", () => {
    const r = perThousand(13, 2036.15);
    expect(r.value).toBeCloseTo(6.385, 2);
  });
});

describe("attributionCoverage", () => {
  it("marks sparse GCLID coverage as not reliable", () => {
    const a = attributionCoverage(5, 33);
    expect(a.status).toBe("not_reliable");
    expect(a.display).toBe("Not reliable yet");
    expect(a.coverage).toBeCloseTo(5 / 33, 4);
  });

  it("accepts sufficient coverage", () => {
    const a = attributionCoverage(20, 40);
    expect(a.status).toBe("ok");
    expect(a.display).toBe("50%");
  });
});

describe("monthBounds", () => {
  it("labels current partial month as month to date", () => {
    const p = monthBounds("2026-08-27", "2026-08");
    expect(p.partial).toBe(true);
    expect(p.start).toBe("2026-08-01");
    expect(p.end).toBe("2026-08-27");
    expect(p.label).toContain("to date");
    expect(p.statusLabel).toContain("Partial through");
  });

  it("freezes completed months", () => {
    const p = monthBounds("2026-09-05", "2026-08");
    expect(p.partial).toBe(false);
    expect(p.end).toBe("2026-08-31");
    expect(p.statusLabel).toContain("Completed");
  });
});

describe("elapsedDays", () => {
  it("counts inclusive days", () => {
    expect(elapsedDays("2026-08-01", "2026-08-27")).toBe(27);
  });
});

describe("sumAdsByDate", () => {
  it("sums Stage-1 spend in range with market currency", () => {
    const by = {
      "2026-08-01": { cost_usd: 100, clicks: 10, impressions: 100 },
      "2026-08-15": { cost_usd: 200, clicks: 20, impressions: 200 },
      "2026-07-31": { cost_usd: 999, clicks: 1, impressions: 1 },
    };
    const t = sumAdsByDate(by, "2026-08-01", "2026-08-27", "USD");
    expect(t?.spend).toBe(300);
    expect(t?.clicks).toBe(30);
    expect(t?.currency).toBe("USD");
    expect(t?.ctrPct).toBeCloseTo(10, 5);
  });
});

describe("sumSalesLabeled", () => {
  it("adds non-overlapping weeks inside the month", () => {
    const funnel = sumSalesLabeled(
      [
        {
          window_start: "2026-08-10",
          window_end: "2026-08-16",
          enquiries: 18,
          sales_calls_completed: 9,
          job_orders_total: 0,
          placements: 0,
        },
        {
          window_start: "2026-08-17",
          window_end: "2026-08-23",
          enquiries: 13,
          sales_calls_completed: 7,
          job_orders_total: 0,
          placements: 0,
        },
        {
          window_start: "2026-08-24",
          window_end: "2026-08-25",
          enquiries: 0,
          sales_calls_completed: 0,
          caveat: "Mon–Tue enquiry count pending",
        },
      ],
      "2026-08-01",
      "2026-08-27",
    );
    expect(funnel.enquiries).toBe(31);
    expect(funnel.discoveries).toBe(16);
    expect(funnel.enquiriesPending).toBeFalsy();
  });

  it("marks pending when only pending slices contribute enquiries", () => {
    const funnel = sumSalesLabeled(
      [
        {
          window_start: "2026-08-24",
          window_end: "2026-08-25",
          enquiries: 0,
          caveat: "enquiry count pending",
        },
      ],
      "2026-08-01",
      "2026-08-27",
    );
    expect(funnel.enquiriesPending).toBe(true);
    expect(funnel.source).toBe("Pending");
  });
});

describe("monthOverMonthCompare", () => {
  it("blocks MoM when no prior pilot month", () => {
    const c = monthOverMonthCompare(100, 50, {
      hasPriorPilotMonth: false,
      currentPartial: true,
      higherIsBetter: true,
    });
    expect(c.text).toContain("First pilot month");
    expect(c.status).toBe("no_compare");
  });
});

describe("compareRateToAgency", () => {
  it("marks materially lower cost as good", () => {
    const c = compareRateToAgency(156.63, 707.45, {
      lowerIsBetter: true,
      pilotPeriod: "Aug 2026 MTD",
      agencyPeriod: "typical 7d 2024-08→2026-08",
    });
    expect(c.tone).toBe("good");
    expect(c.metricKind).toBe("rate");
  });
});

describe("periodActivityRate", () => {
  it("labels same-period conversion as not a mature cohort", () => {
    const r = periodActivityRate(13, 7);
    expect(r.value).toBeCloseTo(7 / 13, 4);
    expect(r.label).toContain("not a mature");
  });
});

describe("currencyForMarket", () => {
  it("keeps US/AU currencies separate", () => {
    expect(currencyForMarket("US")).toBe("USD");
    expect(currencyForMarket("AU")).toBe("AUD");
  });
});

describe("reconciliation: 49 MTD enquiries vs 31 census rows", () => {
  it("sums 31 US enquiries and 18 AU enquiries to 49 cumulative pilot enquiries", () => {
    const usSlices = [
      { window_start: "2026-08-10", window_end: "2026-08-16", enquiries: 18, sales_calls_completed: 9 },
      { window_start: "2026-08-17", window_end: "2026-08-23", enquiries: 13, sales_calls_completed: 7 },
      { window_start: "2026-08-24", window_end: "2026-08-25", enquiries: 0, caveat: "enquiry count pending" },
    ];
    const auSlices = [
      { window_start: "2026-08-10", window_end: "2026-08-16", enquiries: 8, sales_calls_completed: 5, job_orders_total: 6, placements: 4 },
      { window_start: "2026-08-17", window_end: "2026-08-23", enquiries: 8, sales_calls_completed: 7, job_orders_total: 0, placements: 0 },
      { window_start: "2026-08-24", window_end: "2026-08-25", enquiries: 2, sales_calls_completed: 0, job_orders_total: 1, placements: 0 },
    ];

    const usFunnel = sumSalesLabeled(usSlices, "2026-08-01", "2026-08-27");
    const auFunnel = sumSalesLabeled(auSlices, "2026-08-01", "2026-08-27");

    expect(usFunnel.enquiries).toBe(31);
    expect(usFunnel.discoveries).toBe(16);
    expect(auFunnel.enquiries).toBe(18);
    expect(auFunnel.discoveries).toBe(12);
    expect(auFunnel.jobOrders).toBe(7);
    expect(auFunnel.placements).toBe(4);

    const totalEnquiries = (usFunnel.enquiries || 0) + (auFunnel.enquiries || 0);
    expect(totalEnquiries).toBe(49);
  });

  it("distinguishes 31 single-week Zoho census rows from 49 cumulative enquiries", () => {
    const usCensusRows = 20;
    const auCensusRows = 11;
    const totalCensusRows = usCensusRows + auCensusRows; // 31
    expect(totalCensusRows).toBe(31);

    const usGclid = 2;
    const auGclid = 3;
    const totalGclid = usGclid + auGclid; // 5
    expect(totalGclid).toBe(5);

    const cov = attributionCoverage(totalGclid, totalCensusRows);
    expect(cov.status).toBe("not_reliable");
    expect(cov.paidAttributed).toBe(5);
    expect(cov.validatedSalesRecords).toBe(31);
    expect(cov.coverage).toBeCloseTo(5 / 31, 4);
  });
});

