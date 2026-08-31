import { describe, expect, it } from "vitest";
import {
  assignVariant,
  LP_CREATIVE_AB_LIVE,
  normalizeVariant,
  variantFromSeed,
} from "./ab-variant";
import { CATEGORY_SLUGS, resolveCategoryParam } from "../config/categories";

describe("ab variant", () => {
  it("is parked — freeze to A unless query override", () => {
    expect(LP_CREATIVE_AB_LIVE).toBe(false);
  });

  it("normalizes a|b only", () => {
    expect(normalizeVariant("A")).toBe("a");
    expect(normalizeVariant("b")).toBe("b");
    expect(normalizeVariant("c")).toBeNull();
  });

  it("query override wins", () => {
    const r = assignVariant({
      queryVariant: "b",
      cookieVariant: "a",
      seed: "x",
    });
    expect(r).toEqual({ variant: "b", source: "query" });
  });

  it("parked: ignores old B cookie and freezes to A", () => {
    const r = assignVariant({
      queryVariant: null,
      cookieVariant: "b",
      seed: "x",
    });
    expect(r).toEqual({ variant: "a", source: "assigned" });
  });

  it("seed assignment is stable", () => {
    expect(variantFromSeed("stable-seed-1")).toBe(variantFromSeed("stable-seed-1"));
  });

  it("roughly splits seeds ~50/50", () => {
    let a = 0;
    let b = 0;
    for (let i = 0; i < 200; i++) {
      if (variantFromSeed(`seed_${i}`)) {
        /* noop for type */
      }
      const v = variantFromSeed(`seed_${i}`);
      if (v === "a") a++;
      else b++;
    }
    expect(a).toBeGreaterThan(70);
    expect(b).toBeGreaterThan(70);
  });
});

describe("category slugs", () => {
  it("has exactly 9 categories", () => {
    expect(CATEGORY_SLUGS).toHaveLength(9);
  });

  it("maps legacy role params", () => {
    expect(resolveCategoryParam("administration")).toBe("administrative-support");
    expect(resolveCategoryParam("digital_marketing")).toBe("digital-marketing");
    expect(resolveCategoryParam("customer_service")).toBe("customer-service");
  });
});
