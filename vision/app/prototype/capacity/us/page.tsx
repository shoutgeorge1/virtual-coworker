import { redirect } from "next/navigation";
import { CAPACITY_CHALLENGER_PATHS } from "../../../../config/lp-challenger-capacity";

/** Alias only. Ads Final URL is /us/capacity. */
export default function CapacityUsAlias() {
  redirect(CAPACITY_CHALLENGER_PATHS.us);
}
