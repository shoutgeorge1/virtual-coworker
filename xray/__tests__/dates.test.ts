import { describe, expect, it } from "vitest";
import {
  inclusiveDayCount,
  parseUtcDateString,
  previousCompleteDayWindow,
  toUtcDateString,
} from "@/lib/sync/dates";

describe("previousCompleteDayWindow", () => {
  it("excludes today and returns 14 UTC days ending yesterday", () => {
    // Friday 2026-08-21 12:30 UTC → yesterday = 2026-08-20; 14 days → 2026-08-07..2026-08-20
    const asOf = new Date(Date.UTC(2026, 7, 21, 12, 30, 0));
    const w = previousCompleteDayWindow(asOf, 14);
    expect(w.start).toBe("2026-08-07");
    expect(w.end).toBe("2026-08-20");
    expect(w.days).toHaveLength(14);
    expect(w.days[0]).toBe("2026-08-07");
    expect(w.days[13]).toBe("2026-08-20");
    expect(w.days).not.toContain("2026-08-21");
  });

  it("handles month boundaries", () => {
    const asOf = new Date(Date.UTC(2026, 2, 5, 0, 0, 0)); // Mar 5
    const w = previousCompleteDayWindow(asOf, 7);
    expect(w.end).toBe("2026-03-04");
    expect(w.start).toBe("2026-02-26");
    expect(inclusiveDayCount(w.start, w.end)).toBe(7);
  });

  it("rejects invalid dayCount", () => {
    expect(() => previousCompleteDayWindow(new Date(), 0)).toThrow();
  });
});

describe("UTC date parse/format", () => {
  it("round-trips YYYY-MM-DD", () => {
    const d = parseUtcDateString("2026-08-15");
    expect(toUtcDateString(d)).toBe("2026-08-15");
  });

  it("rejects invalid calendar dates", () => {
    expect(() => parseUtcDateString("2026-02-30")).toThrow();
    expect(() => parseUtcDateString("nope")).toThrow();
  });
});
