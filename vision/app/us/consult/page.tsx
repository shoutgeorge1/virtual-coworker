import { redirect } from "next/navigation";

/** Legacy consult path — no SaaS "book a demo". Send to employer hire form. */
export default function USConsultRedirect() {
  redirect("/us#gate");
}
