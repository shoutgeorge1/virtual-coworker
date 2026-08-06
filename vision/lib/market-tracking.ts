/**
 * Three micro-site identities → separate tracking placeholders.
 * Never assume one GTM/GA4 container for US + AU + PH.
 *
 * Env (optional; leave empty until containers exist):
 *   NEXT_PUBLIC_GTM_US / NEXT_PUBLIC_GTM_AU / NEXT_PUBLIC_GTM_PH
 *   NEXT_PUBLIC_GA4_US / NEXT_PUBLIC_GA4_AU / NEXT_PUBLIC_GA4_PH
 * Legacy fallback: NEXT_PUBLIC_GTM_ID / NEXT_PUBLIC_GA4_ID (US-only if set)
 */

export type TrackingSurface = "us" | "au" | "ph";

export function resolveGtmId(surface: TrackingSurface): string {
  const per =
    surface === "us"
      ? process.env.NEXT_PUBLIC_GTM_US
      : surface === "au"
        ? process.env.NEXT_PUBLIC_GTM_AU
        : process.env.NEXT_PUBLIC_GTM_PH;
  const trimmed = (per || "").trim();
  if (trimmed) return trimmed;
  // Legacy single container — only as US fallback; never for AU/PH.
  if (surface === "us") return (process.env.NEXT_PUBLIC_GTM_ID || "").trim();
  return "";
}

export function resolveGa4Id(surface: TrackingSurface): string {
  const per =
    surface === "us"
      ? process.env.NEXT_PUBLIC_GA4_US
      : surface === "au"
        ? process.env.NEXT_PUBLIC_GA4_AU
        : process.env.NEXT_PUBLIC_GA4_PH;
  const trimmed = (per || "").trim();
  if (trimmed) return trimmed;
  if (surface === "us") return (process.env.NEXT_PUBLIC_GA4_ID || "").trim();
  return "";
}
