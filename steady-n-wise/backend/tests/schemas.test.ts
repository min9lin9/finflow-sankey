import { describe, expect, test } from "bun:test";

import { stockCodeSchema, supplyResponseSchema } from "../src/schemas";

describe("schemas", () => {
  test("accepts valid KRX stock codes", () => {
    expect(stockCodeSchema.parse("005930")).toBe("005930");
  });

  test("rejects malformed KRX stock codes", () => {
    expect(() => stockCodeSchema.parse("ABC")).toThrow();
  });

  test("validates supply responses", () => {
    const parsed = supplyResponseSchema.parse({
      stock_code: "005930",
      start_date: "2026-01-02",
      end_date: "2026-01-02",
      data: [
        {
          date: "2026-01-02",
          market_cap: 1,
          foreign_net: 1,
          institution_net: 1,
          supply_ratio: 2,
          ema12: 2,
          ema26: 2,
          macd: 0,
          signal: 0,
          oscillator: 0,
        },
      ],
    });

    expect(parsed.stock_code).toBe("005930");
  });
});
