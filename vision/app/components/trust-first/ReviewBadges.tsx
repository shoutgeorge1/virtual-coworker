import { REVIEW_BADGES } from "../../../config/trust-first";

export default function ReviewBadges() {
  const google = REVIEW_BADGES.google;
  const clutch = REVIEW_BADGES.clutch;
  return (
    <section className="tf-section">
      <div className="tf-wrap">
        <p className="tf-section-kicker">Public reviews</p>
        <h2>Rated where employers already look</h2>
        <div className="tf-reviews">
          <article className="tf-review tf-review-lead">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={google.src} alt={google.alt} />
            <div>
              <p className="tf-review-score">
                <b>{google.rating}</b>
                <span className="tf-stars" aria-hidden="true">
                  ★★★★★
                </span>
              </p>
              <p>
                {google.reviewCount} Google reviews
                <span> · {google.caption}</span>
              </p>
            </div>
          </article>
          <article className="tf-review">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={clutch.src} alt={clutch.alt} />
            <div>
              <p className="tf-review-score">
                <b>{clutch.rating}</b>
                <span className="tf-stars tf-stars-clutch" aria-hidden="true">
                  ★★★★★
                </span>
              </p>
              <p>{clutch.caption}</p>
            </div>
          </article>
        </div>
      </div>
    </section>
  );
}
