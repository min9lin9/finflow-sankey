import { config } from "./config";

export class UpstreamError extends Error {
  constructor(message: string, readonly status = 502) {
    super(message);
  }
}

export async function fetchJson(path: string): Promise<unknown> {
  const url = `${config.dataServiceUrl}${path}`;
  let lastError: unknown;
  for (let attempt = 0; attempt < 5; attempt += 1) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10_000);
    try {
      const response = await fetch(url, { signal: controller.signal });
      if (response.ok) {
        return await response.json();
      }
      lastError = new UpstreamError(`upstream returned ${response.status}`, response.status);
    } catch (error) {
      lastError = error;
    } finally {
      clearTimeout(timeout);
    }
    const jitter = Math.floor(Math.random() * 50);
    const delay = Math.min(200 * 2 ** attempt, 5_000) + jitter;
    await new Promise((resolve) => setTimeout(resolve, delay));
  }
  throw new UpstreamError(lastError instanceof Error ? lastError.message : "upstream unavailable");
}
