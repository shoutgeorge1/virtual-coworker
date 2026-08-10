import type { GoogleBusinessProof } from "../../config/site";

/** Google Maps-style gold stars. Highlight the rating, not a yellow chip box. */
export function RatingStars({ size = 15 }: { size?: number }) {
  return (
    <span className="rating-stars" aria-hidden="true">
      {Array.from({ length: 5 }, (_, i) => (
        <svg key={i} viewBox="0 0 24 24" width={size} height={size} focusable="false">
          <path
            fill="#fbbc04"
            d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"
          />
        </svg>
      ))}
    </span>
  );
}

/** Gold stars + numeric rating. Static badge — no outbound link. */
export default function GoogleReviewBadge({
  proof,
  variant = "chip",
}: {
  proof: GoogleBusinessProof;
  variant?: "chip" | "pill";
}) {
  const label = `Google ${proof.rating} out of 5 from ${proof.reviewCount} reviews`;
  if (variant === "pill") {
    return (
      <span className="trust-rating-pill" aria-label={label}>
        <RatingStars size={14} />
        <b>
          {proof.rating}
          <i>/5</i>
        </b>
        <span>
          Google · {proof.reviewCount} reviews
        </span>
      </span>
    );
  }
  return (
    <span className="trust-chip" aria-label={label}>
      <RatingStars />
      <span>
        <b>{proof.rating}</b>
        <span>
          Google · {proof.reviewCount} reviews
        </span>
      </span>
    </span>
  );
}
