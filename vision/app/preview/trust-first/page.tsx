import type { Metadata } from "next";
import PreviewIndex from "../../components/trust-first/PreviewIndex";
import { previewRobots } from "../../../lib/trust-first";

export const metadata: Metadata = {
  title: "Trust-first preview index | Virtual Coworker",
  description: "Internal review dashboard for US trust-first landing page challengers.",
  robots: previewRobots(),
};

export default function TrustFirstIndexPage() {
  return <PreviewIndex />;
}
