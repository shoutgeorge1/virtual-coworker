import type { MarketId } from "../../config/markets";
import type { ReactNode } from "react";

/** Crisp Hub Map B — shared by Services + How it works so framing stays identical. */
const HUB_MAP_SRC = "/brand/hero-hub-map-b.jpg?v=3";

type Props = {
  market: MarketId;
  children: ReactNode;
};

export default function HubMapHero({ market, children }: Props) {
  return (
    <header className={`micro-hero micro-hero--map micro-hero--${market}`}>
      <div className="micro-hero-map" aria-hidden>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={HUB_MAP_SRC}
          alt=""
          width={3072}
          height={2048}
          decoding="async"
          fetchPriority="high"
        />
      </div>
      <div className="micro-hero-veil" aria-hidden />
      <div className="micro-hero-copy">{children}</div>
    </header>
  );
}
