export type Period = "1M" | "3M" | "6M" | "1Y" | "ALL";

const periodDays: Record<Exclude<Period, "ALL">, number> = {
  "1M": 31,
  "3M": 92,
  "6M": 183,
  "1Y": 366,
};

export function toDateRange(period: Period, today = new Date()): { start: string; end: string } {
  if (period === "ALL") {
    return { start: "", end: "" };
  }
  const end = new Date(today);
  const start = new Date(today);
  start.setDate(start.getDate() - periodDays[period]);
  return {
    start: start.toISOString().slice(0, 10),
    end: end.toISOString().slice(0, 10),
  };
}
