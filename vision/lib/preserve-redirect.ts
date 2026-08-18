import { redirect } from "next/navigation";

/** 308-style App Router redirect that keeps GCLID / UTM / variant query string. */
export function redirectPreservingQuery(
  targetPath: string,
  searchParams: Record<string, string | string[] | undefined>,
): never {
  const q = new URLSearchParams();
  for (const [key, value] of Object.entries(searchParams)) {
    if (typeof value === "string") q.set(key, value);
    else if (Array.isArray(value)) {
      for (const item of value) q.append(key, item);
    }
  }
  const qs = q.toString();
  redirect(qs ? `${targetPath}?${qs}` : targetPath);
}
