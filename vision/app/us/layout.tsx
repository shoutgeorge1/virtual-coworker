import MarketGtm from "../components/MarketGtm";

export default function UsLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <MarketGtm surface="us" />
      {children}
    </>
  );
}
