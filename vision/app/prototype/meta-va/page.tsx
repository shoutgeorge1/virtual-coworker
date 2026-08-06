import type { Metadata } from "next";
import { redirect } from "next/navigation";

export const metadata: Metadata = {
  title: "Retired · Meta VA full-page prototype",
  robots: { index: false, follow: false },
};

/**
 * Retired: George rejected the full-page Meta redesign.
 * Hero overlay A/B lives on real category LPs via ?hero=badge|pill|hot.
 */
export default function MetaVaPrototypeRetired() {
  redirect("/us/digital-marketing?hero=badge&variant=a");
}
