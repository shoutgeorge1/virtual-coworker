"use client";

import { useEffect } from "react";
import { trackValidEmployerSubmit } from "../../lib/tracking";

/** Refresh-safe: primary already deduped by submission id in sessionStorage. */
export default function ThankYouClient({
  market,
  submissionId,
}: {
  market: string;
  submissionId: string;
}) {
  useEffect(() => {
    if (!submissionId || (market !== "us" && market !== "au")) return;
    trackValidEmployerSubmit({ market, submissionId });
  }, [market, submissionId]);

  return null;
}
