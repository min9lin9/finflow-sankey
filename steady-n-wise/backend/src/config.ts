export const config = {
  backendPort: Number(Bun.env.BACKEND_PORT ?? 3000),
  dataServiceUrl: Bun.env.DATA_SERVICE_URL ?? "http://localhost:8000",
  redisUrl: Bun.env.REDIS_URL ?? "redis://localhost:6379/0",
  cacheTtlSeconds: Number(Bun.env.CACHE_TTL_SECONDS ?? 86400),
};
