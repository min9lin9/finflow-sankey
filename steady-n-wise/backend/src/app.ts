import cors from "@elysiajs/cors";
import { Elysia, t } from "elysia";

import type { CacheStore } from "./cache";
import { config } from "./config";
import { fetchJson } from "./dataService";
import { searchResultSchema, stockCodeSchema, supplyResponseSchema } from "./schemas";
import { singleFlight } from "./singleFlight";

export function createApp(cache: CacheStore) {
  return new Elysia()
    .use(cors())
    .get("/health", async () => {
      let redis = "connected";
      try {
        await cache.ping();
      } catch {
        redis = "disconnected";
      }
      return {
        status: "ok",
        redis,
        dataService: "unknown",
        timestamp: new Date().toISOString(),
      };
    })
    .get(
      "/api/v1/stocks/search",
      async ({ query, set }) => {
        const q = query.q.trim();
        const data = await fetchJson(`/stocks/search?q=${encodeURIComponent(q)}`);
        const parsed = searchResultSchema.array().safeParse(data);
        if (!parsed.success) {
          set.status = 502;
          return { error: "UPSTREAM_SCHEMA_MISMATCH" };
        }
        return parsed.data;
      },
      {
        query: t.Object({
          q: t.String({ minLength: 1, maxLength: 30 }),
        }),
      },
    )
    .get(
      "/api/v1/stocks/:stock_code/supply-analysis",
      async ({ params, query, set }) => {
        const code = stockCodeSchema.parse(params.stock_code);
        const start = query.start ?? "";
        const end = query.end ?? "";
        const cacheKey = `supply:${code}:${start}:${end}`;
        const cached = await cache.get(cacheKey).catch(() => null);
        if (cached) {
          return JSON.parse(cached);
        }

        const path =
          `/stocks/${code}/supply-analysis?start=${encodeURIComponent(start)}` +
          `&end=${encodeURIComponent(end)}`;

        try {
          const data = await singleFlight(cacheKey, () => fetchJson(path));
          const parsed = supplyResponseSchema.parse(data);
          await cache.setex(cacheKey, config.cacheTtlSeconds, JSON.stringify(parsed)).catch(() => null);
          return parsed;
        } catch {
          const fallback = await cache.get(cacheKey).catch(() => null);
          set.status = fallback ? 200 : 502;
          if (fallback) {
            return { ...JSON.parse(fallback), warning: "UPSTREAM_UNAVAILABLE" };
          }
          return { error: "UPSTREAM_UNAVAILABLE" };
        }
      },
      {
        params: t.Object({
          stock_code: t.String({ pattern: "^\\d{6}$" }),
        }),
        query: t.Object({
          start: t.Optional(t.String()),
          end: t.Optional(t.String()),
        }),
      },
    );
}
