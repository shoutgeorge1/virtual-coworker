import { TRUST_PROOF } from "../../config/site";

/**
 * LinkedIn + Facebook follower chips — additive social proof near the form.
 * Numbers come only from TRUST_PROOF.socialReach (verified / CEO-approved).
 * Display-only: no outbound links (paid traffic stays on-host).
 */
export default function SocialReachBadges() {
  const s = TRUST_PROOF.socialReach;
  return (
    <>
      <span
        className="trust-chip trust-chip-social trust-chip-social-lead"
        aria-label={`LinkedIn ${s.linkedinDisplay} followers`}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/brand/trust/dir-linkedin.svg" alt="" />
        <span>
          <b className="trust-chip-social-count">{s.linkedinDisplay}</b>
          <span className="trust-chip-meta">LinkedIn followers</span>
        </span>
      </span>
      <span
        className="trust-chip trust-chip-social trust-chip-social-lead"
        aria-label={`Facebook ${s.facebookDisplay} followers`}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/brand/trust/dir-facebook.svg" alt="" />
        <span>
          <b className="trust-chip-social-count">{s.facebookDisplay}</b>
          <span className="trust-chip-meta">Facebook followers</span>
        </span>
      </span>
    </>
  );
}
