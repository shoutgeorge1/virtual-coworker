import { redirect } from "next/navigation";

/** App Router root — send browsers to the existing static command center. */
export default function Home() {
  redirect("/launch-control");
}
