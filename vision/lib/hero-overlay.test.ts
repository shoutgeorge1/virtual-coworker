import { describe, expect, it } from "vitest";
import { normalizeHeroOverlay } from "./hero-overlay";

describe("hero overlay", () => {
  it("defaults to none", () => {
    expect(normalizeHeroOverlay(undefined)).toBe("none");
    expect(normalizeHeroOverlay(null)).toBe("none");
    expect(normalizeHeroOverlay("")).toBe("none");
    expect(normalizeHeroOverlay("flag")).toBe("none");
  });

  it("accepts badge|pill|hot", () => {
    expect(normalizeHeroOverlay("badge")).toBe("badge");
    expect(normalizeHeroOverlay("PILL")).toBe("pill");
    expect(normalizeHeroOverlay(["hot"])).toBe("hot");
  });
});
