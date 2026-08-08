/**
 * Lightweight site A/B (living iteration — not one-and-done death).
 * Sticky localStorage assignment + dataLayer events for GTM/GA4 later.
 * No stats backend — George reviews winners weekly from Tag Assistant / GA4.
 *
 * Events: experiment_view · experiment_click · experiment_convert
 * Doc: vision/docs/SITE-EXPERIMENTS.md
 *
 * Force a variant (sticky): ?vc_exp=lp_density&vc_var=b
 * Applied before first paint via inline script in app/layout.tsx.
 */

import { trackEvent } from "./tracking";

export type ExpVariant = "a" | "b" | "c";

export type ExperimentDef = {
  id: string;
  /** Human label for Launch Control / weekly review */
  label: string;
  variants: readonly ExpVariant[];
  /** Where it shows */
  surface: string;
};

/** Active site experiments — keep in sync with SITE-EXPERIMENTS.md + xray stub */
export const EXPERIMENTS = {
  exit_popup: {
    id: "exit_popup",
    label: "Exit / timed popup copy",
    variants: ["a", "b", "c"] as const,
    surface: "employer LP popup",
  },
  quiz_copy: {
    id: "quiz_copy",
    label: "Quiz teaser + reward framing",
    variants: ["a", "b", "c"] as const,
    surface: "hero teaser + role quiz",
  },
  chat_launcher: {
    id: "chat_launcher",
    label: "Chat launcher label",
    variants: ["a", "b"] as const,
    surface: "engage chat launcher",
  },
  gate_headline: {
    id: "gate_headline",
    label: "Form gate headline",
    variants: ["a", "b"] as const,
    surface: "LeadGate card title",
  },
  lp_density: {
    id: "lp_density",
    label: "Landing density — wordy (a) vs lean (b)",
    variants: ["a", "b"] as const,
    surface: "market landing page body",
  },
  role_imagery: {
    id: "role_imagery",
    label: "Role / trust imagery — set A (defaults) vs set B",
    variants: ["a", "b"] as const,
    surface: "services page + market LPs + late trust",
  },
} as const satisfies Record<string, ExperimentDef>;

/** Readable aliases for the density test — `a` is the current wordy page. */
export type LpDensity = "wordy" | "lean";

export function densityFromVariant(v: ExpVariant): LpDensity {
  return v === "b" ? "lean" : "wordy";
}

export type ExperimentId = keyof typeof EXPERIMENTS;

const STORAGE_PREFIX = "vc_exp_";
const VIEWED_PREFIX = "vc_exp_viewed_";

/** Query params that force a sticky assignment (Site tests preview links). */
export const FORCE_EXP_PARAM = "vc_exp";
export const FORCE_VAR_PARAM = "vc_var";

function storageKey(id: string): string {
  return `${STORAGE_PREFIX}${id}`;
}

function normalizeVariant(
  raw: string | null | undefined,
  allowed: readonly ExpVariant[],
): ExpVariant | null {
  if (!raw) return null;
  const v = raw.trim().toLowerCase() as ExpVariant;
  return allowed.includes(v) ? v : null;
}

function persistVariant(id: string, variant: ExpVariant): void {
  try {
    localStorage.setItem(storageKey(id), variant);
    document.cookie = `${storageKey(id)}=${variant};path=/;max-age=${60 * 60 * 24 * 90};samesite=lax`;
  } catch {
    /* ignore */
  }
}

/**
 * Read ?vc_exp=&vc_var= and stick the assignment when both are valid.
 * Safe to call from assignExperiment (client) and mirrored in layout head script.
 */
export function applyUrlForceVariant(
  search: string | null | undefined = typeof window !== "undefined"
    ? window.location.search
    : "",
): { id: ExperimentId; variant: ExpVariant } | null {
  if (!search) return null;
  const q = search.startsWith("?") ? search.slice(1) : search;
  const params = new URLSearchParams(q);
  const rawId = (params.get(FORCE_EXP_PARAM) || "").trim();
  const rawVar = (params.get(FORCE_VAR_PARAM) || "").trim().toLowerCase();
  if (!rawId || !(rawId in EXPERIMENTS)) return null;
  const id = rawId as ExperimentId;
  const allowed = EXPERIMENTS[id].variants as readonly ExpVariant[];
  const variant = normalizeVariant(rawVar, allowed);
  if (!variant) return null;
  if (typeof window !== "undefined") {
    persistVariant(id, variant);
    // Allow a fresh experiment_view for this forced arm in this session.
    try {
      sessionStorage.removeItem(`${VIEWED_PREFIX}${id}`);
    } catch {
      /* ignore */
    }
    if (id === "lp_density") {
      try {
        document.documentElement.dataset.lpDensity = densityFromVariant(variant);
      } catch {
        /* ignore */
      }
    }
  }
  return { id, variant };
}

/** Build a shareable URL that forces one experiment arm (sticky on load). */
export function buildForceVariantUrl(
  baseUrl: string,
  id: ExperimentId,
  variant: ExpVariant,
): string {
  const u = new URL(baseUrl);
  u.searchParams.set(FORCE_EXP_PARAM, id);
  u.searchParams.set(FORCE_VAR_PARAM, variant);
  return u.toString();
}

/** Sticky assign — same visitor keeps the same letter until storage cleared. */
export function assignExperiment(id: ExperimentId): ExpVariant {
  const def = EXPERIMENTS[id];
  const allowed = def.variants as readonly ExpVariant[];
  if (typeof window === "undefined") return allowed[0];

  // URL override wins (and sticks) before random / stored assignment.
  const forced = applyUrlForceVariant();
  if (forced && forced.id === id) return forced.variant;

  try {
    const stored = normalizeVariant(localStorage.getItem(storageKey(id)), allowed);
    if (stored) return stored;
  } catch {
    /* ignore */
  }

  const picked = allowed[Math.floor(Math.random() * allowed.length)];
  persistVariant(id, picked);
  return picked;
}

/** All sticky assignments currently on this browser (for convert fan-out). */
export function getActiveAssignments(): Partial<Record<ExperimentId, ExpVariant>> {
  const out: Partial<Record<ExperimentId, ExpVariant>> = {};
  if (typeof window === "undefined") return out;
  for (const id of Object.keys(EXPERIMENTS) as ExperimentId[]) {
    const allowed = EXPERIMENTS[id].variants as readonly ExpVariant[];
    try {
      const v = normalizeVariant(localStorage.getItem(storageKey(id)), allowed);
      if (v) out[id] = v;
    } catch {
      /* ignore */
    }
  }
  return out;
}

export function trackExperimentView(
  id: ExperimentId,
  variant: ExpVariant,
  extra: Record<string, string | number | boolean | undefined> = {},
): void {
  if (typeof window === "undefined") return;
  // Once per session per experiment — avoid spam on remount.
  try {
    const key = `${VIEWED_PREFIX}${id}`;
    if (sessionStorage.getItem(key) === variant) return;
    sessionStorage.setItem(key, variant);
  } catch {
    /* ignore */
  }
  trackEvent("experiment_view", {
    experiment_id: id,
    experiment_variant: variant,
    ...extra,
  });
}

export function trackExperimentClick(
  id: ExperimentId,
  variant: ExpVariant,
  extra: Record<string, string | number | boolean | undefined> = {},
): void {
  trackEvent("experiment_click", {
    experiment_id: id,
    experiment_variant: variant,
    ...extra,
  });
}

/**
 * Fan-out convert for every experiment this browser was assigned.
 * Call on durable form success and phone CTA clicks.
 */
export function trackExperimentConvert(
  reason: "form_submit" | "phone_click" | string,
  extra: Record<string, string | number | boolean | undefined> = {},
): void {
  const assignments = getActiveAssignments();
  const ids = Object.keys(assignments) as ExperimentId[];
  if (!ids.length) return;
  for (const id of ids) {
    trackEvent("experiment_convert", {
      experiment_id: id,
      experiment_variant: assignments[id],
      convert_reason: reason,
      ...extra,
    });
  }
}

/**
 * Inline head snippet — keep in sync with applyUrlForceVariant / lp_density paint.
 * Applied in app/layout.tsx before first paint so forced arms never flash.
 */
export const EXPERIMENTS_BOOT_SCRIPT = [
  'document.documentElement.classList.add("js");',
  "try{",
  'var q=location.search||"";',
  'var m=q.match(/[?&]vc_exp=([^&]*)/);',
  'var n=q.match(/[?&]vc_var=([^&]*)/);',
  "if(m&&n){",
  "var eid=decodeURIComponent(m[1]).trim();",
  'var ev=decodeURIComponent(n[1]).trim().toLowerCase();',
  'var ok={exit_popup:"abc",quiz_copy:"abc",chat_launcher:"ab",gate_headline:"ab",lp_density:"ab",role_imagery:"ab"};',
  "if(ok[eid]&&ok[eid].indexOf(ev)>=0){",
  'localStorage.setItem("vc_exp_"+eid,ev);',
  'document.cookie="vc_exp_"+eid+"="+ev+";path=/;max-age=7776000;samesite=lax";',
  'try{sessionStorage.removeItem("vc_exp_viewed_"+eid)}catch(e){}',
  "}",
  "}",
  'var v=localStorage.getItem("vc_exp_lp_density");',
  'if(v==="a"||v==="b"){document.documentElement.dataset.lpDensity=v==="b"?"lean":"wordy"}',
  "}catch(e){}",
].join("");
