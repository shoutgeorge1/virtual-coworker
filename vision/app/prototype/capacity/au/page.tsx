import { redirect } from "next/navigation";
import { CAPACITY_CHALLENGER_PATHS } from "../../../../config/lp-challenger-capacity";

/** Alias only. Ads Final URL is /au/capacity. */
export default function CapacityAuAlias() {
  redirect(CAPACITY_CHALLENGER_PATHS.au);
}
