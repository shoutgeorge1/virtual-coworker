/** Simple in-memory rate limit + duplicate window (single-instance). */

type Hit = { count: number; resetAt: number };
type Dup = { at: number; submissionId: string };

const hits = new Map<string, Hit>();
const recent = new Map<string, Dup>();

const WINDOW_MS = 60_000;
const MAX_PER_WINDOW = 8;
const DUP_MS = 10 * 60 * 1000;

export function rateLimitAllow(key: string): boolean {
  const now = Date.now();
  const cur = hits.get(key);
  if (!cur || now > cur.resetAt) {
    hits.set(key, { count: 1, resetAt: now + WINDOW_MS });
    return true;
  }
  if (cur.count >= MAX_PER_WINDOW) return false;
  cur.count += 1;
  return true;
}

export function checkDuplicate(
  key: string,
): { duplicate: true; submissionId: string } | { duplicate: false } {
  const now = Date.now();
  const prev = recent.get(key);
  if (prev && now - prev.at < DUP_MS) {
    return { duplicate: true, submissionId: prev.submissionId };
  }
  return { duplicate: false };
}

export function rememberSubmission(key: string, submissionId: string) {
  recent.set(key, { at: Date.now(), submissionId });
  // Bound map size
  if (recent.size > 2000) {
    const oldest = [...recent.entries()].sort((a, b) => a[1].at - b[1].at).slice(0, 500);
    for (const [k] of oldest) recent.delete(k);
  }
}

/** Test helpers */
export function _resetLimitsForTests() {
  hits.clear();
  recent.clear();
}
