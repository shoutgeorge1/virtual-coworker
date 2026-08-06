import { redirect } from "next/navigation";

/**
 * Legacy consult path — no SaaS "book a demo". Send to employer hire form.
 * Use ?focus=gate (not #gate): HTTP redirects strip URL fragments.
 */
export default function AUConsultRedirect() {
  redirect("/au?focus=gate");
}
