import { redirectPreservingQuery } from "../../../lib/preserve-redirect";

/** Retired Ads challenger alias → Paid Landing Page Baseline v1 (/us). */
export default async function USStartAlias({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  redirectPreservingQuery("/us", await searchParams);
}
