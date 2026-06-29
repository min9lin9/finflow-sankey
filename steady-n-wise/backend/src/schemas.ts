import { z } from "zod";

export const stockCodeSchema = z.string().regex(/^\d{6}$/);
export const isoDateSchema = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);

export const searchResultSchema = z.object({
  code: stockCodeSchema,
  name: z.string().min(1),
});

export const supplyPointSchema = z.object({
  date: isoDateSchema,
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
  stock_code: stockCodeSchema,
  start_date: isoDateSchema,
  end_date: isoDateSchema,
  data: z.array(supplyPointSchema).min(1),
});

export type SearchResult = z.infer<typeof searchResultSchema>;
export type SupplyResponse = z.infer<typeof supplyResponseSchema>;
