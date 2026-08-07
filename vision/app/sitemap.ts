import type { MetadataRoute } from "next";
import { SITE_URL, isPilotNoindex, sitemapPaths } from "../lib/seo";

export default function sitemap(): MetadataRoute.Sitemap {
  if (isPilotNoindex()) return [];

  const now = new Date();
  return sitemapPaths().map(({ path, priority }) => ({
    url: `${SITE_URL}${path}`,
    lastModified: now,
    changeFrequency: path === "/us" || path === "/au" ? "weekly" : "monthly",
    priority,
  }));
}
