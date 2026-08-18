import { redirectPreservingQuery } from "../../../lib/preserve-redirect";

/** Retired Ads challenger alias → Paid Landing Page Baseline v1 (/au). */
export default async function AUCapacityAlias({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  redirectPreservingQuery("/au", await searchParams);
}
