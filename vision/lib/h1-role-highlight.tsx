import type { ReactNode } from "react";

/**
 * Role phrases to tint in employer H1s (longest-first so "virtual assistants"
 * wins over "virtual assistant"). Keep plain strings — public-copy lint reads
 * config, not this markup.
 */
const ROLE_PHRASES = [
  "Filipino virtual assistant",
  "Filipino marketing support",
  "Filipino accounting support",
  "Filipino recruiting support",
  "Filipino sales support",
  "Filipino HR support",
  "Filipino social teammate",
  "Filipino bookkeeper",
  "Filipino marketer",
  "Filipino support",
  "Filipino teammate",
  "Filipino talent",
  "Filipino hire",
  "customer service capacity",
  "social media capacity",
  "bookkeeping capacity",
  "accounting capacity",
  "recruitment capacity",
  "sales-support seat",
  "marketing seat",
  "virtual assistants",
  "virtual assistant",
  "customer support",
  "recruiting support",
  "sales support",
  "social support",
  "books support",
  "HR capacity",
  "HR support",
] as const;

/** Wrap the first matching role phrase in `<span class="h1-role">` for AU/US hero tint. */
export function highlightH1Role(text: string): ReactNode {
  const lower = text.toLowerCase();
  for (const phrase of ROLE_PHRASES) {
    const idx = lower.indexOf(phrase.toLowerCase());
    if (idx < 0) continue;
    const matched = text.slice(idx, idx + phrase.length);
    return (
      <>
        {text.slice(0, idx)}
        <span className="h1-role">{matched}</span>
        {text.slice(idx + phrase.length)}
      </>
    );
  }
  return text;
}

/** Test helper — which phrase would highlight, or null. */
export function findH1RolePhrase(text: string): string | null {
  const lower = text.toLowerCase();
  for (const phrase of ROLE_PHRASES) {
    if (lower.includes(phrase.toLowerCase())) return phrase;
  }
  return null;
}
