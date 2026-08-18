import { redirectPreservingQuery } from "../../../../lib/preserve-redirect";

/** Approved challenger preview → production baseline /us. Query string preserved. */
export default async function StaffingPartnerPrototypeRedirect({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  redirectPreservingQuery("/us", await searchParams);
}
