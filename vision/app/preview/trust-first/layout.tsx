import type { Metadata } from "next";
import { Suspense } from "react";
import PreviewVariantToolbar from "../../components/trust-first/PreviewVariantToolbar";
import { previewRobots } from "../../../lib/trust-first";
import "./trust-first.css";

export const metadata: Metadata = {
  title: "Trust-first US preview | Virtual Coworker",
  robots: previewRobots(),
};

/**
 * Isolated preview shell.
 * No MarketGtm. No production nav. No Ads conversion tags.
 */
export default function TrustFirstPreviewLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Suspense fallback={null}>
        <PreviewVariantToolbar />
      </Suspense>
      {children}
    </>
  );
}
