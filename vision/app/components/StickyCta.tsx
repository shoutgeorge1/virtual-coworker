/* Mobile-only conversion bar. On a paid click the phone and the form are the
   only two things that matter, so both stay in reach without scrolling. */
export default function StickyCta({
  href,
  label,
  phoneDisplay,
  phoneHref,
}: {
  href: string;
  label: string;
  phoneDisplay?: string;
  phoneHref?: string;
}) {
  return (
    <div className="sticky-cta">
      {phoneHref ? (
        <a className="sticky-cta-call" href={phoneHref}>
          <span aria-hidden>☎</span>
          <b>{phoneDisplay}</b>
        </a>
      ) : null}
      <a className="sticky-cta-go" href={href}>
        {label}
      </a>
    </div>
  );
}
