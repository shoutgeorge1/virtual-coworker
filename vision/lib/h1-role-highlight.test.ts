import { describe, expect, it } from "vitest";
import { CATEGORIES, CATEGORY_SLUGS } from "../config/categories";
import { MARKETS } from "../config/markets";
import { findH1RolePhrase } from "./h1-role-highlight";

describe("highlightH1Role phrases", () => {
  it("highlights market home H1s", () => {
    expect(findH1RolePhrase(MARKETS.us.headline)).toBe("virtual assistants");
    expect(findH1RolePhrase(MARKETS.au.headline)).toBe("virtual assistants");
  });

  it("highlights quiz hero H1", () => {
    expect(
      findH1RolePhrase("Find the right virtual assistant for your business"),
    ).toBe("virtual assistant");
  });

  it("highlights every category variant H1", () => {
    const misses: string[] = [];
    for (const slug of CATEGORY_SLUGS) {
      const cat = CATEGORIES[slug];
      for (const variant of ["a", "b"] as const) {
        for (const market of ["us", "au"] as const) {
          const h1 = cat.variants[variant].h1[market];
          if (!findH1RolePhrase(h1)) {
            misses.push(`${slug}.${variant}.${market}: ${h1}`);
          }
        }
      }
    }
    expect(misses).toEqual([]);
  });
});
