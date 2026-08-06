import { describe, expect, it } from "vitest";
import {
  resolveHeroRateBadge,
  resolveHeroSecondaryBadge,
} from "./hero-badge-copy";

describe("hero badge rates (public Price Guide only)", () => {
  it("uses published digital marketing starting rates", () => {
    const us = resolveHeroRateBadge("us", "digital-marketing");
    expect(us?.prefix).toBe("from");
    expect(us?.amount).toBe("$12");
    expect(us?.unit).toBe("/hr");
    expect(us?.roleLabel).toBe("Digital Marketing Manager");

    const au = resolveHeroRateBadge("au", "digital-marketing");
    expect(au?.amount).toBe("$14");
    expect(au?.unit).toBe("AUD/hr");
  });

  it("uses published accountant starting rates", () => {
    expect(resolveHeroRateBadge("us", "accounting")?.amount).toBe("$10");
    expect(resolveHeroRateBadge("au", "accounting")?.amount).toBe("$12");
  });

  it("does not invent an HR rate", () => {
    expect(resolveHeroRateBadge("us", "hr")).toBeNull();
    expect(resolveHeroSecondaryBadge("us", "hr")).toEqual({
      kind: "ph",
      label: "Philippines",
      sub: "Dedicated hire",
      aria: "Philippines dedicated hire",
    });
  });

  it("falls back to PH dedicated when no category", () => {
    expect(resolveHeroSecondaryBadge("us", null).kind).toBe("ph");
  });
});
