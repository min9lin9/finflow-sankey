import { describe, expect, test } from "bun:test";

import { toDateRange } from "../src/dateRange";

describe("toDateRange", () => {
  test("uses empty params for ALL", () => {
    expect(toDateRange("ALL")).toEqual({ start: "", end: "" });
  });

  test("calculates 6M from a supplied date", () => {
    expect(toDateRange("6M", new Date("2026-06-29T00:00:00Z"))).toEqual({
      start: "2025-12-28",
      end: "2026-06-29",
    });
  });
});
