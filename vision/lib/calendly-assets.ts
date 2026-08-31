/**
 * Shared Calendly widget.js / widget.css loader.
 * Ensures the script is injected at most once per page.
 */

const WIDGET_JS = "https://assets.calendly.com/assets/external/widget.js";
const WIDGET_CSS = "https://assets.calendly.com/assets/external/widget.css";

declare global {
  interface Window {
    Calendly?: {
      initPopupWidget: (opts: { url: string }) => void;
      initInlineWidget: (opts: {
        url: string;
        parentElement: HTMLElement;
      }) => void;
      preload: (url: string) => void;
    };
  }
}

export function calendlyAssetsReady(): boolean {
  if (typeof window === "undefined") return false;
  return Boolean(window.Calendly?.initInlineWidget);
}

/** Load Calendly CSS + JS once. Resolves when initInlineWidget is available. */
export function loadCalendlyAssets(): Promise<void> {
  if (typeof window === "undefined") return Promise.resolve();
  if (calendlyAssetsReady()) return Promise.resolve();

  if (!document.querySelector(`link[href="${WIDGET_CSS}"]`)) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = WIDGET_CSS;
    document.head.appendChild(link);
  }

  const existing = document.querySelector(
    `script[src="${WIDGET_JS}"]`,
  ) as HTMLScriptElement | null;
  if (existing) {
    return new Promise((resolve, reject) => {
      if (calendlyAssetsReady()) {
        resolve();
        return;
      }
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener(
        "error",
        () => reject(new Error("Calendly script failed")),
        { once: true },
      );
    });
  }

  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = WIDGET_JS;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Calendly script failed"));
    document.body.appendChild(script);
  });
}

/** Poll briefly until Calendly.initInlineWidget exists. */
export function waitForInlineWidget(timeoutMs = 2500): Promise<boolean> {
  if (typeof window === "undefined") return Promise.resolve(false);
  if (calendlyAssetsReady()) return Promise.resolve(true);
  return new Promise((resolve) => {
    const start = Date.now();
    const tick = () => {
      if (calendlyAssetsReady()) {
        resolve(true);
        return;
      }
      if (Date.now() - start >= timeoutMs) {
        resolve(false);
        return;
      }
      window.setTimeout(tick, 50);
    };
    tick();
  });
}
