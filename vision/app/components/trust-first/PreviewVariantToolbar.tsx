"use client";

/**
 * Preview review chrome. Never import this from a production /us page.
 * Also refuses to render outside /preview/trust-first.
 */

import { usePathname, useSearchParams } from "next/navigation";
import { TRUST_FIRST_NAMESPACE } from "../../../config/trust-first";
import { variantHref } from "../../../lib/trust-first";

export default function PreviewVariantToolbar() {
  const pathname = usePathname() || "";
  const search = useSearchParams();
  if (!pathname.startsWith(TRUST_FIRST_NAMESPACE)) return null;

  const current = search.get("v") === "proof" ? "proof_heavy" : "simple";
  const simpleHref = variantHref(pathname, "simple");
  const proofHref = variantHref(pathname, "proof_heavy");
  const onIndex = pathname === TRUST_FIRST_NAMESPACE;

  return (
    <div className="tf-toolbar" role="navigation" aria-label="Preview variant toolbar">
      <span>PREVIEW ONLY — NOTHING LAUNCHED</span>
      <span>
        <a className={onIndex ? "is-on" : ""} href={TRUST_FIRST_NAMESPACE}>
          Index
        </a>
        {!onIndex ? (
          <>
            {" "}
            <a className={current === "simple" ? "is-on" : ""} href={simpleHref}>
              Simple
            </a>{" "}
            <a className={current === "proof_heavy" ? "is-on" : ""} href={proofHref}>
              Proof-heavy
            </a>
          </>
        ) : null}
      </span>
    </div>
  );
}
