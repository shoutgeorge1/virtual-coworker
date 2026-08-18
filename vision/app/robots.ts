import type { MetadataRoute } from "next";
import { SITE_URL, isPilotNoindex } from "../lib/seo";

export default function robots(): MetadataRoute.Robots {
  if (isPilotNoindex()) {
    return {
      rules: { userAgent: "*", disallow: "/" },
      sitemap: `${SITE_URL}/sitemap.xml`,
      host: SITE_URL,
    };
  }

  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: [
          "/thank-you",
          "/api/",
          "/prototype/",
          "/preview/",
          "/ph",
          "/ph/",
          "/us/consult",
          "/au/consult",
        ],
      },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL,
  };
}
