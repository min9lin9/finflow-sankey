const inFlight = new Map<string, Promise<unknown>>();

export async function singleFlight<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const pending = inFlight.get(key);
  if (pending) {
    return pending as Promise<T>;
  }
  const next = fetcher().finally(() => inFlight.delete(key));
  inFlight.set(key, next);
  return next;
}
