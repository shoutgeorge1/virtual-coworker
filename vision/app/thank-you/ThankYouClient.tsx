"use client";

import { useEffect } from "react";
import { trackValidEmployerSubmit } from "../../lib/tracking";

/** Refresh-safe: primary already deduped by submission id in sessionStorage. */
export default function ThankYouClient({
  market,
  submissionId,
  conversionEligible = true,
}: {
  market: string;
  submissionId: string;
  conversionEligible?: boolean;
}) {
  useEffect(() => {
    if (!submissionId || (market !== "us" && market !== "au")) return;
    trackValidEmployerSubmit({
      market,
      submissionId,
      conversionEligible,
    });
  }, [market, submissionId, conversionEligible]);

  return null;
}
