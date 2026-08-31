import MarketGtm from "../../../components/MarketGtm";

export default function CapacityAuLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <MarketGtm surface="au" />
      {children}
    </>
  );
}
