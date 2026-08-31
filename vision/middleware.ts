import { NextRequest, NextResponse } from "next/server";
import { AB_COOKIE, assignVariant, normalizeVariant } from "./lib/ab-variant";

const ROLE_REDIRECT: Record<string, string> = {
  digital_marketing: "digital-marketing",
  "digital-marketing": "digital-marketing",
  social_media: "social-media",
  "social-media": "social-media",
  accounting: "accounting",
  bookkeeping: "bookkeeping",
  administration: "administrative-support",
  admin: "administrative-support",
  "administrative-support": "administrative-support",
  administrative_support: "administrative-support",
  customer_service: "customer-service",
  "customer-service": "customer-service",
  hr: "hr",
  "human-resources": "hr",
  human_resources: "hr",
  recruitment: "recruitment",
  recruiting: "recruitment",
  sales: "sales",
};

const US_ONLY_ROLE_REDIRECT: Record<string, string> = {
  "real-estate": "real-estate",
  real_estate: "real-estate",
  realestate: "real-estate",
};

export function middleware(req: NextRequest) {
  const { pathname, searchParams } = req.nextUrl;

  // Canonical HR slug: /{us|au}/human-resources → /{us|au}/hr
  // Preserve GCLID / WBRAID / GBRAID / UTMs / variant query string.
  const hrAlias = pathname.match(/^\/(us|au)\/human-resources\/?$/i);
  if (hrAlias) {
    const url = req.nextUrl.clone();
    url.pathname = `/${hrAlias[1]}/hr`;
    const res = NextResponse.redirect(url, 308);
    return withAbCookie(req, res);
  }

  // Backward-compat: /us?role=bookkeeping → /us/bookkeeping (preserve other params)
  if (pathname === "/us" || pathname === "/au") {
    const role = searchParams.get("role");
    if (role) {
      const key = role.trim().toLowerCase();
      const slug =
        (pathname === "/us" ? US_ONLY_ROLE_REDIRECT[key] : undefined) ||
        ROLE_REDIRECT[key];
      if (slug) {
        const url = req.nextUrl.clone();
        url.pathname = `${pathname}/${slug}`;
        url.searchParams.delete("role");
        const res = NextResponse.redirect(url, 308);
        return withAbCookie(req, res);
      }
    }
  }

  const res = NextResponse.next();
  return withAbCookie(req, res);
}

function withAbCookie(req: NextRequest, res: NextResponse): NextResponse {
  const q = normalizeVariant(req.nextUrl.searchParams.get("variant"));
  const existing = normalizeVariant(req.cookies.get(AB_COOKIE)?.value);
  const { variant } = assignVariant({
    queryVariant: q,
    cookieVariant: existing,
    seed: `${Date.now()}_${Math.random().toString(36).slice(2)}`,
  });

  // Refresh when QA override, missing cookie, or parked freeze disagrees with old B.
  if (q || !existing || existing !== variant) {
    res.cookies.set(AB_COOKIE, variant, {
      path: "/",
      maxAge: 60 * 60 * 24 * 90,
      sameSite: "lax",
    });
  }
  return res;
}

export const config = {
  matcher: ["/us", "/au", "/us/:path*", "/au/:path*"],
};
