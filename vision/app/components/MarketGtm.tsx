import Script from "next/script";
import { resolveGtmId, type TrackingSurface } from "../../lib/market-tracking";
import MarketIdentity from "./MarketIdentity";

/** Loads the GTM container for one micro-site only (if configured). */
export default function MarketGtm({ surface }: { surface: TrackingSurface }) {
  const gtmId = resolveGtmId(surface);

  return (
    <>
      <MarketIdentity surface={surface} />
      {gtmId ? (
        <>
          <Script id={`gtm-init-${surface}`} strategy="afterInteractive">{`
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
              'gtm.start': new Date().getTime(),
              event: 'gtm.js',
              market: ${JSON.stringify(surface)},
              site_surface: ${JSON.stringify(surface)}
            });
          `}</Script>
          <Script
            id={`gtm-${surface}`}
            strategy="afterInteractive"
            src={`https://www.googletagmanager.com/gtm.js?id=${encodeURIComponent(gtmId)}`}
          />
        </>
      ) : null}
    </>
  );
}
