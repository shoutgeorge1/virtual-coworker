import { redactUnknown } from "./redact";

export class QuotaExhaustedError extends Error {
  constructor(message = "Upstream quota exhausted — stop retries") {
    super(message);
    this.name = "QuotaExhaustedError";
  }
}

export type RetryOptions = {
  attempts?: number;
  baseDelayMs?: number;
  shouldRetry?: (err: unknown) => boolean;
  sleep?: (ms: number) => Promise<void>;
};

const defaultSleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

function isQuota(err: unknown): boolean {
  if (err instanceof QuotaExhaustedError) return true;
  const text = redactUnknown(err).toUpperCase();
  return text.includes("RESOURCE_EXHAUSTED") || text.includes("QUOTA");
}

function defaultShouldRetry(err: unknown): boolean {
  if (isQuota(err)) return false;
  const text = redactUnknown(err).toLowerCase();
  if (text.includes("401") || text.includes("unauthorized")) return true;
  if (text.includes("429") || text.includes("rate")) return true;
  if (text.includes("503") || text.includes("502") || text.includes("timeout")) return true;
  if (text.includes("econnreset") || text.includes("fetch failed")) return true;
  return false;
}

/** Retry with exponential backoff. Never retries quota exhaustion. */
export async function withRetry<T>(
  fn: (attempt: number) => Promise<T>,
  opts: RetryOptions = {},
): Promise<T> {
  const attempts = opts.attempts ?? 3;
  const base = opts.baseDelayMs ?? 400;
  const shouldRetry = opts.shouldRetry ?? defaultShouldRetry;
  const sleep = opts.sleep ?? defaultSleep;

  let last: unknown;
  for (let attempt = 1; attempt <= attempts; attempt++) {
    try {
      return await fn(attempt);
    } catch (err) {
      last = err;
      if (isQuota(err)) throw err;
      if (attempt >= attempts || !shouldRetry(err)) throw err;
      await sleep(base * 2 ** (attempt - 1));
    }
  }
  throw last instanceof Error ? last : new Error(redactUnknown(last));
}
