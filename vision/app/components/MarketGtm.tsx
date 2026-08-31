import Script from "next/script";
import {
  resolveGa4Id,
  resolveGtmId,
  type TrackingSurface,
} from "../../lib/market-tracking";
import MarketIdentity from "./MarketIdentity";

/**
 * Loads the GTM container for one micro-site only (if configured).
 * Also installs a GA4 collect beacon for experiment_* (GTM alone was only
 * forwarding page_view; gtag('event') is swallowed when GTM owns the same ID).
 */
export default function MarketGtm({ surface }: { surface: TrackingSurface }) {
  const gtmId = resolveGtmId(surface);
  const ga4Id = resolveGa4Id(surface);

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
      {ga4Id ? (
        <Script id={`ga4-exp-bridge-${surface}`} strategy="afterInteractive">{`
          (function(){
            var tid = ${JSON.stringify(ga4Id)};
            window.__vcGa4MeasurementId = tid;
            function cid(){
              try{
                var m = document.cookie.match(/(?:^|; )_ga=([^;]+)/);
                if(m){
                  var p = decodeURIComponent(m[1]).split('.');
                  if(p.length >= 4) return p[2] + '.' + p[3];
                }
              }catch(e){}
              try{
                var k = 'vc_ga_cid';
                var existing = localStorage.getItem(k);
                if(existing) return existing;
                var fresh = String(Math.floor(Math.random()*1e10)) + '.' + String(Math.floor(Date.now()/1000));
                localStorage.setItem(k, fresh);
                return fresh;
              }catch(e2){
                return '555.555';
              }
            }
            window.__vcSendExpGa4 = function(name, params){
              if(!name || String(name).indexOf('experiment_') !== 0) return;
              try{
                var qs = new URLSearchParams();
                qs.set('v','2');
                qs.set('tid', tid);
                qs.set('cid', cid());
                qs.set('en', name);
                qs.set('_z','vc_exp');
                var p = params || {};
                Object.keys(p).forEach(function(key){
                  var val = p[key];
                  if(val === undefined || val === null) return;
                  if(typeof val === 'number' && isFinite(val)) qs.set('epn.'+key, String(val));
                  else qs.set('ep.'+key, String(val));
                });
                var url = 'https://www.google-analytics.com/g/collect?' + qs.toString();
                if(navigator.sendBeacon) navigator.sendBeacon(url);
                else {
                  var img = new Image();
                  img.src = url;
                }
              }catch(err){}
            };
            var q = window.__vcExpGa4Queue || [];
            window.__vcExpGa4Queue = [];
            for(var i=0;i<q.length;i++){
              window.__vcSendExpGa4(q[i][0], q[i][1] || {});
            }
          })();
        `}</Script>
      ) : null}
    </>
  );
}
