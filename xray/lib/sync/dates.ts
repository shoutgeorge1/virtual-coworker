/** Calendar-day helpers for the daily sync window (UTC). */

const DAY_MS = 24 * 60 * 60 * 1000;

function pad(n: number): string {
  return String(n).padStart(2, "0");
}

/** Format a Date as YYYY-MM-DD in UTC. */
export function toUtcDateString(d: Date): string {
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`;
}

/** Parse YYYY-MM-DD as UTC midnight. */
export function parseUtcDateString(isoDate: string): Date {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(isoDate.trim());
  if (!m) throw new Error(`Invalid UTC date string: ${isoDate}`);
  const y = Number(m[1]);
  const mo = Number(m[2]);
  const day = Number(m[3]);
  const d = new Date(Date.UTC(y, mo - 1, day));
  if (
    d.getUTCFullYear() !== y ||
    d.getUTCMonth() !== mo - 1 ||
    d.getUTCDate() !== day
  ) {
    throw new Error(`Invalid calendar date: ${isoDate}`);
  }
  return d;
}

/**
 * Previous N complete calendar days ending yesterday (UTC).
 * Today is excluded so delayed conversions can settle into closed days.
 */
export function previousCompleteDayWindow(
  asOf: Date = new Date(),
  dayCount = 14,
): { start: string; end: string; days: string[] } {
  if (!Number.isInteger(dayCount) || dayCount < 1) {
    throw new Error("dayCount must be a positive integer");
  }
  const todayUtc = Date.UTC(
    asOf.getUTCFullYear(),
    asOf.getUTCMonth(),
    asOf.getUTCDate(),
  );
  const endMs = todayUtc - DAY_MS;
  const startMs = endMs - (dayCount - 1) * DAY_MS;
  const days: string[] = [];
  for (let i = 0; i < dayCount; i++) {
    days.push(toUtcDateString(new Date(startMs + i * DAY_MS)));
  }
  return {
    start: days[0]!,
    end: days[days.length - 1]!,
    days,
  };
}

export function inclusiveDayCount(start: string, end: string): number {
  const a = parseUtcDateString(start).getTime();
  const b = parseUtcDateString(end).getTime();
  if (b < a) throw new Error("end before start");
  return Math.floor((b - a) / DAY_MS) + 1;
}
