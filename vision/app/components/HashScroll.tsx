"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

/**
 * Next.js App Router often lands on `/path#gate` without scrolling to the target
 * (or restores a mid-page scroll). Scroll + lightly focus hash / `?focus=` anchors.
 */
function resolveAnchorId(): string | null {
  const hash = window.location.hash.replace(/^#/, "");
  if (hash) return decodeURIComponent(hash);
  const focus = new URLSearchParams(window.location.search).get("focus");
  return focus ? decodeURIComponent(focus) : null;
}

function scrollToAnchor(
  id: string,
  behavior: ScrollBehavior = "smooth"
): boolean {
  const el = document.getElementById(id);
  if (!el) return false;
  el.scrollIntoView({ behavior, block: "start" });
  if (el instanceof HTMLElement) {
    if (!el.hasAttribute("tabindex")) el.setAttribute("tabindex", "-1");
    try {
      el.focus({ preventScroll: true });
    } catch {
      /* older browsers */
    }
  }
  return true;
}

export default function HashScroll() {
  const pathname = usePathname();

  useEffect(() => {
    let cancelled = false;

    const run = (behavior: ScrollBehavior = "auto") => {
      if (cancelled) return;
      const id = resolveAnchorId();
      if (!id) return;
      scrollToAnchor(id, behavior);
    };

    // Next may scroll-restore after first paint — retry past that window.
    const delays = [0, 50, 150, 350, 700, 1200];
    const timers = delays.map((ms) =>
      window.setTimeout(() => run("auto"), ms)
    );

    const onHashChange = () => run("smooth");
    window.addEventListener("hashchange", onHashChange);

    // Same-path Next <Link href="#gate"> / `/us#gate` may not fire hashchange.
    const onClick = (e: MouseEvent) => {
      const target = e.target;
      if (!(target instanceof Element)) return;
      const a = target.closest("a");
      if (!(a instanceof HTMLAnchorElement) || !a.href) return;
      let url: URL;
      try {
        url = new URL(a.href, window.location.href);
      } catch {
        return;
      }
      if (url.origin !== window.location.origin) return;
      const id = url.hash.replace(/^#/, "");
      if (!id) return;
      const samePath = url.pathname === window.location.pathname;
      window.setTimeout(
        () => {
          if (cancelled) return;
          if (samePath || window.location.pathname === url.pathname) {
            scrollToAnchor(decodeURIComponent(id), "smooth");
          }
        },
        samePath ? 0 : 100
      );
    };
    document.addEventListener("click", onClick);

    return () => {
      cancelled = true;
      timers.forEach((t) => window.clearTimeout(t));
      window.removeEventListener("hashchange", onHashChange);
      document.removeEventListener("click", onClick);
    };
  }, [pathname]);

  return null;
}
