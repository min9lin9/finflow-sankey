import Redis from "ioredis";

import { config } from "./config";

export interface CacheStore {
  get(key: string): Promise<string | null>;
  setex(key: string, ttlSeconds: number, value: string): Promise<unknown>;
  ping(): Promise<string>;
}

export function createRedis(): CacheStore {
  return new Redis(config.redisUrl, {
    lazyConnect: true,
    maxRetriesPerRequest: 1,
  });
}
