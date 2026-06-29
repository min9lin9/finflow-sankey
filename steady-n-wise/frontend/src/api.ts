import { z } from "zod";

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:3000";

export const searchResultSchema = z.object({
  code: z.string().regex(/^\d{6}$/),
  name: z.string(),
});

export const supplyPointSchema = z.object({
  date: z.string(),
  market_cap: z.number(),
  foreign_net: z.number(),
  institution_net: z.number(),
  supply_ratio: z.number(),
  ema12: z.number(),
  ema26: z.number(),
  macd: z.number(),
  signal: z.number(),
  oscillator: z.number(),
});

export const supplyResponseSchema = z.object({
  stock_code: z.string().regex(/^\d{6}$/),
  start_date: z.string(),
  end_date: z.string(),
  data: z.array(supplyPointSchema).min(1),
});

export type StockSearchResult = z.infer<typeof searchResultSchema>;
export type SupplyResponse = z.infer<typeof supplyResponseSchema>;

export async function searchStocks(query: string): Promise<StockSearchResult[]> {
  const response = await fetch(`${apiBase}/api/v1/stocks/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error("검색을 불러오지 못했습니다.");
  }
  return searchResultSchema.array().parse(await response.json());
}

export async function fetchSupplyAnalysis(
  code: string,
  range: { start: string; end: string },
): Promise<SupplyResponse> {
  const params = new URLSearchParams(range);
  const response = await fetch(`${apiBase}/api/v1/stocks/${code}/supply-analysis?${params}`);
  if (!response.ok) {
    throw new Error("차트 데이터를 불러오지 못했습니다.");
  }
  return supplyResponseSchema.parse(await response.json());
}
