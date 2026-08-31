import { describe, expect, it } from "vitest";
import {
  currencyForMarket,
  formatMoney,
  microsToMajor,
  roundMoney,
} from "@/lib/sync/currency";

describe("currencyForMarket", () => {
  it("maps AU → AUD and US → USD", () => {
    expect(currencyForMarket("AU")).toBe("AUD");
    expect(currencyForMarket("au")).toBe("AUD");
    expect(currencyForMarket("US")).toBe("USD");
    expect(currencyForMarket("")).toBe("USD");
  });
});

describe("microsToMajor", () => {
  it("converts Google Ads micros without inventing currency", () => {
    expect(microsToMajor(1_500_000)).toBe(1.5);
    expect(microsToMajor("2500000")).toBe(2.5);
    expect(microsToMajor(null)).toBe(0);
    expect(microsToMajor(undefined)).toBe(0);
  });

  it("preserves AU vs US labeling on format", () => {
    const amount = microsToMajor(12_340_000);
    expect(formatMoney(amount, "USD")).toBe("$12.34");
    expect(formatMoney(amount, "AUD")).toBe("A$12.34");
  });

  it("rounds display money without mutating storage precision path", () => {
    expect(roundMoney(12.345, 2)).toBe(12.35);
    expect(microsToMajor(1)).toBe(0.000001);
  });
});
