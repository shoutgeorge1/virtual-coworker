import { cookies } from "next/headers";
import { AB_COOKIE, assignVariant, normalizeVariant } from "./ab-variant";
import type { AbVariant } from "../config/categories";

/** Server-side variant resolution — matches middleware cookie to avoid hydration mismatch. */
export async function resolveLpVariant(
  searchParams?: { variant?: string | string[] },
): Promise<AbVariant> {
  const qRaw = searchParams?.variant;
  const q = Array.isArray(qRaw) ? qRaw[0] : qRaw;
  const jar = await cookies();
  const cookieVal = jar.get(AB_COOKIE)?.value;
  const { variant } = assignVariant({
    queryVariant: normalizeVariant(q),
    cookieVariant: normalizeVariant(cookieVal),
    seed: "ssr-fallback-a",
  });
  return variant;
}
