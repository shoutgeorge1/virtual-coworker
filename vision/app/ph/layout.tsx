import MarketGtm from "../components/MarketGtm";

export default function PhLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <MarketGtm surface="ph" />
      {children}
    </>
  );
}
