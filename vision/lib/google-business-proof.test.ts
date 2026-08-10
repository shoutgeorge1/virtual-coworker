import { describe, expect, it } from "vitest";
import { TRUST_PROOF, googleBusinessForMarket } from "../config/site";
import { resolvePhone } from "../config/markets";

describe("Google Business Profile proof vs site phones", () => {
  it("US is 5.0 / 39 and does not change the verified 888 site phone", () => {
    const gbp = googleBusinessForMarket("us");
    expect(gbp.rating).toBe("5.0");
    expect(gbp.reviewCount).toBe(39);
    expect(gbp.label).toBe("Google");
    const phone = resolvePhone("us");
    expect(phone.display).toBe("(888) 964-8644");
    expect(phone.href).toBe("tel:+18889648644");
  });

  it("AU is 4.8 / 23 and keeps 1300 886 740", () => {
    const gbp = googleBusinessForMarket("au");
    expect(gbp.rating).toBe("4.8");
    expect(gbp.reviewCount).toBe(23);
    expect(gbp.label).toBe("Google");
    const phone = resolvePhone("au");
    expect(phone.display).toBe("1300 886 740");
    expect(phone.href).toBe("tel:+611300886740");
  });

  it("Clutch stays 4.9 / 7 from TRUST_PROOF", () => {
    expect(TRUST_PROOF.clutch.rating).toBe("4.9");
    expect(TRUST_PROOF.clutch.reviewCount).toBe(7);
    expect(TRUST_PROOF.clutch.label).toBe("Clutch");
  });
});
