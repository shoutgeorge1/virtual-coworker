import MarketGtm from "../components/MarketGtm";

export default function AuLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <MarketGtm surface="au" />
      {children}
    </>
  );
}
