import { describe, expect, it } from "vitest";
import { MARKETS, phoneTelHref, resolvePhone } from "../config/markets";

describe("AU / US phone resolution", () => {
  it("AU knownPhone is George-approved 1300 display", () => {
    expect(MARKETS.au.knownPhone).toBe("1300 886 740");
  });

  it("builds AU 1300 tel href as +61 E.164", () => {
    expect(phoneTelHref("1300 886 740", "au")).toBe("tel:+611300886740");
  });

  it("keeps US national digits in tel href", () => {
    expect(phoneTelHref("(310) 730-9126", "us")).toBe("tel:3107309126");
  });

  it("resolvePhone(au) is configured without env", () => {
    const phone = resolvePhone("au");
    expect(phone.configured).toBe(true);
    expect(phone.display).toBe("1300 886 740");
    expect(phone.href).toBe("tel:+611300886740");
  });

  it("resolvePhone(us) still uses known US line", () => {
    const phone = resolvePhone("us");
    expect(phone.configured).toBe(true);
    expect(phone.display).toBe("(310) 730-9126");
    expect(phone.href).toBe("tel:3107309126");
  });
});
