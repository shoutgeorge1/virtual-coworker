import { redirect } from "next/navigation";

/** New TF URL was not a live Ads destination. Send visitors to restored /us. */
export default function USVirtualAssistantAgencyRedirect() {
  redirect("/us");
}
