import { redirect } from "next/navigation";

/**
 * IA decision (George): no multi-market corporate hub at `/`.
 * US is the primary paid market — root goes straight to the US micro-site.
 */
export default function RootPage() {
  redirect("/us");
}
